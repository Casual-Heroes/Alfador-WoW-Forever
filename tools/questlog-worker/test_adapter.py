import base64
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import time
import unittest
from uuid import uuid4
from controller import Worker,INPUT_KEYS
from journal import Journal,pump_lock
from protocol import Contract,Invalid,canonical,digest,decode
from secure_identity import node
from transport import signed_message


class FakeServer:
    def __init__(self,tasks,profile):
        self.tasks=tasks;self.profile=profile;self.receipts={};self.calls=[];self.online=True;self.authorized=True;self.lose=None
    def call(self,op,payload,opid):
        self.calls.append((op,payload,opid))
        if not self.online:raise ConnectionError('offline')
        if opid in self.receipts:return {**self.receipts[opid],'execution_authorized':False,'replayed':True}
        if op=='poll':
            reply={'worker':{'id':self.profile['worker_id'],'binding_digest':self.tasks[0]['binding_digest']},
                   'tasks':[t for t in self.tasks if t['state'] not in ('completed','failed','cancelled')]}
        elif op=='claim':
            task=next((t for t in self.tasks if t['state']=='queued'),None)
            if task:task.update(state='claimed',lease_id=str(uuid4()),fence=1)
            reply={'task':copy.deepcopy(task),'execution_authorized':False}
        else:
            task=next(t for t in self.tasks if t['id']==payload['task_id'])
            if op in ('validate','heartbeat','started') and not self.authorized:raise PermissionError('revoked')
            if op=='reserve_dispatch':task.update(dispatch_id=task['dispatch_id'] or str(uuid4()),state='dispatched_to_chat')
            elif op=='started':task.update(turn_id=payload['turn_id'],state='running')
            elif op=='report':task.update(state=payload['status'])
            elif op=='reconcile':
                task.update(state={'unknown':'reconcile_required'}.get(payload['resolution'],payload['resolution']),turn_id=payload['turn_id'])
            reply={'task':copy.deepcopy(task),'execution_authorized':op=='validate','valid_until':int(time.time())+15,'completion_accepted':op in ('report','reconcile') and task['state'] in ('completed','failed','cancelled')}
        reply={'version':'questlog.dispatcher.v1',**reply};self.receipts[opid]=copy.deepcopy(reply)
        if self.lose==op:self.lose=None;raise ConnectionError('lost_response')
        return reply


