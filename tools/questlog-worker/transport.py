"""Fixed HTTPS origin, no cookies/proxies/redirects; local signer only."""
import hashlib
import http.client
import time
from uuid import uuid4
from protocol import Contract,canonical,decode

HOST='questlog.casual-heroes.com'
PATH='/api/v1/questlog-dispatcher/worker/'
VERSION='questlog.dispatcher.v1'


def signed_message(worker,request,timestamp,body):
    return ('questlog.dispatcher.worker.v1\nPOST\n'+PATH+'\n'+worker+'\n'+request+'\n'+str(timestamp)+'\n'+hashlib.sha256(body).hexdigest()).encode()


class HTTPError(RuntimeError):
    def __init__(self,status,code,retry_after=None):
        super().__init__('dispatcher_http_'+str(status)+':'+code)
        self.status=status;self.retry_after=retry_after


class Client:
    def __init__(self,worker,signer):self.worker=worker;self.signer=signer;self.contract=Contract()
    def call(self,operation,payload,operation_id):
        body=canonical({'version':VERSION,'operation':operation,'operation_id':operation_id,'payload':payload})
        if len(body)>16000:raise ValueError('request_budget')
        self.contract.validate('WorkerRequest',decode(body))
        request=str(uuid4());timestamp=int(time.time())
        headers={'Content-Type':'application/json','Accept':'application/json','User-Agent':'QuestLog-WoW-Review-Worker/0.1',
            'X-QuestLog-Worker-ID':self.worker,'X-QuestLog-Request-ID':request,'X-QuestLog-Timestamp':str(timestamp),
            'X-QuestLog-Signature':self.signer(signed_message(self.worker,request,timestamp,body))}
        conn=http.client.HTTPSConnection(HOST,timeout=12)
        try:
            conn.request('POST',PATH,body,headers);response=conn.getresponse();raw=response.read(65537)
            if len(raw)>65536:raise ValueError('reply_budget')
            if response.status!=200:
                try:code=decode(raw).get('error','request_rejected')
                except (ValueError,UnicodeError):code='non_json_reply'
                raise HTTPError(response.status,str(code)[:160],response.getheader('Retry-After'))
            if 'json' not in (response.getheader('Content-Type') or ''):raise ValueError('reply_not_json')
            value=self.contract.validate('WorkerReply',decode(raw))
            if value['version']!=VERSION:raise ValueError('version_mismatch')
            return value
        finally:conn.close()
