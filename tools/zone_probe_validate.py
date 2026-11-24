"""Fixed developer evidence decoder: no Lua execution, watcher, network or live claim."""
import json
from pathlib import Path
import re
import sys
from observation_import import InvalidObservation, _schema, decode_bounded_json, require

ROOT = Path(__file__).resolve().parents[1]
MAX_JSON = 65536
MAX_SAVED = 140000


def decode_saved_hex(raw):
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SAVED, 'saved-byte-limit')
    match = re.fullmatch(rb'\s*AlfadorZoneTestEvidence\s*=\s*"([0-9a-f]+)"\s*', raw)
    require(match is not None, 'not-fixed-saved-data')
    encoded = match.group(1)
    require(len(encoded) % 2 == 0 and len(encoded) <= MAX_JSON * 2, 'saved-hex-limit')
    return bytes.fromhex(encoded.decode('ascii'))


def validate(raw):
    require(type(raw) is bytes and 0 < len(raw) <= MAX_JSON, 'json-byte-limit')
    doc = decode_bounded_json(raw)
    schema = json.loads((ROOT / 'contracts/zone-probe-sample.draft1.schema.json').read_bytes())
    _schema(doc, schema)
    require(len(doc['samples']) > 0, 'empty-samples')
    previous = 0
    for row in doc['samples']:
        require(re.fullmatch('[a-f0-9]{32}', row['boundary']) is not None, 'invalid-boundary')
        require(row['sequence'] > previous, 'sequence-regression')
        previous = row['sequence']
        fields = row['fields']
        if row['state'] == 'in_world':
            require(row['reason'] == 'sampled' and row['buildCheck'] == 'matched-at-sample', 'bad-world-claim')
            require(fields['inWorld'] == {'status': 'observed', 'value': True}, 'world-signal-missing')
            require(fields['mapId']['status'] == fields['zoneName']['status'] == 'observed', 'zone-facts-missing')
            for key, value in [('version','1.60.1'),('build','70959'),('interface',16001)]:
                require(row['observedClient'][key] == {'status':'observed','value':value}, 'build-mismatch')
            require(row['capturedAtUnix']['status'] == row['sampleEndUnix']['status'] == 'observed', 'time-missing')
            delta = row['sampleEndUnix']['value'] - row['capturedAtUnix']['value']
            require(0 <= delta <= 1, 'sample-window-invalid')
        else:
            require(row['reason'] != 'sampled', 'bad-unavailable-reason')
            require(all(v == {'status':'unavailable'} for v in fields.values()), 'stale-unavailable-data')
    latest = doc['samples'][-1]
    return doc, {'schema':'alfador.wowf.zone-probe.review-receipt.draft1',
                 'samples_checked':len(doc['samples']), 'latest_state':latest['state'],
                 'latest_sequence':latest['sequence'], 'freshness':'historical',
                 'live_desktop_delivery_verified':False, 'game_attested':False}


if __name__ == '__main__':
    if len(sys.argv) not in (2,3) or len(sys.argv) == 3 and sys.argv[2] != '--saved-hex':
        raise SystemExit('Usage: zone_probe_validate.py <local-evidence-file> [--saved-hex]')
    maximum = MAX_SAVED if len(sys.argv) == 3 else MAX_JSON
    with Path(sys.argv[1]).open('rb') as stream: raw = stream.read(maximum + 1)
    if len(sys.argv) == 3: raw = decode_saved_hex(raw)
    _, receipt = validate(raw)
    print(json.dumps(receipt, sort_keys=True))
