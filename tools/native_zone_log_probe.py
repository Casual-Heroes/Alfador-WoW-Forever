"""Read only new zone metadata from one native WoW combat log for a local test."""
import argparse
import json
import os
from pathlib import Path
import re
import time

from transfer_marker_tail import shared_read

ZONE = re.compile(
    rb'(?P<stamp>[0-9/ :.+-]{12,48})  (?P<event>ZONE_CHANGE|MAP_CHANGE),'
    rb'(?P<id>[0-9]{1,9}),"(?P<name>[^"\x00-\x1f]{1,128})"(?:,.*)?'
)


def zone_record(line):
    match = ZONE.fullmatch(line.rstrip(b'\r'))
    if match is None:
        return None
    return {
        'event': match['event'].decode('ascii'),
        'log_id': int(match['id']),
        'zone': match['name'].decode('utf-8', errors='replace'),
        'logged_at': match['stamp'].decode('ascii').strip(),
    }


def watch(path, duration_seconds=90):
    with shared_read(path) as stream:
        identity = os.fstat(stream.fileno())
        stream.seek(0, 2)
        start = time.monotonic()
        pending = b''
        discarding_partial = False
        if stream.tell():
            stream.seek(-1, 2)
            discarding_partial = stream.read(1) != b'\n'
        print('READY: watching only new zone metadata', flush=True)
        while duration_seconds is None or time.monotonic() - start < duration_seconds:
            disk = path.stat()
            if not os.path.samestat(identity, disk) or disk.st_size < stream.tell():
                raise ValueError('log changed or truncated')
            if duration_seconds is not None and disk.st_size - stream.tell() > 65536:
                raise ValueError('read limit reached')
            chunk = stream.read(65536)
            if discarding_partial:
                _, separator, chunk = chunk.partition(b'\n')
                discarding_partial = not separator
            lines = (pending + chunk).split(b'\n')
            pending = lines.pop()
            if len(pending) > 4096:
                raise ValueError('line limit reached')
            for line in lines:
                record = zone_record(line) if len(line) <= 4096 else None
                if record is not None:
                    record['elapsed_seconds'] = round(time.monotonic() - start, 3)
                    print(json.dumps(record), flush=True)
            time.sleep(0.25)
        print('DONE', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('forever_root', type=Path)
    parser.add_argument('--until-stopped', action='store_true',
                        help='keep watching until interrupted')
    args = parser.parse_args()
    try:
        root = args.forever_root.resolve(strict=True)
        logs = root / 'Logs'
        if root.name.lower() != '_forever_' or logs.resolve(strict=True) != logs:
            raise ValueError('unexpected log directory')
        files = [
            path for path in logs.glob('WoWCombatLog*.txt')
            if path.is_file() and path.resolve(strict=True) == path
        ]
        if not files:
            print('NO FILE: WoW has not created a combat log', flush=True)
            return 2
        duration = None if args.until_stopped else 90
        watch(max(files, key=lambda path: path.stat().st_mtime_ns), duration)
    except KeyboardInterrupt:
        print('STOPPED', flush=True)
    except (OSError, ValueError):
        print('STOP: log unavailable, changed, or exceeded probe bounds', flush=True)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
