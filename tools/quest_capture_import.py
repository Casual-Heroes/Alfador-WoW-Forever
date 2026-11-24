"""Read-only local check of raw quest-pilot JSON; no session or Core delivery."""
import argparse
import hashlib
import json
from pathlib import Path

from observation_import import InvalidObservation, MAX_BYTES, _schema, decode_bounded_json, require


def validate_capture(raw):
    value = decode_bounded_json(raw)
    require(type(value) is dict, 'capture-must-be-object')
    schemas = {'alfador.wow.forever.quest-pilot.capture.draft1': 'quest-pilot-capture.schema.json',
               'alfador.wow.forever.quest-pilot.capture.draft2': 'quest-pilot-capture-v2.schema.json',
               'alfador.wow.forever.quest-pilot.capture.draft3': 'quest-pilot-capture-v3.schema.json',
               'alfador.wow.forever.quest-pilot.capture.draft4': 'quest-pilot-capture-v4.schema.json'}
    require(type(value.get('schema')) is str and value['schema'] in schemas, 'unsupported-capture-schema')
    schema_path = Path(__file__).resolve().parents[1] / 'contracts' / schemas[value['schema']]
    _schema(value, json.loads(schema_path.read_text(encoding='utf-8')))
    expected = {'version': '1.60.1', 'number': '70959', 'interface': 16001}
    require(all(value['build'][key] == {'status': 'observed', 'value': item}
                for key, item in expected.items()), 'unsupported-pilot-build')
    ids = []
    observed_xp = 0
    diagnostics = {}
    for quest in value['quests']:
        require(quest['questId']['status'] == 'observed' and quest['questId']['value'] > 0,
                'quest-id-unavailable')
        require(quest['onMap'] == {'status': 'observed', 'value': True}, 'not-an-on-map-candidate')
        ids.append(quest['questId']['value'])
        if not value['schema'].endswith('draft1'):
            if quest['rewardXP']['status'] == 'observed':
                context = quest['rewardXPContext']
                require(context['status'] == 'observed', 'xp-context-required')
                context = context['value']
                require(context['questId'] == quest['questId']['value'], 'xp-quest-mismatch')
                require(value['player']['guid']['status'] == 'observed' and value['player']['guid']['value'] != '',
                        'xp-player-context-unavailable')
                require(value['player']['level'] == {'status': 'observed', 'value': context['playerLevel']}, 'xp-level-mismatch')
                require(value['capturedAtUnix'] == {'status': 'observed', 'value': context['capturedAtUnix']}, 'xp-time-mismatch')
                observed_xp += 1
            else:
                require(quest['rewardXPContext']['status'] == 'unavailable', 'xp-context-without-amount')
        if 'selectedQuestAtCapture' in value:
            reason = quest['rewardXPRead']
            diagnostics[reason] = diagnostics.get(reason, 0) + 1
            require((reason == 'observed') == (quest['rewardXP']['status'] == 'observed'), 'xp-diagnostic-mismatch')
            if reason == 'observed':
                require(value['selectedQuestAtCapture'] == quest['questId'], 'xp-selection-mismatch')
    require(len(ids) == len(set(ids)), 'duplicate-quest-id')
    require(observed_xp <= 1, 'multiple-selected-quest-xp-observations')
    return value, {'result': 'locally-validated-untrusted-historical-quest-capture',
                   'inputSha256': hashlib.sha256(raw).hexdigest(),
                   'candidateCount': len(ids), 'unresolvedLogEntries': value['unresolvedLogEntries'],
                   'eligibility': 'not-established', 'xpAndTiming': 'selected-quest-xp-observed;timing-unavailable' if observed_xp else 'unavailable',
                   'xpAmountsObserved': observed_xp, 'xpUIVerification': 'not-established',
                   'xpReadDiagnostics': diagnostics,
                   'sessionVerification': 'not-established', 'coreDelivery': 'not-attempted'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        with args.input.open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
        _, receipt = validate_capture(raw)
        print(json.dumps(receipt, indent=2))
    except (InvalidObservation, OSError) as error:
        print(json.dumps({'result': 'rejected', 'reason': str(error) if isinstance(error, InvalidObservation) else 'input-unreadable'}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
