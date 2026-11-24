"""Synthetic save behavior only; no native save/flush acceptance."""
from pathlib import Path
import json
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.builddeps'));sys.path.insert(0,str(ROOT/'tools'))
from lupa.lua51 import LuaRuntime as Lua51
from lupa.lua54 import LuaRuntime as Lua54
from save_test_validate import validate_saved,MAX_SAVED
from observation_import import InvalidObservation
MOCK=(ROOT/'tests/zone_probe_mock.lua').read_text()
class ProbeChecks:
    runtime=None
    def setUp(self):
        self.lua=self.runtime(unpack_returned_tuples=True,register_eval=False,register_builtins=False)
        self.lua.execute(MOCK)
        self.lua.execute("""
function GetBuildInfo() return '1.60.1','71037','',16001 end
function IsLoggedIn() return true end
function UnitExists() return true end
function UnitName() error('name forbidden') end
function UnitGUID() error('guid forbidden') end
function UnitLevel() error('level unnecessary') end
function ReloadUI() error('reload forbidden') end
function LoggingChat() error('logging forbidden') end
C_ChatInfo=nil; C_Map=nil
""")
        self.lua.execute((ROOT/'probes/Alfador-wow-Save-Test/SaveTest.lua').read_text())
    def enter(self):self.lua.execute("objects.AlfadorWowSaveTestBoundary:OnEvent('PLAYER_ENTERING_WORLD')")
    def mark(self):self.lua.execute("SlashCmdList.ALFADORSAVETEST('mark')")
    def saved(self):
        text=self.lua.globals().AlfadorWowSaveTestEvidence
        return ('AlfadorWowSaveTestEvidence = "'+text+'"\n').encode()
    def test_no_mutation_until_manual_mark(self):
        self.assertIsNone(self.lua.globals().AlfadorWowSaveTestEvidence)
        self.enter();self.assertIsNone(self.lua.globals().AlfadorWowSaveTestEvidence)
        self.lua.execute("SlashCmdList.ALFADORSAVETEST('http://example.invalid')")
        self.assertIsNone(self.lua.globals().AlfadorWowSaveTestEvidence)
    def test_marker_safe_decoder_roundtrip_and_sequence(self):
        self.enter();self.mark();a,_=validate_saved(self.saved());self.mark();b,r=validate_saved(self.saved())
        self.assertEqual((a['sequence'],b['sequence']),(1,2));self.assertEqual(a['boundary'],b['boundary'])
        self.assertEqual(b['build'],'71037');self.assertFalse(r['live_delivery_verified'])
    def test_exit_does_not_replace_last_marker_and_reentry_changes_boundary(self):
        self.enter();self.mark();old=self.saved();a,_=validate_saved(old)
        self.lua.execute("objects.AlfadorWowSaveTestBoundary:OnEvent('PLAYER_LOGOUT')")
        self.mark();self.assertEqual(self.saved(),old)
        self.enter();self.mark();b,_=validate_saved(self.saved())
        self.assertEqual(b['sequence'],1);self.assertNotEqual(a['boundary'],b['boundary'])
    def test_invalid_build_secret_and_player_guard_preserve_existing_marker(self):
        for script in ["GetBuildInfo=function() return '1.60.1','70959','',16001 end",
                       "GetBuildInfo=function() return '1.60.1','71037','',16002 end",
                       "IsLoggedIn=function() return false end","UnitExists=function() return false end",
                       "InCombatLockdown=function() return true end","issecretvalue=nil",
                       "GetServerTime=function() return secret end","GetServerTime=function() return 0/0 end"]:
            self.setUp();self.enter();self.mark();old=self.saved();self.lua.execute(script);self.mark();self.assertEqual(self.saved(),old)
    def test_not_in_world_does_not_create_marker(self):
        self.mark();self.assertIsNone(self.lua.globals().AlfadorWowSaveTestEvidence)
    def test_thousand_marker_bound(self):
        self.enter()
        for _ in range(1001):self.mark()
        doc,_=validate_saved(self.saved());self.assertEqual(doc['sequence'],1000)
class Lua51SaveProbe(ProbeChecks,unittest.TestCase):runtime=Lua51
class Lua54SaveProbe(ProbeChecks,unittest.TestCase):runtime=Lua54
class DecoderChecks(unittest.TestCase):
    def fixture(self):return dict(schema='alfador.wowf.save-test.v1',version='1.60.1',build='71037',interface=16001,boundary='a'*32,sequence=1,capturedAtUnix=1795000000,freshness='historical',payloadKind='synthetic-save-marker')
    def saved(self,doc):return b'AlfadorWowSaveTestEvidence = "'+json.dumps(doc).encode().hex().encode()+b'"\n'
    def test_forbidden_lua_and_extra_assignments_rejected(self):
        good=self.saved(self.fixture())
        for raw in [b'AlfadorWowSaveTestEvidence = os.execute("bad")',good+b'other=1',b'-- comment\n'+good,b'X = "00"',b'AlfadorWowSaveTestEvidence = "0"']:
            with self.assertRaises(InvalidObservation):validate_saved(raw)
    def test_bounds_and_invalid_encoding(self):
        for raw in [b'',b'x'*(MAX_SAVED+1),b'AlfadorWowSaveTestEvidence = "ff"']:
            with self.assertRaises(InvalidObservation):validate_saved(raw)
    def test_extra_missing_wrong_build_and_boolean_numbers_rejected(self):
        for change in [dict(extra='x'),dict(build='70959'),dict(interface=True),dict(sequence=True),dict(capturedAtUnix=True),dict(sequence=1001),dict(boundary='bad')]:
            doc=self.fixture();doc.update(change)
            with self.assertRaises(InvalidObservation):validate_saved(self.saved(doc))
        doc=self.fixture();del doc['build']
        with self.assertRaises(InvalidObservation):validate_saved(self.saved(doc))
    def test_duplicate_json_keys_rejected(self):
        text=json.dumps(self.fixture())[:-1]+',"sequence":2}'
        raw=b'AlfadorWowSaveTestEvidence = "'+text.encode().hex().encode()+b'"'
        with self.assertRaises(InvalidObservation):validate_saved(raw)
if __name__=='__main__':unittest.main()
