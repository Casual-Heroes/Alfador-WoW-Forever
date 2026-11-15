"""Explicit development bootstrap; only a NEW dedicated WoW thread."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import time
import queue
from uuid import uuid4
from codex_rpc import RPC, CODEX
from protocol import Contract, canonical, digest
from secure_identity import STATE, LOCKS, create_key, sign, node

WORKTREE=Path(__file__).resolve().parents[2]
PROJECT=Path(r'G:\Projects\Alfador-WoW')


def immutable(path, value):
    raw=canonical(value)
    if path.exists():
        if path.read_bytes()!=raw:raise RuntimeError('immutable_identity_collision')
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:stream.write(raw);stream.flush()


def run_turn(rpc, identity, marker):
    reply=rpc.call('turn/start',{'threadId':identity,
        'input':[{'type':'text','text':'Edition: Shared\nOwner-approved local setup probe. Return exactly '+marker+'. Use no tools, access no files or network, and make no changes. This is not a central QuestLog task.'}],
        'cwd':str(WORKTREE),'approvalPolicy':'never','sandboxPolicy':{'type':'readOnly','networkAccess':False}})
    turn_id=reply['turn']['id'];deadline=time.monotonic()+120
    while time.monotonic()<deadline:
        try:event=rpc.notifications.pop(0) if rpc.notifications else rpc.next(timeout=2)
        except queue.Empty:continue
        if 'id' in event and 'method' in event:
            rpc.send({'id':event['id'],'error':{'code':-32601,'message':'No tool approvals permitted'}})
            continue
        params=event.get('params',{})
        if event.get('method')=='turn/completed' and params.get('threadId')==identity and params.get('turn',{}).get('id')==turn_id:
            turns=rpc.call('thread/turns/list',{'threadId':identity,'itemsView':'full','limit':10,'sortDirection':'desc'})['data']
            turn=next(turn for turn in turns if turn['id']==turn_id)
            messages=[item.get('text','') for item in turn.get('items',[]) if item.get('type')=='agentMessage']
            tools=[item.get('type') for item in turn.get('items',[]) if item.get('type') not in ('userMessage','agentMessage','reasoning')]
            passed=turn['status']=='completed' and marker in messages and not tools
            evidence={'thread_id':identity,'turn_id':turn_id,'status':turn['status'],
                      'expected_marker':marker,'marker_returned':marker in messages,'tool_items':tools,'passed':passed}
            if not passed:raise RuntimeError('local_setup_turn_failed_keep_original_identity')
            return evidence
        time.sleep(.5)
    raise RuntimeError('setup_turn_uncertain_reconcile_original_thread_do_not_bootstrap_again')


def main():
    if (STATE/'registration.json').exists():
        profile=json.loads((STATE/'registration.json').read_text())
        identity=profile['chat_id'];public=profile['public_key']
        if (WORKTREE/'docs'/'dispatcher'/'LOCAL-THREAD-EVIDENCE.json').exists():
            raise RuntimeError('Setup already complete; do not repeat setup turns')
        rpc=RPC(WORKTREE)
        try:
            rpc.resume(identity)
            history=rpc.call('thread/turns/list',{'threadId':identity,'itemsView':'full','limit':20,'sortDirection':'desc'})
            if history.get('nextCursor') or any(t['status'] not in ('completed','interrupted','failed') for t in history['data']):
                raise RuntimeError('Original setup turn unresolved; no new turn permitted')
            immutable(STATE/'initial-attempt-reconciliation.json',{'thread_id':identity,
                'prior_turns':[{'id':t['id'],'status':t['status']} for t in history['data']],
                'reason':'Initial setup inspected stored history too early; corrected to wait for turn/completed notification.',
                'replacement_thread_created':False,'key_rotated':False})
            first=run_turn(rpc,identity,'WOW_LOCAL_SETUP_ONE_20261115')
            immutable(STATE/'first-turn.json',first)
        finally:rpc.close()
    else:
        if STATE.exists():raise RuntimeError('Incomplete state without registration; preserve and reconcile before proceeding')
        STATE.mkdir(parents=True)
        owner=subprocess.run(['whoami'],capture_output=True,text=True,check=True).stdout.strip()
        subprocess.run(['icacls',str(STATE),'/inheritance:r','/grant:r',owner+':(OI)(CI)F','SYSTEM:(OI)(CI)F'],check=True,capture_output=True)
        public=create_key()
        rpc=RPC(WORKTREE)
        try:
            identity=rpc.create()
            immutable(STATE/'thread-created.json',{'thread_id':identity,'worktree':str(WORKTREE)})
            profile={'worker_id':str(uuid4()),'device_id':str(uuid4()),'team':'addon',
                     'repository':str(PROJECT/'Forever'),'worktree':str(WORKTREE),
                     'lock_id':str(uuid4()),'chat_id':identity,'public_key':public,
                     'allowed_actions':['review'],'recipes':{},'enabled':True,'verification_sha256':None}
            Contract().validate('WorkerRegistration',profile)
            immutable(STATE/'registration.json',profile)
            first=run_turn(rpc,identity,'WOW_LOCAL_SETUP_ONE_20261115')
            immutable(STATE/'first-turn.json',first)
        finally:rpc.close()
    # New process and exact ID, never a history search or a replacement thread.
    rpc=RPC(WORKTREE)
    try:
        resumed=rpc.resume(identity)
        second=run_turn(rpc,identity,'WOW_LOCAL_SETUP_TWO_20261115')
    finally:rpc.close()
    rpc=RPC(WORKTREE)
    try:
        rpc.resume(identity)
        turns=rpc.call('thread/turns/list',{'threadId':identity,'itemsView':'full','limit':20,'sortDirection':'desc'})['data']
        actual={turn['id'] for turn in turns}
        if first['turn_id'] not in actual or second['turn_id'] not in actual:raise RuntimeError('history_not_persistent')
    finally:rpc.close()
    challenge=canonical({'purpose':'public WoW registration key possession','registration_sha256':digest(profile)})
    signature=sign(challenge)
    verify="let a='';process.stdin.on('data',x=>a+=x).on('end',()=>{let v=JSON.parse(a),c=require('crypto'),k=c.createPublicKey({key:Buffer.from('302a300506032b6570032100'+v.public_key,'hex'),format:'der',type:'spki'});process.stdout.write(JSON.stringify(c.verify(null,Buffer.from(v.message,'base64'),k,Buffer.from(v.signature,'base64'))))});"
    if node(verify,json.dumps({'public_key':public,'message':base64.b64encode(challenge).decode(),'signature':signature}).encode())!=b'true':raise RuntimeError('key_possession_failed')
    evidence={'schema':'questlog.wow-worker.local-thread-evidence.v1','profile':profile,
              'first_turn':first,'resumed_turn':second,'third_process_history_verified':True,
              'effective_sandbox':resumed['sandbox'],'approval_policy':resumed['approvalPolicy'],
              'codex_binary':str(CODEX),'codex_sha256':hashlib.sha256(CODEX.read_bytes()).hexdigest(),
              'codex_version':subprocess.run([str(CODEX),'--version'],capture_output=True,text=True,check=True).stdout.strip(),
              'public_possession':{'message_base64':base64.b64encode(challenge).decode(),'signature_base64':signature},
              'key_storage':'current-user DPAPI, owner/SYSTEM ACL, outside source/worktrees/exchange',
              'central_tasks_completed':False,'background_installed':False,'currently_running':False}
    if (STATE/'initial-attempt-reconciliation.json').exists():
        evidence['initial_attempt_reconciliation']=json.loads((STATE/'initial-attempt-reconciliation.json').read_text())
    public_dir=WORKTREE/'docs'/'dispatcher'
    immutable(public_dir/'WorkerRegistration.json',profile)
    immutable(public_dir/'LOCAL-THREAD-EVIDENCE.json',evidence)
    artifacts={}
    tasks=[]
    for edition,token,check in [('Forever','WOW_FOREVER_CANARY','canary_token_one'),('Retail','WOW_RETAIL_CANARY','canary_token_two')]:
        path=WORKTREE/'worker-inputs'/(edition+'-readonly-canary.txt')
        pin=hashlib.sha256(path.read_bytes()).hexdigest();artifacts[pin]=str(path)
        task={'worker_id':profile['worker_id'],'action':'review','artifact_sha256':pin,
              'instructions':'Edition: '+edition+'\nHarmless central read-only check. Summarize only the supplied artifact in one sentence and return '+token+'. Use no tools. Do not infer facts about the other edition. No file changes, network, installation, activation, restart or gameplay actions.',
              'checks':['worker_binding','original_turn_terminal','read_only_review','artifact_pin','nonempty_result',check],
              'dependencies':[],'timeout_seconds':180,'recipe_id':None,'recipe_sha256':None,'deployment':None}
        Contract().validate('TaskInput',task);tasks.append(task)
    immutable(STATE/'artifact-map.json',artifacts)
    immutable(public_dir/'CENTRAL-CHECKS.json',{'sender':'WoW dispatcher setup','recipient':'Server A dispatcher operator',
              'required_action':'Register exact profile; assign Forever first, then Retail with dependency on actual first task ID. Do not enable background installation.',
              'task_templates':tasks,'second_task_dependency':'Replace empty dependencies in second template with the actual first task ID before assignment.'})
    immutable(public_dir/'SOURCE-LAYOUT.json',{
        'primary_controller_repository':str(PROJECT/'Forever'),'registered_worktree':str(WORKTREE),
        'edition_worktrees':{e:str(WORKTREE.parent/e) for e in ('Forever','Retail')},
        'repositories':{e:{'root':str(PROJECT/e),'remote':'https://github.com/Casual-Heroes/Alfador-WoW-'+e+'.git',
             'baseline_commit':subprocess.run(['git','-C',str(PROJECT/e),'rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()} for e in ('Forever','Retail')},
        'shared_files':{'root':str(PROJECT),'handling':'Originals preserved; bootstrap context snapshots tracked independently in each edition.'},
        'one_serial_worker':True,'edition_required':['Forever','Retail','Shared']})
    # Existing host-wide registry is reused only for locking, never identities.
    if not LOCKS.is_dir():raise RuntimeError('existing_shared_lock_registry_missing')
    print(json.dumps({'worker_id':profile['worker_id'],'thread_id':identity,'local_control_checks_passed':True,
                      'public_registration':str(public_dir/'WorkerRegistration.json'),
                      'private_state_path':str(STATE),'central_acceptance':False,'background_installed':False}))


if __name__=='__main__':main()
