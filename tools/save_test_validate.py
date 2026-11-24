"""Read-only fixed SavedVariables decoder; never executes Lua or uploads data."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from observation_import import InvalidObservation, decode_bounded_json, require
MAX_SAVED = 4096
KEYS = {'schema','version','build','interface','boundary','sequence','capturedAtUnix','freshness','payloadKind'}
def validate_saved(raw):
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SAVED, 'saved-byte-limit')
    match = re.fullmatch(rb'\s*AlfadorWowSaveTestEvidence\s*=\s*"([0-9a-f]+)"\s*',raw)
    require(match is not None, 'not-fixed-save-marker')
    hexed = match.group(1)
    require(len(hexed) % 2 == 0,'odd-hex')
    doc = decode_bounded_json(bytes.fromhex(hexed.decode('ascii')))
    require(type(doc) is dict and set(doc) == KEYS,'wrong-marker-fields')
    for key, value in [('schema','alfador.wowf.save-test.v1'),('version','1.60.1'),('build','71037'),('freshness','historical'),('payloadKind','synthetic-save-marker')]:
        require(type(doc[key]) is str and doc[key] == value,'wrong-marker-constant')
    require(type(doc['interface']) is int and doc['interface'] == 16001,'wrong-interface')
    require(type(doc['boundary']) is str and re.fullmatch('[a-f0-9]{32}',doc['boundary']) is not None,'wrong-boundary')
    require(type(doc['sequence']) is int and 1 <= doc['sequence'] <= 1000,'wrong-sequence')
    require(type(doc['capturedAtUnix']) is int and 1 <= doc['capturedAtUnix'] <= 9999999999,'wrong-timestamp')
    return doc, {'result':'validated-untrusted-historical-save-marker','boundary':doc['boundary'],'sequence':doc['sequence'],'capturedAtUnix':doc['capturedAtUnix'],'inputSha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'live_delivery_verified':False,'core_delivery':'not-attempted'}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    args=parser.parse_args()
    try:
        with args.input.open('rb') as stream:raw=stream.read(MAX_SAVED+1)
        _, receipt=validate_saved(raw)
    except (InvalidObservation,OSError):
        print(json.dumps({'result':'unavailable-or-rejected','live_delivery_verified':False}));return 1
    print(json.dumps(receipt,sort_keys=True));return 0
if __name__ == '__main__':raise SystemExit(main())
