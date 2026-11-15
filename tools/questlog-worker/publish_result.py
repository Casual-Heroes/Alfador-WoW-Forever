"""Only generated canary results to Server A through the existing exchange."""
import hashlib
from pathlib import Path
import re
import subprocess
from protocol import decode
HUB=Path(r'G:\OneDrive\MeldTools\ServerHandoffs')
HELPER=HUB/'Transfer-VerifiedHandoff.ps1'
HELPER_PIN='be2ff89147cd1e81810dbcd2ef8df66974e83a9d378a1748cf6629dc054e1130'

def publish(path):
    path=Path(path);name=path.name
    if not re.fullmatch(r'WOW-DISPATCH-[a-f0-9-]{36}-result\.json',name) or path.is_symlink():raise ValueError('only_generated_dispatch_result')
    raw=path.read_bytes()
    if len(raw)>65536:raise ValueError('result_budget')
    value=decode(raw)
    if value.get('recipient')!='server_a' or value.get('intended_action')!='attach_verified_result_to_task':raise ValueError('result_intent_required')
    if re.search(r'BEGIN .*PRIVATE KEY|\bsk-[A-Za-z0-9_-]{20,}|(?:access_token|refresh_token|password)\s*[=:]\s*\S+',raw.decode(),re.I):raise ValueError('result_credentials_prohibited')
    expected=hashlib.sha256(raw).hexdigest()
    if hashlib.sha256(HELPER.read_bytes()).hexdigest()!=HELPER_PIN:raise ValueError('trusted_transfer_helper_changed')
    destination=HUB/name
    if destination.exists():
        if destination.is_symlink() or destination.read_bytes()!=raw:raise ValueError('immutable_result_collision')
    else:
        with destination.open('xb') as stream:stream.write(raw)
    result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-File',str(HELPER),'-Server','chcmty','-Files',name],capture_output=True,text=True,check=True,timeout=60)
    if not any(line in result.stdout for line in [f'DELIVERED_VERIFIED chcmty {name} {expected}',f'VERIFIED_EXISTING chcmty {name} {expected}']):raise RuntimeError('remote_result_not_verified')
    root='/home/fulldata/ServerHandoffs';target=root+'/inbox/'+name;source=root+'/'+name
    command=f"if test -e '{target}'; then cmp '{source}' '{target}' || exit 1; else ln '{source}' '{target}' || exit 1; fi; sha256sum '{target}'"
    remote=subprocess.run(['ssh','-F','C:/Users/Tom/.ssh/config','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','chcmty',command],capture_output=True,text=True,check=True,timeout=30)
    if not remote.stdout.split() or remote.stdout.split()[0]!=expected:raise RuntimeError('inbox_result_not_verified')
    return {'name':name,'sha256':expected,'delivered_to':'server_a_inbox','verified':True}