class FakeCodex:
    def __init__(self,thread):self.thread=thread;self.turns=[];self.starts=0;self.interrupts=[];self.lose=False;self.busy=False
    def call(self,method,params):
        if 'threadId' in params:assert params['threadId']==self.thread
        if method=='thread/read':return {'thread':{'status':{'type':'active' if self.busy else 'idle'}}}
        if method=='thread/turns/list':return {'data':self.turns,'nextCursor':None}
        if method=='turn/interrupt':self.interrupts.append(params['turnId']);return {}
        if method=='turn/start':
            self.starts+=1;turn={'id':'turn-'+str(self.starts),'status':'inProgress',
                'items':[{'type':'userMessage','content':params['input']}]}
            self.turns.append(turn)
            if self.lose:self.lose=False;raise ConnectionError('lost_codex_ack')
            return {'turn':copy.deepcopy(turn)}
        raise AssertionError(method)


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);(self.root/'worker-inputs').mkdir();self.artifact=self.root/'worker-inputs'/'fixture.txt';self.artifact.write_bytes(b'public synthetic test fixture')
        self.profile={'worker_id':str(uuid4()),'device_id':str(uuid4()),'team':'addon','repository':str(self.root),
            'worktree':str(self.root),'lock_id':str(uuid4()),'chat_id':'dedicated-test-chat','public_key':'a'*64,
            'allowed_actions':['review'],'recipes':{},'enabled':True,'verification_sha256':None}
        self.tasks=[self.task(),self.task()];self.server=FakeServer(self.tasks,self.profile);self.codex=FakeCodex(self.profile['chat_id'])
        self.journal=Journal(self.root/'test.sqlite3');self.make_worker()
    def tearDown(self):self.journal.db.close();self.tmp.cleanup()
    def make_worker(self):self.worker=Worker(self.profile,self.journal,self.server,self.codex,
        {hashlib.sha256(self.artifact.read_bytes()).hexdigest():str(self.artifact)},self.root/'evidence',
        publisher=lambda p:{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'delivered_to':'server_a_inbox','verified':True})
    def task(self):
        p=self.profile;now=int(time.time());t={k:p[k] for k in ('worker_id','device_id','repository','worktree','lock_id','chat_id','team')}
        t.update(id=str(uuid4()),action='review',artifact_sha256=hashlib.sha256(self.artifact.read_bytes()).hexdigest(),
            instructions='Edition: Shared\nRead the public synthetic fixture; return a brief summary.',checks=['worker_binding','nonempty_result','artifact_pin','read_only_review'],
            dependencies=[],timeout_seconds=120,recipe_id=None,recipe_sha256=None,deployment=None,
            owner_id=1,revision=1,queue_order=1,created_at=now,lease_expires_at=now+60,fence=0,
            binding_digest=digest({k:v for k,v in p.items() if k not in ('enabled','verification_sha256')}),
            state='queued',approval_revision=None,approval_expires_at=None,authorized_until=now+3600,started_at=None,
            lease_id=None,dispatch_id=None,parent_task_id=None,follow_on_id=None,turn_id=None,last_report='',evidence=None)
        t['instructions_digest']=digest({k:t[k] for k in INPUT_KEYS});return t
    def finish(self):
        self.codex.turns[-1]['status']='completed';self.codex.turns[-1]['items'].append({'type':'agentMessage','text':'Public fixture reviewed.'})
    def test_signature_vector_and_tamper_rejection(self):
        v=json.loads(Path(__file__).with_name('signature-vector.json').read_text());body=v['body_utf8'].encode()
        self.assertEqual(signed_message(v['worker_id'],v['request_id'],v['timestamp'],body),v['message_utf8'].encode())
        self.assertEqual(hashlib.sha256(body).hexdigest(),v['body_sha256'])
        script="let a='';process.stdin.on('data',x=>a+=x).on('end',()=>{let v=JSON.parse(a),c=require('crypto'),k=c.createPublicKey({key:Buffer.from('302a300506032b6570032100'+v.public_key,'hex'),type:'spki',format:'der'});process.stdout.write(JSON.stringify([c.verify(null,Buffer.from(v.message_utf8),k,Buffer.from(v.signature_base64,'base64')),c.verify(null,Buffer.from(v.message_utf8+'\\n'),k,Buffer.from(v.signature_base64,'base64'))]))});"
        self.assertEqual(json.loads(node(script,json.dumps(v).encode())),[True,False])
    def test_closed_schema_rejects_owner_override_and_duplicates(self):
        contract=Contract();request={'version':'questlog.dispatcher.v1','operation':'poll','operation_id':str(uuid4()),'payload':{}}
        contract.validate('WorkerRequest',request);request['payload']['owner_id']=1
        with self.assertRaises(Invalid):contract.validate('WorkerRequest',request)
        with self.assertRaises(Invalid):decode(b'{"operation":1,"operation":2}')
    def test_registration_and_task_snapshots_match_contract(self):
        Contract().validate('WorkerRegistration',self.profile)
        for t in self.tasks:Contract().validate('TaskSnapshot',t)
    def test_two_tasks_sequential_actual_adapter(self):
        self.assertEqual(self.worker.tick(),'started');self.assertEqual(self.worker.tick(),'running');self.assertEqual(self.codex.starts,1)
        self.finish();self.assertEqual(self.worker.tick(),'completed')
        self.assertEqual(self.worker.tick(),'started');self.assertEqual(self.codex.starts,2)
        self.finish();self.assertEqual(self.worker.tick(),'completed')
    def test_lost_codex_ack_reconciles_no_duplicate(self):
        self.codex.lose=True
        with self.assertRaises(ConnectionError):self.worker.tick()
        self.assertEqual(self.worker.tick(),'running');self.assertEqual(self.codex.starts,1)
        self.finish();self.assertEqual(self.worker.tick(),'completed')
    def test_restart_preserves_thread_turn_and_completion(self):
        self.worker.tick();self.journal.db.close();self.journal=Journal(self.root/'test.sqlite3');self.make_worker()
        self.assertEqual(self.worker.tick(),'running');self.assertEqual(self.codex.starts,1)
        self.finish();self.assertEqual(self.worker.tick(),'completed')
    def test_absent_uncertain_turn_never_restarted(self):
        self.codex.lose=True
        with self.assertRaises(ConnectionError):self.worker.tick()
        self.codex.turns=[];self.assertEqual(self.worker.tick(),'reconcile_required')
        self.assertEqual(self.worker.tick(),'reconcile_required');self.assertEqual(self.codex.starts,1)
    def test_disconnect_in_running_turn_interrupts_original(self):
        self.worker.tick();self.server.online=False
        with self.assertRaises(ConnectionError):self.worker.tick()
        self.assertEqual(self.codex.interrupts,['turn-1'])
        self.assertEqual(self.journal.active()['phase'],'interrupted')
    def test_revocation_interrupts_without_new_turn(self):
        self.worker.tick();self.server.authorized=False
        with self.assertRaises(PermissionError):self.worker.tick()
        self.assertEqual(self.codex.interrupts,['turn-1']);self.assertEqual(self.codex.starts,1)
    def test_task_wrong_target_worktree_chat_and_digest(self):
        for key,bad in [('team','desktop'),('chat_id','another-chat'),('binding_digest','b'*64),('worktree',str(self.root/'elsewhere'))]:
            task=copy.deepcopy(self.tasks[0]);task[key]=bad
            with self.assertRaises(ValueError):self.worker.check_task(task)
        self.assertEqual(self.codex.starts,0)
    def test_changed_artifact_blocks_before_codex(self):
        self.artifact.write_bytes(b'changed')
        with self.assertRaises(ValueError):self.worker.tick()
        self.assertEqual(self.codex.starts,0)
    def test_unknown_tests_cannot_be_marked_passed(self):
        task=copy.deepcopy(self.tasks[0]);task['checks']=['imaginary_test'];task['instructions_digest']=digest({k:task[k] for k in INPUT_KEYS})
        with self.assertRaises(ValueError):self.worker.check_task(task)
    def test_failed_result_delivery_prevents_completed_report(self):
        self.worker.tick();self.finish();self.worker.publisher=lambda p:None
        with self.assertRaises(RuntimeError):self.worker.tick()
        self.assertNotEqual(self.tasks[0]['state'],'completed')
        self.assertEqual(self.journal.active()['phase'],'running')
    def test_duplicate_mutating_rpc_reuses_operation_id(self):
        self.server.lose='claim'
        with self.assertRaises(ConnectionError):self.worker.tick()
        self.assertEqual(self.worker.tick(),'started');self.assertEqual(self.codex.starts,1)
        calls=[c for c in self.server.calls if c[0]=='claim'];self.assertEqual(calls[0][2],calls[1][2])
    def test_disconnect_before_stdio_intent_can_safely_continue_same_reservation(self):
        self.server.lose='validate'
        with self.assertRaises(ConnectionError):self.worker.tick()
        self.assertEqual(self.codex.starts,0);self.assertEqual(self.journal.active()['phase'],'reserved')
        self.assertEqual(self.worker.tick(),'started');self.assertEqual(self.codex.starts,1)
    def test_busy_chat_not_steered(self):
        self.codex.busy=True;self.assertEqual(self.worker.tick(),'chat_busy');self.assertEqual(self.codex.starts,0)
    def test_pump_lock_excludes_second_controller(self):
        with pump_lock(self.root/'pump.lock'):
            with self.assertRaises(OSError):
                with pump_lock(self.root/'pump.lock'):pass
    def test_different_workers_share_persistent_worktree_reservations(self):
        a=Journal(self.root/'a.sqlite3',self.root/'shared.sqlite3');b=Journal(self.root/'b.sqlite3',self.root/'shared.sqlite3')
        try:
            a.reserve(self.root,'task-a','worker-a')
            with self.assertRaises(RuntimeError):b.reserve(self.root,'task-b','worker-b')
            a.db.close();a.locks.close();a=Journal(self.root/'a.sqlite3',self.root/'shared.sqlite3')
            with self.assertRaises(RuntimeError):b.reserve(self.root,'task-b','worker-b')
            a.release(self.root,'task-a');b.reserve(self.root,'task-b','worker-b')
        finally:
            a.locks.close();a.db.close();b.locks.close();b.db.close()
    def test_no_installation_or_recipe_execution_interface(self):
        self.assertFalse(hasattr(self.worker,'install'));self.assertEqual(self.profile['recipes'],{})


if __name__=='__main__':unittest.main()
