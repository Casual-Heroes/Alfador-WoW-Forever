# Source-only transport experiments; no native game or physical delivery acceptance.
from pathlib import Path
import sys
import re
import subprocess
import json
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.builddeps'));sys.path.insert(0,str(ROOT/'tools'))
from lupa.lua51 import LuaRuntime as Lua51
from lupa.lua54 import LuaRuntime as Lua54
from transfer_marker_tail import MarkerTail
MOCK=(ROOT/'tests/zone_probe_mock.lua').read_text()
LUA=ROOT/'probes/Alfador-wow-Transfer-Test/TransferTest.lua'

class MarkerProbeChecks:
    runtime=None
    def setUp(self):
        self.lua=self.runtime(unpack_returned_tuples=True,register_eval=False,register_builtins=False)
        self.lua.execute(MOCK)
        self.lua.execute('''
        sent={}; loggingCalls=0
        function GetBuildInfo() return '1.60.1','71037','Nov 18 2026',16001 end
        function GetTimePreciseSec() return 123.456789 end
        function IsLoggedIn() return true end
        function IsInInstance() return false, "none" end
        function UnitExists(unit) assert(unit=='player');return true end
        function UnitName(unit) assert(unit=='player');return 'SyntheticSelf' end
        function UnitGUID() error('GUID forbidden') end
        function LoggingChat() loggingCalls=loggingCalls+1;error('do not enable logging') end
        Enum={SendAddonMessageResult={Success=0}}
        C_ChatInfo={AreOutgoingAddonChatMessagesRestricted=function() return false end,
            InChatMessagingLockdown=function() return false end,
            IsLoggingChat=function() return true end,
            RegisterAddonMessagePrefix=function(p) assert(p=='AlfadorTest');return 0 end,
            IsAddonMessagePrefixRegistered=function(p) return p=='AlfadorTest' end,
            SendAddonMessageLogged=function(prefix,msg,channel,target)
                assert(prefix=='AlfadorTest' and channel=='WHISPER' and target=='SyntheticSelf')
                sent[#sent+1]=msg;return 0
            end}
        ''')
        self.lua.execute(LUA.read_text())
    def prepare(self):
        self.lua.execute("objects.AlfadorWowTransferTestSampler:OnEvent('PLAYER_ENTERING_WORLD');SlashCmdList.ALFADORTRANSFERTEST('prepare')")
    def start(self):
        self.prepare();self.lua.execute("SlashCmdList.ALFADORTRANSFERTEST('start')")
    def tick(self,n=3): self.lua.execute('objects.AlfadorWowTransferTestSampler:OnUpdate('+str(n)+')')
    def count(self): return len(self.lua.globals().sent)
    def test_previous_build_and_other_interface_still_fail_closed(self):
        for script in ["GetBuildInfo=function() return '1.60.1','70959','',16001 end",
                       "GetBuildInfo=function() return '1.60.1','71037','',16002 end"]:
            self.setUp();self.lua.execute(script);self.start();self.tick();self.assertEqual(self.count(),0)
    def test_idle_until_manual_start_and_no_auto_logging(self):
        self.tick(30);self.assertEqual(self.count(),0);self.assertEqual(self.lua.globals().loggingCalls,0)
    def test_eight_small_plaintext_self_only_markers_then_stop(self):
        self.start()
        for _ in range(20):self.tick()
        self.assertEqual(self.count(),8)
        for i in range(1,9):
            msg=self.lua.globals().sent[i]
            self.assertIn('seq='+str(i),msg);self.assertLess(len(msg),200)
            self.assertNotIn('SyntheticSelf',msg);self.assertNotIn('GUID',msg)
    def test_no_catch_up_and_no_duplicate_start(self):
        self.start();self.tick(1);self.assertEqual(self.count(),0)
        self.lua.execute("SlashCmdList.ALFADORTRANSFERTEST('start')")
        self.tick(30);self.assertEqual(self.count(),1)
    def test_restrictions_logging_off_missing_api_fail_closed(self):
        for script in ['C_ChatInfo.IsLoggingChat=function() return false end',
            'C_ChatInfo.AreOutgoingAddonChatMessagesRestricted=nil',
            'C_ChatInfo.AreOutgoingAddonChatMessagesRestricted=function() return secret end',
            'IsInInstance=function() return true end',
            'C_ChatInfo.InChatMessagingLockdown=function() return true end',
            'C_ChatInfo.SendAddonMessageLogged=nil','issecretvalue=nil',
            "GetBuildInfo=function() return '1.60.1','99999','',16001 end"]:
            self.setUp();self.lua.execute(script);self.start();self.tick();self.assertEqual(self.count(),0)
    def test_true_flag_is_reported_without_claiming_native_or_disk_success(self):
        self.lua.execute('C_ChatInfo.AreOutgoingAddonChatMessagesRestricted=function() return true end')
        self.start();self.tick()
        self.assertEqual(self.count(),1)
        ack=self.lua.globals().messages[len(self.lua.globals().messages)]
        self.assertIn('restriction_flag=true',ack)
        self.assertIn('native_success_only=true',ack)
        self.assertNotIn('disk_success',ack)
    def test_lockdown_stops_true_flag_candidate_and_never_resumes(self):
        self.lua.execute('C_ChatInfo.AreOutgoingAddonChatMessagesRestricted=function() return true end')
        self.start()
        self.lua.execute('C_ChatInfo.InChatMessagingLockdown=function() return true end')
        self.tick();self.assertEqual(self.count(),0)
        self.lua.execute('C_ChatInfo.InChatMessagingLockdown=function() return false end')
        self.tick();self.assertEqual(self.count(),0)
    def test_native_denial_with_true_diagnostic_stops_after_one_attempt(self):
        self.lua.execute('C_ChatInfo.AreOutgoingAddonChatMessagesRestricted=function() return true end')
        self.start()
        self.lua.execute('C_ChatInfo.SendAddonMessageLogged=function() sent[#sent+1]="attempt";return 1 end')
        self.tick();self.tick();self.assertEqual(self.count(),1)
    def test_diagnostic_unavailable_or_instance_transition_cancels_active_run(self):
        for script in ['C_ChatInfo.AreOutgoingAddonChatMessagesRestricted=nil',
                       'IsInInstance=function() return true end',
                       'IsInInstance=nil']:
            self.setUp();self.start();self.lua.execute(script);self.tick()
            self.assertEqual(self.count(),0)

    def test_combat_world_exit_and_target_change_stop_without_resume(self):
        for script in ['InCombatLockdown=function() return true end',
            "objects.AlfadorWowTransferTestSampler:OnEvent('PLAYER_LEAVING_WORLD')",
            "UnitName=function() return 'DifferentSynthetic' end"]:
            self.setUp();self.start();self.lua.execute(script);self.tick();self.assertEqual(self.count(),0)
    def test_stop_unknown_commands_and_unregistered_prefix_never_send(self):
        self.start();self.lua.execute("SlashCmdList.ALFADORTRANSFERTEST('stop')");self.tick();self.assertEqual(self.count(),0)
        self.lua.execute("SlashCmdList.ALFADORTRANSFERTEST('https://bad.invalid')");self.tick();self.assertEqual(self.count(),0)
        self.setUp();self.lua.execute('C_ChatInfo.IsAddonMessagePrefixRegistered=function() return false end')
        self.start();self.tick();self.assertEqual(self.count(),0)
    def test_send_failure_no_retry(self):
        self.start();self.lua.execute('C_ChatInfo.SendAddonMessageLogged=function() sent[#sent+1]="attempt";return 1 end')
        self.tick();self.tick();self.assertEqual(self.count(),1)
    def test_clock_or_restricted_target_unavailable(self):
        for script in ['GetServerTime=function() return 0 end','UnitName=function() return secret end']:
            self.setUp();self.start();self.lua.execute(script);self.tick();self.assertEqual(self.count(),0)

    def test_matched_prepare_ready_start_preserves_all_eight_markers(self):
        self.prepare();self.tick(30);self.assertEqual(self.count(),0)
        message=self.lua.globals().messages[len(self.lua.globals().messages)]
        label=re.search('session=([a-f0-9]{32})',message).group(1)
        temp=tempfile.TemporaryDirectory(prefix='alfador-ready-flow-tests-')
        root=Path(temp.name).resolve();reader=None
        try:
            (root/'Logs').mkdir();path=root/'Logs/WoWChatLog.txt';path.write_bytes(b'old ignored line\n')
            reader=MarkerTail(root,label)
            self.assertEqual(reader.ready_event()['event'],'ready')
            self.lua.execute("SlashCmdList.ALFADORTRANSFERTEST('start')")
            observed=[]
            for i in range(1,9):
                self.tick()
                with path.open('ab') as file:file.write(self.lua.globals().sent[i].encode()+b'\n')
                observed.extend(r['sequence'] for r in reader.poll() if r['event']=='marker-observed')
            self.assertEqual(observed,list(range(1,9)))
            self.assertEqual(reader.summary()['missing_sequences'],[])
        finally:
            if reader is not None and not reader.closed:reader.close()
            assert root.name.startswith('alfador-ready-flow-tests-') and root==Path(temp.name).resolve()
            temp.cleanup()
    def test_prepare_is_idle_until_reader_ready_and_explicit_start(self):
        self.prepare();self.tick(30);self.assertEqual(self.count(),0)
        message=self.lua.globals().messages[len(self.lua.globals().messages)]
        self.assertIn('PREPARED session=',message)
        self.assertIn('zero markers sent',message)
    def test_start_without_prepare_or_after_completed_run_does_not_restart(self):
        self.lua.execute("objects.AlfadorWowTransferTestSampler:OnEvent('PLAYER_ENTERING_WORLD');SlashCmdList.ALFADORTRANSFERTEST('start')")
        self.tick();self.assertEqual(self.count(),0)
        self.start()
        for _ in range(8):self.tick()
        self.lua.execute("SlashCmdList.ALFADORTRANSFERTEST('start')");self.tick()
        self.assertEqual(self.count(),8)
    def test_start_keeps_prepared_label_and_emits_subsecond_local_ack(self):
        self.prepare()
        message=self.lua.globals().messages[len(self.lua.globals().messages)]
        label=re.search('session=([a-f0-9]{32})',message).group(1)
        self.lua.execute("SlashCmdList.ALFADORTRANSFERTEST('start')");self.tick()
        self.assertIn(label,self.lua.globals().sent[1])
        ack=self.lua.globals().messages[len(self.lua.globals().messages)]
        self.assertIn('SEND seq=1 game_before=123.456789',ack)
    def test_world_exit_or_target_change_invalidates_prepared_session(self):
        self.prepare();self.lua.execute("objects.AlfadorWowTransferTestSampler:OnEvent('PLAYER_LEAVING_WORLD');objects.AlfadorWowTransferTestSampler:OnEvent('PLAYER_ENTERING_WORLD');SlashCmdList.ALFADORTRANSFERTEST('start')")
        self.tick();self.assertEqual(self.count(),0)
        self.prepare();self.lua.execute("UnitName=function() return 'DifferentSynthetic' end;SlashCmdList.ALFADORTRANSFERTEST('start')")
        self.tick();self.assertEqual(self.count(),0)
    def test_subsecond_clock_missing_no_native_send(self):
        self.prepare();self.lua.execute("GetTimePreciseSec=nil;SlashCmdList.ALFADORTRANSFERTEST('start')")
        self.tick();self.assertEqual(self.count(),0)

