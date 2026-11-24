"""Bounded, offline import of the draft Forever JSON contract. No Lua/network."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

MAX_BYTES = 256 * 1024
SCHEMA_PATH = Path(__file__).resolve().parents[1] / 'contracts' / 'character-context.schema.json'


class InvalidObservation(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise InvalidObservation(reason)


def timestamp(value):
    require(isinstance(value, str) and re.fullmatch(
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', value),
        'invalid-date-time')
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise InvalidObservation('invalid-date-time') from None


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate-json-key')
        result[key] = value
    return result


def _depth(raw):
    # Check before json.loads so nesting cannot exhaust the parser stack.
    depth = 0
    quoted = escaped = False
    for char in raw:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1
            require(depth <= 20, 'nesting-limit')
        elif char in ']}':
            depth -= 1


def _reject_constant(_):
    raise InvalidObservation('non-finite-number')


def _schema(value, rule, location='$'):
    """Validate only the schema features used by the bundled fixed contract.

    Reject unsupported keywords so future schema edits cannot silently skip rules.
    This is not a public JSON Schema evaluator and accepts no imported schemas.
    """
    supported = {'$schema', 'title', 'description', 'type', 'properties', 'required',
                 'additionalProperties', 'oneOf', 'const', 'enum', 'minLength',
                 'maxLength', 'minimum', 'maximum', 'maxItems', 'items',
                 'uniqueItems', 'format'}
    require(not set(rule) - supported, 'unsupported-bundled-schema-keyword')
    if 'oneOf' in rule:
        matches = 0
        for branch in rule['oneOf']:
            try:
                _schema(value, branch, location)
                matches += 1
            except InvalidObservation:
                pass
        require(matches == 1, location + ':invalid-observation-shape')
    if 'const' in rule:
        require(type(value) is type(rule['const']) and value == rule['const'], location + ':invalid-constant')
    if 'enum' in rule:
        require(any(type(value) is type(item) and value == item for item in rule['enum']), location + ':invalid-enum')
    if 'type' in rule:
        kinds = rule['type'] if isinstance(rule['type'], list) else [rule['type']]
        checks = {'object': type(value) is dict, 'array': type(value) is list,
                  'string': type(value) is str, 'integer': type(value) is int,
                  'null': value is None, 'boolean': type(value) is bool}
        require(all(kind in checks for kind in kinds), 'unsupported-bundled-schema-type')
        require(any(checks[kind] for kind in kinds), location + ':invalid-type')
    if type(value) is dict:
        properties = rule.get('properties', {})
        require(all(key in value for key in rule.get('required', [])), location + ':missing-field')
        if rule.get('additionalProperties') is False:
            require(not set(value) - set(properties), location + ':unknown-field')
        for key, item in value.items():
            if key in properties:
                _schema(item, properties[key], location + '.' + key)
    elif type(value) is list:
        require(len(value) <= rule.get('maxItems', MAX_BYTES), location + ':array-limit')
        if rule.get('uniqueItems'):
            keys = [json.dumps(item, sort_keys=True, ensure_ascii=True) for item in value]
            require(len(keys) == len(set(keys)), location + ':duplicate-entry')
        for item in value:
            _schema(item, rule.get('items', {}), location + '[]')
    elif type(value) is str:
        require(rule.get('minLength', 0) <= len(value) <= rule.get('maxLength', MAX_BYTES), location + ':string-limit')
        require(not any(0xD800 <= ord(c) <= 0xDFFF for c in value), location + ':invalid-unicode')
        if rule.get('format') == 'date-time':
            timestamp(value)
    elif type(value) in (int, float):
        require(type(value) is int or math.isfinite(value), 'non-finite-number')
        require(rule.get('minimum', -math.inf) <= value <= rule.get('maximum', math.inf), location + ':number-range')


def decode_bounded_json(raw):
    require(type(raw) is bytes and len(raw) <= MAX_BYTES, 'byte-limit')
    try:
        text = raw.decode('utf-8', errors='strict')
        _depth(text)
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        if isinstance(error, InvalidObservation):
            raise
        raise InvalidObservation('invalid-json') from None
    return value


def validate_structure(raw):
    value = decode_bounded_json(raw)
    schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
    _schema(value, schema)
    return value


def import_observation(raw, *, subject, region, build, now=None):
    """Return a locally checked historical document and receipt, never Core proof.

    Expected identity/build are caller-supplied comparisons, not authentication.
    The receiving Core must separately authenticate and bind the source/character.
    """
    value = validate_structure(raw)
    require(value['character'] == {'subject': subject, 'region': region}, 'character-mismatch')
    require(region != 'unknown', 'region-unverified')
    require(value['build']['version'] == {'status': 'observed', 'value': build}, 'build-mismatch-or-unavailable')
    require(value['build']['number']['status'] == 'observed' and
            value['build']['interface']['status'] == 'observed', 'build-incomplete')
    current = now or datetime.now(timezone.utc)
    require(current.tzinfo is not None, 'clock-must-be-timezone-aware')
    provenance = value['provenance']
    retrieved = timestamp(provenance['retrievedAt'])
    captured = timestamp(provenance['capturedAt']) if provenance['capturedAt'] is not None else None
    require(retrieved <= current + timedelta(seconds=120), 'future-retrieval')
    if captured is not None:
        require(captured <= retrieved, 'capture-after-retrieval')
    equipment = value['equipment']
    if 'data' in equipment:
        slots = equipment['data']['slots']
        slot_ids = [slot['slot'] for slot in slots]
        require(len(slot_ids) == len(set(slot_ids)), 'duplicate-equipment-slot')
        if equipment['status'] == 'observed':
            require(set(slot_ids) == set(range(1, 20)), 'incomplete-observed-equipment')
            require(all(slot['item']['status'] == 'observed' for slot in slots), 'unknown-observed-equipment-slot')
    talents = value['talents']
    if 'data' in talents:
        selected = talents['data']['selected']
        ids = [talent['id'] for talent in selected]
        require(len(ids) == len(set(ids)), 'duplicate-talent-id')
        if talents['status'] == 'observed':
            require(talents['data']['configuration']['status'] == 'observed', 'talent-configuration-unavailable')
    for section in ('zone', 'summary'):
        if value[section]['status'] == 'observed':
            require(all(item['status'] == 'observed' for item in value[section]['data'].values()),
                    'incomplete-observed-' + section)
    canonical = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')
    receipt = {
        'result': 'locally-validated-historical-snapshot',
        'revision': value['revision'],
        'inputSha256': hashlib.sha256(raw).hexdigest(),
        'canonicalSha256': hashlib.sha256(canonical).hexdigest(),
        'coreDelivery': 'not-attempted',
        'sourceAuthentication': 'not-established',
        'captureTimeKnown': captured is not None,
        'equipmentCoverage': equipment['status'],
        'talentCoverage': talents['status'],
        'recommendationReadiness': 'not-established',
    }
    return value, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Explicit JSON export; never a Lua file')
    parser.add_argument('--subject', required=True)
    parser.add_argument('--region', choices=['us', 'eu', 'kr', 'tw', 'cn'], required=True)
    parser.add_argument('--build', required=True, help='Expected observed version, e.g. 1.60.1')
    args = parser.parse_args()
    try:
        with args.input.open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
        _, receipt = import_observation(raw, subject=args.subject, region=args.region, build=args.build)
        print(json.dumps(receipt, indent=2))
    except (InvalidObservation, OSError) as error:
        # Avoid logging imported values, private file paths or file contents.
        reason = str(error) if isinstance(error, InvalidObservation) else 'input-unreadable'
        print(json.dumps({'result': 'rejected', 'reason': reason}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
