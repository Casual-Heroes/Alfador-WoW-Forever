"""Offline developer compiler for a pre-reviewed pinned Forever source snapshot.

Not a Desktop file-import feature. No networking or imported Lua execution.
"""
import hashlib
import json
from pathlib import Path
import sys


def compile_reference(snapshot, output):
    snapshot = Path(snapshot)
    provenance = json.loads((snapshot / 'provenance.json').read_bytes())
    documents = {}
    for name, pin in provenance['pins'].items():
        if not name.startswith('/data/') or '..' in name or len(name) > 100:
            raise ValueError('invalid-source-member')
        path = snapshot / name.replace('/', '_').lstrip('_')
        raw = path.read_bytes()
        if len(raw) > 4_000_000 or hashlib.sha256(raw).hexdigest() != pin:
            raise ValueError('source-pin-mismatch')
        documents[name] = json.loads(raw)
    rows = []
    def clean(value, size):
        return str(value or '').replace('$B', '\n').strip()[:size]
    def ident(value):
        return type(value) is int and value > 0
    # Caller snapshots explicitly enumerate selected areas; never claim full catalog.
    for name, shard in documents.items():
        if not name.startswith('/data/forever/quest/'):
            continue
        for record in shard.values():
            if record.get('uiMapId') != 1426:
                continue
            points = []
            for field, role in [('startedBy', 'pickup'), ('finishedBy', 'turnin')]:
                for ref in record.get(field, []):
                    key = str(ref.get('t')) + ':' + str(ref.get('id'))
                    for area, xy_list in record.get('spawns', {}).get(key, {}).get('spawns', {}).items():
                        for xy in xy_list:
                            if len(xy) == 2 and all(type(v) in (int, float) and 0 <= v <= 100 for v in xy):
                                points.append({'role': role, 'area_id': int(area), 'x': xy[0], 'y': xy[1]})
            pres = []
            for kind in ['preSingle', 'preGroup']:
                for ref in record.get('chain', {}).get(kind, []):
                    if ident(ref.get('id')) and ref['id'] not in pres:
                        pres.append(ref['id'])
            requirements = {k: record[k] for k in ['reqLevel', 'maxLevel', 'side', 'races', 'classes',
                            'requiredSkill', 'requiredMinRep', 'requiredMaxRep'] if k in record}
            rows.append({'quest_id': record['id'], 'name': clean(record['name'], 256),
                         'map_id': record['uiMapId'], 'minimum_level': record.get('reqLevel'),
                         'source_xp': record.get('rewards', {}).get('xp'),
                         'requirements': json.dumps(requirements, sort_keys=True, separators=(',', ':')),
                         'prerequisites': pres, 'chain_id': record.get('questline', {}).get('id'),
                         'chain_size': record.get('questline', {}).get('size'),
                         'story_importance': 'unreviewed', 'lore_excerpt': clean(record.get('details'), 1200),
                         'locations': points[:32]})
    provenance.update({'repository': 'https://github.com/Stein-N/WoW-Quest-Database',
        'repository_code_reference': '8153cf7536636208c91bc88e34082d1dc1bdeac0',
        'repository_pin_does_not_pin_hosted_data': True, 'code_license': 'GPL-3.0',
        'captured_client_date': '2026-11-19', 'exact_build_authority': False,
        'provider_timestamp_is_not_build_attestation': True})
    doc = {'schema': 'alfador.wowf.area-reference.v1', 'game': 'wow_forever',
        'release_id': 'wowf-dun-morogh-area-source-20261119-01', 'client_build': 70959,
        'build_compatibility': 'unverified_exact_build', 'coverage': 'partial-source-area-index',
        'provenance': provenance, 'quests': sorted(rows, key=lambda q: q['quest_id'])}
    raw = (json.dumps(doc, indent=2, ensure_ascii=True) + '\n').encode()
    Path(output).write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: build_area_reference.py <pinned-snapshot-dir> <new-json-output>')
    if Path(sys.argv[2]).exists():
        raise SystemExit('Refusing to overwrite existing output')
    print(compile_reference(sys.argv[1], sys.argv[2]))
