"""Windows CurrentUser DPAPI; Ed25519 via local Node built-in crypto.
Private signing material never enters a worktree, shared exchange or argv.
"""
import base64
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess

STATE=Path(r'C:\Users\Tom\AppData\Local\QuestLogWoWWorker')
LOCKS=Path(r'C:\Users\Tom\AppData\Local\QuestLogDeveloperWorkers')
NODE=Path(r'C:\Program Files\nodejs\node.exe')


def node(script,data):
    proc=subprocess.run([str(NODE),'-e',script],input=data,capture_output=True,check=True,timeout=20)
    return proc.stdout


def dpapi(data,unprotect=False):
    if os.name!='nt':raise RuntimeError('windows_current_user_dpapi_required')
    class Blob(ctypes.Structure):_fields_=[('cbData',wintypes.DWORD),('pbData',ctypes.POINTER(ctypes.c_ubyte))]
    buffer=ctypes.create_string_buffer(data);source=Blob(len(data),ctypes.cast(buffer,ctypes.POINTER(ctypes.c_ubyte)));dest=Blob()
    function=ctypes.windll.crypt32.CryptUnprotectData if unprotect else ctypes.windll.crypt32.CryptProtectData
    # CRYPTPROTECT_UI_FORBIDDEN, CURRENT USER (not LOCAL_MACHINE).
    if not function(ctypes.byref(source),None,None,None,None,1,ctypes.byref(dest)):raise ctypes.WinError()
    try:return ctypes.string_at(dest.pbData,dest.cbData)
    finally:ctypes.windll.kernel32.LocalFree(dest.pbData)


def create_key():
    path=STATE/'signing-key.dpapi'
    if path.exists():raise RuntimeError('signing_identity_already_exists_do_not_overwrite')
    raw=json.loads(node("const c=require('crypto');let k=c.generateKeyPairSync('ed25519');process.stdout.write(JSON.stringify({private:k.privateKey.export({format:'der',type:'pkcs8'}).toString('base64'),public:k.publicKey.export({format:'der',type:'spki'}).subarray(-32).toString('hex')}));",b''))
    protected=dpapi(base64.b64decode(raw['private']))
    with path.open('xb') as stream:stream.write(protected)
    return raw['public']


def sign(message):
    private=dpapi((STATE/'signing-key.dpapi').read_bytes(),True)
    payload=json.dumps({'private':base64.b64encode(private).decode(),'message':base64.b64encode(message).decode()}).encode()
    return node("let a='';process.stdin.on('data',x=>a+=x).on('end',()=>{const c=require('crypto'),v=JSON.parse(a),k=c.createPrivateKey({key:Buffer.from(v.private,'base64'),format:'der',type:'pkcs8'});process.stdout.write(c.sign(null,Buffer.from(v.message,'base64'),k).toString('base64'))});",payload).decode()