class Lua51TransferTests(MarkerProbeChecks,unittest.TestCase):runtime=Lua51
class Lua54TransferTests(MarkerProbeChecks,unittest.TestCase):runtime=Lua54

class TailChecks(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='alfador-transfer-marker-tests-')
        self.root=Path(self.tmp.name).resolve();(self.root/'Logs').mkdir()
        self.path=self.root/'Logs/WoWChatLog.txt';self.path.write_bytes(b'old raw chat never exported\n')
        self.session='a'*32;self.reader=MarkerTail(self.root,self.session);self.ready=self.reader.ready_event()
    def tearDown(self):
        if not self.reader.closed:self.reader.close()
        # Cleanup only the verified task-specific disposable directory.
        assert self.root.name.startswith('alfador-transfer-marker-tests-') and self.root==Path(self.tmp.name).resolve()
        self.tmp.cleanup()
    def append(self,data):
        with self.path.open('ab') as stream:stream.write(data)
    def marker(self,seq=1,session=None):
        return ('native local header ALFADOR_XFER_V1 session='+(session or self.session)+' seq='+str(seq)+' sent=100 END\n').encode()
    def test_no_old_data_and_unrelated_chat_discarded(self):
        self.assertEqual(self.reader.poll(now=101),[])
        self.append(b'private chat ignored\n');self.assertEqual(self.reader.poll(now=101),[])
    def test_marker_receipt_contains_no_raw_names_or_paths_and_no_live_claim(self):
        self.append(self.marker());r=self.reader.poll(now=101)[0]
        self.assertEqual(r['sequence'],1);self.assertEqual(r['observed_clock_difference_seconds'],1)
        self.assertFalse(r['live_transport_verified']);self.assertFalse(r['game_attested'])
        self.assertNotIn('header',str(r));self.assertNotIn(str(self.root),str(r))
    def test_other_sessions_duplicates_and_out_of_order_ignored(self):
        self.append(self.marker(session='b'*32)+self.marker(2)+self.marker(1)+self.marker(2))
        events=self.reader.poll(now=101)
        self.assertEqual([r['sequence'] for r in events if r['event']=='marker-observed'],[2,1])
        self.assertEqual(self.reader.summary()['duplicates'],1)
        self.assertEqual(self.reader.summary()['out_of_order'],1)
        self.assertEqual(self.reader.summary()['received_sequences'],[1,2])
    def test_partial_lines_wait_for_completion(self):
        m=self.marker();self.append(m[:40]);self.assertEqual(self.reader.poll(now=101),[])
        self.append(m[40:]);self.assertEqual(len(self.reader.poll(now=101)),1)
    def test_truncation_stops_instead_of_rebinding(self):
        self.path.write_bytes(b'')
        self.assertEqual(self.reader.poll(now=101)[0]['event'],'source-replaced-or-truncated')
        self.assertTrue(self.reader.closed)
    def test_read_and_line_bounds_stop(self):
        self.append(b'x'*70000);self.assertEqual(self.reader.poll(now=101)[0]['event'],'read-budget-exceeded')
    def test_pending_long_line_stops(self):
        self.append(b'x'*4097);self.assertEqual(self.reader.poll(now=101)[0]['event'],'line-budget-exceeded')
    def test_ambiguous_lines_and_invalid_clock_rejected(self):
        self.append(self.marker().rstrip()+b' '+self.marker())
        self.assertEqual(self.reader.poll(now=101),[])
        with self.assertRaises(ValueError):self.reader.poll(now=float('inf'))
    def test_ready_precedes_first_send_and_missing_list_is_exact(self):
        self.assertEqual(self.ready['event'],'ready')
        self.assertEqual(self.ready['position'],'end-of-file-before-send')
        self.assertEqual(self.reader.poll(),[])
        self.append(self.marker(1)+self.marker(3))
        events=self.reader.poll(now=101,monotonic=self.reader.started_monotonic+2.5)
        self.assertEqual([r['sequence'] for r in events],[1,3])
        self.assertTrue(all(r['monotonic_elapsed_seconds']==2.5 for r in events))
        self.assertTrue(all(r['batch_matching_markers']==2 for r in events))
        self.assertEqual(self.reader.summary()['missing_sequences'],[2,4,5,6,7,8])
    def test_cli_ready_before_writer_preserves_first_marker_and_summary(self):
        process=subprocess.Popen([sys.executable,'-B',str(ROOT/'tools/transfer_marker_tail.py'),
            '--forever-root',str(self.root),'--session',self.session,'--seconds','1'],
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            ready=json.loads(process.stdout.readline())
            self.assertEqual(ready['event'],'ready')
            for seq in range(1,9):self.append(self.marker(seq))
            output,error=process.communicate(timeout=5)
            self.assertEqual(process.returncode,0,error)
            records=[json.loads(line) for line in output.splitlines()]
            self.assertEqual([r['sequence'] for r in records if r['event']=='marker-observed'],list(range(1,9)))
            self.assertEqual(records[-1]['missing_sequences'],[])
        finally:
            if process.poll() is None:process.kill();process.communicate()
    def test_cannot_poll_before_ready(self):
        self.reader.ready_emitted=False
        with self.assertRaisesRegex(ValueError,'reader-not-ready'):self.reader.poll()
        self.reader.ready_event();self.assertEqual(self.reader.poll(),[])
    def test_pre_ready_marker_is_not_mislabeled_as_success(self):
        self.reader.close();self.append(self.marker(1));self.reader=MarkerTail(self.root,self.session)
        self.reader.ready_event();self.append(self.marker(2))
        self.assertEqual(self.reader.poll()[0]['sequence'],2)
        self.assertIn(1,self.reader.summary()['missing_sequences'])
    def test_reader_is_shareable_with_synthetic_concurrent_writer(self):
        with self.path.open('ab') as writer:
            writer.write(self.marker(1));writer.flush()
            self.assertEqual(self.reader.poll()[0]['sequence'],1)
        if sys.platform=='win32':self.assertEqual(self.ready['native_file_share'],'read-write-delete')
    def test_monotonic_regression_rejected_before_consuming_marker(self):
        self.append(self.marker(1))
        with self.assertRaises(ValueError):self.reader.poll(monotonic=self.reader.started_monotonic-1)
        self.assertEqual(self.reader.poll()[0]['sequence'],1)

    def test_invalid_session_rejected(self):
        with self.assertRaises(ValueError):MarkerTail(self.root,'not a session')

if __name__=='__main__':unittest.main()
