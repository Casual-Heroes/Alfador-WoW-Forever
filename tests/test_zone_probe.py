# Isolated Lua source checks, never actual in-game acceptance.
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.builddeps'))
from lupa.lua51 import LuaRuntime as Lua51
from lupa.lua54 import LuaRuntime as Lua54
MOCK = (ROOT / 'tests/zone_probe_mock.lua').read_text(encoding='utf-8')
sys.path.insert(0, str(ROOT / 'tools'))
from zone_probe_validate import validate, decode_saved_hex
from observation_import import InvalidObservation
SOURCE = ROOT / 'probes/Alfador-wow-Zone-Test/ZoneTest.lua'

class ZoneChecks:
    runtime = None
    def setUp(self):
        self.lua = self.runtime(unpack_returned_tuples=True, register_eval=False, register_builtins=False)
        self.lua.execute(MOCK)
        self.lua.execute('''
            function IsLoggedIn() return true end
            function UnitExists(unit) assert(unit == 'player'); return true end
            function UnitGUID() error('GUID read forbidden in probe') end
            function UnitName() error('Name read forbidden in probe') end
        ''')
        self.lua.execute(SOURCE.read_text())
    def event(self, name):
        self.lua.execute('objects.AlfadorWowZoneTestSampler:OnEvent(' + json.dumps(name) + ')')
    def tick(self, seconds=1):
        self.lua.execute('objects.AlfadorWowZoneTestSampler:OnUpdate(' + str(seconds) + ')')
    def read(self):
        self.lua.execute("SlashCmdList.ALFADORZONETEST('')")
        raw = self.lua.globals().exported.encode('utf-8')
        doc, _ = validate(raw)
        return doc
    def latest(self): return self.read()['samples'][-1]
    def enter(self):
        self.event('PLAYER_ENTERING_WORLD'); self.tick()
        return self.latest()
    def test_startup_does_not_infer_world_from_logged_in(self):
        self.assertEqual(self.latest()['state'], 'unavailable'); self.tick()
        self.assertEqual(self.latest()['reason'], 'startup-awaiting-world-event')
    def test_in_world_reads_exact_build_map_name_level(self):
        row = self.enter()
        self.assertEqual(row['state'], 'in_world')
        self.assertEqual(row['observedClient']['build']['value'], '70959')
        self.assertEqual(row['fields']['mapId']['value'], 10)
        self.assertEqual(row['fields']['zoneName']['value'], 'Synthetic zone')
        self.assertTrue(row['fields']['inWorld']['value'])
        self.assertEqual(row['transport'], 'local-copy-only-not-live-desktop')
    def test_zone_transition_invalidates_before_fresh_read(self):
        self.enter(); self.event('ZONE_CHANGED_NEW_AREA'); old = self.latest()
        self.assertEqual(old['state'], 'unavailable')
        self.assertEqual(old['fields']['mapId'], {'status': 'unavailable'})
        self.lua.execute("C_Map.GetBestMapForUnit=function() return 20 end; GetZoneText=function() return 'New synthetic zone' end")
        self.tick(); self.assertEqual(self.latest()['fields']['mapId']['value'], 20)
    def test_leaving_logout_and_absent_player_do_not_reuse_zone(self):
        for event in ['PLAYER_LEAVING_WORLD', 'PLAYER_LOGOUT']:
            self.enter(); self.event(event); self.tick()
            self.assertEqual(self.latest()['state'], 'unavailable')
            self.assertEqual(self.latest()['fields']['zoneName'], {'status': 'unavailable'})
        self.lua.execute('function UnitExists() return false end')
        self.assertEqual(self.enter()['reason'], 'player-unavailable')
    def test_enter_changes_boundary_with_increasing_sequence(self):
        first = self.enter(); second = self.enter()
        self.assertNotEqual(first['boundary'], second['boundary'])
        self.assertGreater(second['sequence'], first['sequence'])
        self.assertRegex(first['boundary'], '^[a-f0-9]{32}$')
    def test_missing_failed_restricted_invalid_api_unavailable(self):
        for script in ["C_Map.GetBestMapForUnit=nil", "C_Map.GetBestMapForUnit=function() error('fail') end",
                       'C_Map.GetBestMapForUnit=function() return secret end', 'C_Map.GetBestMapForUnit=function() return 0 end']:
            self.setUp(); self.lua.execute(script); self.assertEqual(self.enter()['state'], 'unavailable')
    def test_combat_and_unknown_secret_check_suppress_facts(self):
        for script in ['function InCombatLockdown() return true end', 'issecretvalue=nil']:
            self.setUp(); self.lua.execute(script); self.assertEqual(self.enter()['state'], 'unavailable')
    def test_mismatched_build_reported_but_not_accepted(self):
        self.lua.execute("GetBuildInfo=function() return '1.60.1','99999','',16001 end"); row = self.enter()
        self.assertEqual(row['state'], 'unavailable'); self.assertEqual(row['observedClient']['build']['value'], '99999')
    def test_mid_sample_map_change_discards_cohort(self):
        self.lua.execute('local n=0; C_Map.GetBestMapForUnit=function() n=n+1; return n end')
        self.assertEqual(self.enter()['state'], 'unavailable')
    def test_timestamp_regression_or_unavailable_discards(self):
        self.lua.execute('local n=1795000000; GetServerTime=function() n=n-1; return n end')
        self.assertEqual(self.enter()['state'], 'unavailable')
        self.setUp(); self.lua.execute('GetServerTime=nil')
        self.assertEqual(self.enter()['capturedAtUnix'], {'status': 'unavailable'})
    def test_rate_bound_and_ring_retention(self):
        self.enter(); first = self.latest()['sequence']; self.tick(.5)
        self.assertEqual(self.latest()['sequence'], first); self.tick(.5)
        self.assertEqual(self.latest()['sequence'], first + 1)
        for _ in range(30): self.tick()
        rows = self.read()['samples']; self.assertEqual(len(rows), 12)
        self.assertTrue(all(a['sequence'] < b['sequence'] for a,b in zip(rows, rows[1:])))
    def test_copy_frozen_saved_text_decodes_current_samples(self):
        self.enter(); before = self.read(); self.tick()
        self.assertEqual(json.loads(self.lua.globals().exported), before)
        self.assertEqual(json.loads(bytes.fromhex(self.lua.globals().AlfadorZoneTestEvidence)), self.read())
    def test_saved_logout_has_terminal_unavailable(self):
        self.enter(); self.event('PLAYER_LOGOUT')
        saved = json.loads(bytes.fromhex(self.lua.globals().AlfadorZoneTestEvidence))
        self.assertEqual(saved['samples'][-1]['reason'], 'logout')
        self.assertEqual(saved['samples'][-1]['state'], 'unavailable')
    def test_level_optional_and_no_position_invented(self):
        self.lua.execute('UnitLevel=nil'); row = self.enter()
        self.assertEqual(row['state'], 'in_world')
        self.assertEqual(row['fields']['level'], {'status': 'unavailable'})
        self.assertNotIn('position', row['fields'])
    def test_player_loss_requires_new_world_boundary(self):
        self.enter(); self.lua.execute('UnitExists=function() return false end'); self.tick()
        unavailable = self.latest()
        self.lua.execute('UnitExists=function() return true end'); self.tick()
        self.assertEqual(self.latest()['sequence'], unavailable['sequence'])
        fresh = self.enter()
        self.assertNotEqual(fresh['boundary'], unavailable['boundary'])
        self.assertEqual(fresh['state'], 'in_world')
    def test_new_lua_runtime_starts_unavailable_and_resets_sequence(self):
        self.enter(); self.tick(); self.setUp()
        row = self.latest()
        self.assertEqual(row['sequence'], 1)
        self.assertEqual(row['state'], 'unavailable')
    def test_saved_decoder_rejects_extra_executable_lua(self):
        self.enter(); value = self.lua.globals().AlfadorZoneTestEvidence
        raw = ('AlfadorZoneTestEvidence = "' + value + '"').encode()
        self.assertEqual(validate(decode_saved_hex(raw))[1]['freshness'], 'historical')
        for bad in [raw + b'; os.execute("bad")', b'dofile("bad")', b'AlfadorZoneTestEvidence = "abc"',
                    b'AlfadorZoneTestEvidence = "zz"']:
            with self.assertRaises(InvalidObservation): decode_saved_hex(bad)
    def test_validator_rejects_stale_fields_unknowns_and_sequence_regression(self):
        self.enter(); doc = self.read(); doc['samples'][-1]['fields']['guid'] = 'forbidden'
        with self.assertRaises(InvalidObservation): validate(json.dumps(doc).encode())
        doc = self.read(); doc['samples'][-1]['sequence'] = 1
        with self.assertRaises(InvalidObservation): validate(json.dumps(doc).encode())
        self.event('ZONE_CHANGED'); doc = self.read()
        doc['samples'][-1]['fields']['zoneName'] = {'status':'observed','value':'stale'}
        with self.assertRaises(InvalidObservation): validate(json.dumps(doc).encode())
    def test_json_control_and_unicode_round_trip(self):
        self.lua.execute(r'''function GetZoneText() return 'quote" slash\\ newline\n Synth?tique' end''')
        self.assertEqual(self.enter()['fields']['zoneName']['value'], 'quote" slash\\ newline\n Synth?tique')

class Lua51ZoneTests(ZoneChecks, unittest.TestCase): runtime = Lua51
class Lua54ZoneTests(ZoneChecks, unittest.TestCase): runtime = Lua54
if __name__ == '__main__': unittest.main()
