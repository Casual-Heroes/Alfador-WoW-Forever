import copy
import time
import unittest
from unittest.mock import patch
from test_adapter import AdapterTests
from protocol import digest
from controller import INPUT_KEYS, Worker


class WoWTests(unittest.TestCase):
    setUp=AdapterTests.setUp
    tearDown=AdapterTests.tearDown
    make_worker=AdapterTests.make_worker
    task=AdapterTests.task
    finish=AdapterTests.finish
    def test_edition_required_and_all_three_supported(self):
        for edition in ('Forever','Retail','Shared'):
            task=copy.deepcopy(self.tasks[0]);task['instructions']='Edition: '+edition+'\nReview only.'
            task['instructions_digest']=digest({k:task[k] for k in INPUT_KEYS})
            self.worker.check_task(task)
        for prefix in ('', 'Edition: FFXIV\n','edition: Forever\n','Edition: Forever and Retail\n'):
            task=copy.deepcopy(self.tasks[0]);task['instructions']=prefix+'Review only.'
            task['instructions_digest']=digest({k:task[k] for k in INPUT_KEYS})
            with self.assertRaises(ValueError):self.worker.check_task(task)

    def test_review_only_profile_cannot_expand(self):
        for action in ('implement','test','package','install','activate','restart'):
            profile=copy.deepcopy(self.profile);profile['allowed_actions']=[action]
            with self.assertRaises(ValueError):Worker(profile,self.journal,self.server,self.codex,{},self.root/'evidence')

    def test_delayed_validation_consumes_budget_from_request_start(self):
        task=self.tasks[0];wall=time.time();original=self.server.call
        def slow(*args):
            result=original(*args);result['valid_until']=int(wall)+15
            return result
        self.server.call=slow
        with patch('controller.time.time',return_value=wall), patch('controller.time.monotonic',side_effect=[100,116]):
            with self.assertRaisesRegex(RuntimeError,'monotonic'):self.worker.validate(task)

    def test_wall_clock_jump_does_not_extend_authority(self):
        wall=time.time();task=self.tasks[0]
        with patch('controller.time.time',return_value=wall), patch('controller.time.monotonic',side_effect=[100,101]):
            self.worker.validate(task)
        with patch('controller.time.time',return_value=wall-100000),patch('controller.time.monotonic',return_value=116):
            with self.assertRaisesRegex(RuntimeError,'monotonic'):self.worker.assert_authority()

    def test_overlong_deadline_capped_at_fifteen_seconds(self):
        wall=time.time();original=self.server.call
        def overlong(*args):
            result=original(*args);result['valid_until']=int(wall)+999
            return result
        self.server.call=overlong
        with patch('controller.time.time',return_value=wall),patch('controller.time.monotonic',side_effect=[100,101]):
            self.worker.validate(self.tasks[0])
        self.assertEqual(self.worker.authority_deadline,115)

    def test_replayed_or_revalidation_required_denied(self):
        original=self.server.call
        for key in ('replayed','requires_live_revalidation'):
            def stale(*args):
                result=original(*args);result[key]=True;return result
            self.server.call=stale
            with self.assertRaises(RuntimeError):self.worker.validate(self.tasks[0])

    def test_no_tool_calls_accepted_in_result(self):
        self.worker.tick();self.finish()
        self.codex.turns[-1]['items'].append({'type':'commandExecution','command':'echo unsafe'})
        with self.assertRaisesRegex(RuntimeError,'side_effect'):self.worker.tick()

    def test_hash_verified_after_restart_and_before_completed(self):
        self.worker.tick();self.finish();self.artifact.write_text('changed')
        with self.assertRaises(ValueError):self.worker.tick()
        self.assertNotEqual(self.tasks[0]['state'],'completed')

    def test_foreign_fence_validation_rejected(self):
        original=self.server.call
        def wrong(*args):
            result=original(*args);result['task']['fence']+=1;return result
        self.server.call=wrong
        with self.assertRaisesRegex(RuntimeError,'binding_changed'):self.worker.validate(self.tasks[0])

    def test_follow_on_disabled(self):
        with self.assertRaisesRegex(ValueError,'follow_on_disabled'):self.worker.propose_follow_on('unused',{})

    def test_transient_terminal_history_not_completed_while_live(self):
        self.worker.tick();self.finish();self.codex.busy=True
        self.assertEqual(self.worker.tick(),'running')
        self.assertNotEqual(self.tasks[0]['state'],'completed')

    def test_completion_flag_required(self):
        self.worker.tick();self.finish();original=self.server.call
        def unaccepted(*args):
            result=original(*args);result.pop('completion_accepted',None);return result
        self.server.call=unaccepted
        self.assertEqual(self.worker.tick(),'completion_not_accepted')
        self.assertEqual(self.journal.active()['phase'],'reconcile_required')


del AdapterTests

if __name__=='__main__':unittest.main()
