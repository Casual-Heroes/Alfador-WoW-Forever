"""Isolated marker-only reader. Never emits raw chat or uploads to Core."""
import argparse
import json
import math
import os
from pathlib import Path
import re
import time

MARKER = re.compile(rb'ALFADOR_XFER_V1 session=([a-f0-9]{32}) seq=([1-8]) sent=([0-9]{1,10}) END')
MAX_READ, MAX_LINE, POLL_SECONDS = 65536, 4096, .25


def shared_read(path):
    if os.name != 'nt':
        return path.open('rb')
    # Native file read only; allow the game writer, rotation and deletion.
    import ctypes
    from ctypes import wintypes
    import msvcrt
    api = ctypes.WinDLL('kernel32', use_last_error=True)
    api.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                               wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    api.CreateFileW.restype = wintypes.HANDLE
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = api.CreateFileW(str(path), 0x80000000, 0x1 | 0x2 | 0x4, None, 3, 0x08000000, None)
    if handle == ctypes.c_void_p(-1).value:
        raise OSError(ctypes.get_last_error(), 'source-not-readable')
    try:
        fd = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except Exception:
        api.CloseHandle(handle)
        raise
    try:
        return os.fdopen(fd, 'rb')
    except Exception:
        os.close(fd)
        raise


class MarkerTail:
    def __init__(self, trusted_forever_root, session):
        if not isinstance(session, str) or re.fullmatch('[a-f0-9]{32}', session) is None:
            raise ValueError('invalid-test-session')
        root = Path(trusted_forever_root).resolve(strict=True)
        directory = root / 'Logs'
        self.path = directory / 'WoWChatLog.txt'
        if directory.is_symlink() or directory.resolve(strict=True) != directory or self.path.is_symlink():
            raise ValueError('linked-path-not-allowed')
        if self.path.resolve(strict=True).parent != directory.resolve(strict=True):
            raise ValueError('out-of-scope-path')
        self.session = session.encode('ascii')
        self.handle = shared_read(self.path)
        try:
            disk, opened = self.path.stat(), os.fstat(self.handle.fileno())
            self.identity = (opened.st_dev, opened.st_ino)
            if self.identity != (disk.st_dev, disk.st_ino):
                raise ValueError('source-changed-before-ready')
            self.handle.seek(0, 2)
        except Exception:
            self.handle.close()
            raise
        self.started_monotonic = time.monotonic()
        self.ready_at_unix = time.time()
        self.buffer = b''
        self.last_sequence = self.receipt_count = self.duplicate_count = self.out_of_order_count = 0
        self.poll_id = self.batch_id = self.multimarker_batches = 0
        self.seen = set()
        self.closed = self.ready_emitted = False
        self.terminal_reason = None

    def ready_event(self):
        if self.closed: raise ValueError('reader-closed')
        self.ready_emitted = True
        return {'schema':'alfador.wowf.transport-marker-status.source2', 'event':'ready',
                'session':self.session.decode('ascii'), 'position':'end-of-file-before-send',
                'ready_at_unix_local':self.ready_at_unix, 'monotonic_elapsed_seconds':0,
                'poll_interval_seconds':POLL_SECONDS,
                'monotonic_resolution_seconds':time.get_clock_info('monotonic').resolution,
                'native_file_share': 'read-write-delete' if os.name == 'nt' else 'not-windows',
                'live_transport_verified':False}

    def close(self):
        self.closed = True
        self.buffer = b''
        self.handle.close()

    def fail(self, reason):
        self.terminal_reason = reason
        self.close()
        return [{'event':reason, 'live_transport_verified':False}]

    def poll(self, now=None, monotonic=None):
        if self.closed: raise ValueError('reader-closed')
        if not self.ready_emitted: raise ValueError('reader-not-ready')
        received = time.time() if now is None else now
        mono = time.monotonic() if monotonic is None else monotonic
        if (any(type(v) not in (int,float) or not math.isfinite(v) for v in (received,mono))
                or received < 0 or mono < self.started_monotonic):
            raise ValueError('invalid-receive-clock')
        elapsed = mono - self.started_monotonic
        self.poll_id += 1
        try: disk = self.path.stat()
        except OSError: return self.fail('source-unavailable')
        if (disk.st_dev,disk.st_ino) != self.identity or disk.st_size < self.handle.tell():
            return self.fail('source-replaced-or-truncated')
        if disk.st_size - self.handle.tell() > MAX_READ:
            return self.fail('read-budget-exceeded')
        try: chunk = self.handle.read(MAX_READ)
        except OSError: return self.fail('source-read-failed')
        lines = (self.buffer + chunk).split(b'\n')
        self.buffer = lines.pop()
        if len(self.buffer) > MAX_LINE: return self.fail('line-budget-exceeded')
        matches = []
        for line in lines:
            if len(line) > MAX_LINE: continue
            found = list(MARKER.finditer(line))
            if len(found) != 1 or found[0].group(1) != self.session: continue
            seq,sent = int(found[0].group(2)),int(found[0].group(3))
            if 0 < sent <= 9999999999: matches.append((seq,sent))
        if not matches: return []
        self.batch_id += 1
        if len(matches) > 1: self.multimarker_batches += 1
        result = []
        for seq,sent in matches:
            duplicate = seq in self.seen
            out_of_order = not duplicate and seq < self.last_sequence
            if duplicate: self.duplicate_count += 1
            else:
                self.seen.add(seq); self.receipt_count += 1
                if out_of_order: self.out_of_order_count += 1
                self.last_sequence = max(self.last_sequence,seq)
            result.append({'schema':'alfador.wowf.transport-marker-receipt.source2',
                'event':'marker-duplicate' if duplicate else 'marker-observed', 'sequence':seq,
                'sent_at_unix_claimed':sent, 'received_at_unix_local':received,
                'monotonic_elapsed_seconds':elapsed, 'poll_id':self.poll_id,
                'batch_id':self.batch_id, 'batch_matching_markers':len(matches),
                'duplicate':duplicate, 'out_of_order':out_of_order,
                'observed_clock_difference_seconds':received-sent, 'clock_skew_measured':False,
                'payload_kind':'test-marker-not-gameplay', 'live_transport_verified':False,
                'game_attested':False})
        return result

    def summary(self):
        return {'schema':'alfador.wowf.transport-marker-status.source2', 'event':'test-ended',
                'ready':self.ready_emitted, 'expected_sequences':list(range(1,9)),
                'received_sequences':sorted(self.seen),
                'missing_sequences':[v for v in range(1,9) if v not in self.seen],
                'unique_marker_receipts':self.receipt_count, 'duplicates':self.duplicate_count,
                'out_of_order':self.out_of_order_count, 'multimarker_poll_batches':self.multimarker_batches,
                'poll_interval_seconds':POLL_SECONDS, 'terminal_reason':self.terminal_reason,
                'observation_window_elapsed_seconds':max(0,time.monotonic()-self.started_monotonic),
                'live_transport_verified':False, 'clock_skew_measured':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--forever-root',required=True)
    parser.add_argument('--session',required=True)
    parser.add_argument('--seconds',type=int,default=45)
    args = parser.parse_args()
    if not 1 <= args.seconds <= 60: parser.error('seconds must be1..60')
    try: reader = MarkerTail(args.forever_root,args.session)
    except (OSError,ValueError) as error:
        code = error.errno if isinstance(error,OSError) and type(error.errno) is int else None
        print(json.dumps({'event':'reader-not-ready','reason':'source-unavailable-or-invalid','os_error_code':code,'live_transport_verified':False}),flush=True)
        return 2
    print(json.dumps(reader.ready_event(),sort_keys=True),flush=True)
    end = time.monotonic() + args.seconds
    try:
        while time.monotonic() < end and not reader.closed:
            for event in reader.poll(): print(json.dumps(event,sort_keys=True),flush=True)
            time.sleep(POLL_SECONDS)
    except (OSError,ValueError):
        reader.terminal_reason = 'reader-measurement-failed'
    finally:
        if not reader.closed: reader.close()
    print(json.dumps(reader.summary(),sort_keys=True),flush=True)
    return 0


if __name__ == '__main__': raise SystemExit(main())
