"""Benign filesystem isolation check; never reads any actual secret or game file."""
import json
from pathlib import Path
import sys
write_denied=False;read_denied=False
try:Path(sys.argv[1]).write_text('unexpected sandbox write')
except PermissionError:write_denied=True
try:Path(sys.argv[2]).read_bytes()
except PermissionError:read_denied=True
print(json.dumps({'worktree_write_denied':write_denied,'protected_nonsecret_canary_read_denied':read_denied,
                  'actual_key_read':False,'game_files_accessed':False}))
if not (write_denied and read_denied):raise SystemExit(1)
