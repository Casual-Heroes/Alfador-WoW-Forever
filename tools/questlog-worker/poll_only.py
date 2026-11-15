"""Read-only signed discovery; no claim/start action."""
import json
from pathlib import Path
from uuid import uuid4
from secure_identity import STATE, sign
from transport import Client, HTTPError
from journal import Journal
from protocol import canonical
profile=json.loads((STATE/'registration.json').read_text())
journal=Journal(STATE/'worker.sqlite3')
try:
 value=journal.fresh(Client(profile['worker_id'],sign),'poll',{})
 result={'state':'poll_succeeded','worker_id':profile['worker_id'],'task_claimed':False,
         'worker_binding':value.get('worker',{}).get('binding_digest'),'central_acceptance':False}
except HTTPError as error:
 result={'state':'registration_or_discovery_pending','http_status':error.status,'reason':str(error),
         'worker_id':profile['worker_id'],'task_claimed':False,'central_acceptance':False}
finally:journal.db.close()
path=Path(__file__).resolve().parents[2]/'docs'/'dispatcher'/'SIGNED-POLL.json'
if path.exists():raise RuntimeError('Do not overwrite a discovery receipt')
with path.open('xb') as stream:stream.write(canonical(result))
print(json.dumps(result))
