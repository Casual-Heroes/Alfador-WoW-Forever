"""Host-local durable queue/RPC journal. Never stores signing/Codex credentials."""
from contextlib import contextmanager
import json
import os
import sqlite3
import time
from uuid import uuid4
from protocol import canonical


class Journal:
    def __init__(self,path,lock_database=None):
        self.path=path;self.db=sqlite3.connect(path,timeout=10,isolation_level=None)
        self.db.row_factory=sqlite3.Row
        self.db.executescript('''
        PRAGMA synchronous=FULL;
        CREATE TABLE IF NOT EXISTS operations(key TEXT PRIMARY KEY,id TEXT NOT NULL,operation TEXT NOT NULL,payload BLOB NOT NULL,response BLOB);
        CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,snapshot BLOB NOT NULL,phase TEXT NOT NULL,turn TEXT,evidence BLOB,first_seen REAL NOT NULL DEFAULT (unixepoch()));
        CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,at REAL NOT NULL,status TEXT NOT NULL,details BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS reservations(worktree TEXT PRIMARY KEY,task_id TEXT NOT NULL,worker_id TEXT NOT NULL);
        ''')
        self.locks=self.db if lock_database is None else sqlite3.connect(lock_database,timeout=10,isolation_level=None)
        self.locks.row_factory=sqlite3.Row
        self.locks.execute('CREATE TABLE IF NOT EXISTS reservations(worktree TEXT PRIMARY KEY,task_id TEXT NOT NULL,worker_id TEXT NOT NULL)')
    def record(self,status,**details):
        self.db.execute('INSERT INTO events(at,status,details) VALUES(?,?,?)',(time.time(),status,canonical(details)))
    def rpc(self,client,key,operation,payload):
        raw=canonical(payload)
        self.db.execute('INSERT OR IGNORE INTO operations(key,id,operation,payload) VALUES(?,?,?,?)',(key,str(uuid4()),operation,raw))
        row=self.db.execute('SELECT * FROM operations WHERE key=?',(key,)).fetchone()
        if row['operation']!=operation or bytes(row['payload'])!=raw:raise ValueError('immutable_operation_conflict')
        if row['response'] is not None:return json.loads(row['response'])
        # A timeout leaves this same operation ID/body pending for safe replay.
        result=client.call(operation,payload,row['id'])
        self.db.execute('UPDATE operations SET response=? WHERE key=?',(canonical(result),key))
        return result
    def fresh(self,client,operation,payload):return self.rpc(client,str(uuid4()),operation,payload)
    def save(self,task,phase,turn=None,evidence=None):
        self.db.execute('INSERT INTO tasks(id,snapshot,phase,turn,evidence) VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET snapshot=excluded.snapshot,phase=excluded.phase,turn=coalesce(excluded.turn,tasks.turn),evidence=coalesce(excluded.evidence,tasks.evidence)',
            (task['id'],canonical(task),phase,turn,canonical(evidence) if evidence else None))
    def active(self):
        row=self.db.execute("SELECT * FROM tasks WHERE phase NOT IN ('completed','failed','cancelled','blocked_before_dispatch') ORDER BY rowid LIMIT 1").fetchone()
        return dict(row) if row else None
    def reserve(self,path,task,worker):
        canonical_path=str(path.resolve()).casefold()
        self.locks.execute('INSERT OR IGNORE INTO reservations VALUES(?,?,?)',(canonical_path,task,worker))
        row=self.locks.execute('SELECT * FROM reservations WHERE worktree=?',(canonical_path,)).fetchone()
        if row['task_id']!=task or row['worker_id']!=worker:raise RuntimeError('local_worktree_reserved')
    def release(self,path,task):self.locks.execute('DELETE FROM reservations WHERE worktree=? AND task_id=?',(str(path.resolve()).casefold(),task))


@contextmanager
def pump_lock(path):
    with open(path,'a+b') as stream:
        stream.seek(0,2)
        if not stream.tell():stream.write(b'0');stream.flush()
        stream.seek(0)
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:yield
        finally:
            stream.seek(0)
            if os.name=='nt':msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(stream.fileno(),fcntl.LOCK_UN)
