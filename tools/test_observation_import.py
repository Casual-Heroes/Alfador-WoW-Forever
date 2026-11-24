"""Synthetic offline boundary tests; no game/Core acceptance is implied."""
import copy
import json
import unittest
from datetime import datetime, timezone

from observation_import import InvalidObservation, MAX_BYTES, import_observation, validate_structure


def observed(value):
    return {'status': 'observed', 'value': value}


def fixture():
    return {
        'schema': 'alfador.wow.forever.character-context.draft1',
        'game': 'wow-forever', 'revision': 'synthetic-capture-1',
        'character': {'subject': 'synthetic-player', 'region': 'us'},
        'provenance': {'source': 'wow-addon-api', 'capturedAt': '2026-11-18T12:00:00Z',
                       'retrievedAt': '2026-11-18T12:01:00Z', 'freshness': 'historical',
                       'sourceRevision': 'synthetic-capture-1'},
        'build': {'version': observed('1.60.1'), 'number': observed('70959'), 'interface': observed(1)},
        # Interface=1 is deliberately synthetic, never an installable TOC claim.
        'zone': {'status': 'partial', 'data': {'mapID': {'status': 'unavailable'}, 'name': observed('Synthetic zone')}},
        'summary': {'status': 'observed', 'data': {'name': observed('Synthetic'), 'class': observed('DRUID'), 'level': observed(10)}},
        'talents': {'status': 'partial', 'data': {'configuration': {'status': 'unavailable'}, 'selected': []}},
        'equipment': {'status': 'partial', 'data': {'slots': []}},
    }


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.value = fixture()

    def run_import(self, value=None, raw=None, **kwargs):
        raw = raw if raw is not None else json.dumps(value or self.value).encode()
        return import_observation(raw, subject='synthetic-player', region='us', build='1.60.1',
                                  now=datetime(2026, 11, 18, 12, 2, tzinfo=timezone.utc), **kwargs)

    def reject(self, expected):
        with self.assertRaisesRegex(InvalidObservation, expected):
            self.run_import()

    def test_partial_preserved_without_mutation(self):
        before = copy.deepcopy(self.value)
        value, receipt = self.run_import()
        self.assertEqual(value, before)
        self.assertEqual(receipt['equipmentCoverage'], 'partial')
        self.assertEqual(receipt['coreDelivery'], 'not-attempted')
        self.assertEqual(receipt['sourceAuthentication'], 'not-established')

    def test_unknown_capture_time_stays_unknown(self):
        self.value['provenance']['capturedAt'] = None
        _, receipt = self.run_import()
        self.assertFalse(receipt['captureTimeKnown'])

    def test_old_snapshot_remains_historical(self):
        self.value['provenance']['capturedAt'] = '2020-01-01T00:00:00Z'
        value, _ = self.run_import()
        self.assertEqual(value['provenance']['freshness'], 'historical')

    def test_canonical_hash_independent_of_key_order(self):
        _, left = self.run_import()
        _, right = self.run_import(raw=json.dumps(self.value, sort_keys=True, indent=2).encode())
        self.assertEqual(left['canonicalSha256'], right['canonicalSha256'])
        self.assertNotEqual(left['inputSha256'], right['inputSha256'])

    def test_other_character(self):
        self.value['character']['subject'] = 'someone-else'
        self.reject('character-mismatch')

    def test_other_region(self):
        self.value['character']['region'] = 'eu'
        self.reject('character-mismatch')

    def test_other_game(self):
        self.value['game'] = 'wow-retail'
        self.reject('invalid-constant')

    def test_wrong_build(self):
        self.value['build']['version'] = observed('12.1.5')
        self.reject('build-mismatch')

    def test_missing_interface(self):
        self.value['build']['interface'] = {'status': 'unavailable'}
        self.reject('build-incomplete')

    def test_capture_after_retrieval(self):
        self.value['provenance']['capturedAt'] = '2026-11-18T12:02:00Z'
        self.reject('capture-after-retrieval')

    def test_future_retrieval(self):
        self.value['provenance']['retrievedAt'] = '2026-11-19T00:00:00Z'
        self.reject('future-retrieval')

    def test_invalid_calendar_date(self):
        self.value['provenance']['capturedAt'] = '2026-02-30T00:00:00Z'
        self.reject('invalid-date-time')

    def test_naive_date(self):
        self.value['provenance']['capturedAt'] = '2026-11-18T12:00:00'
        self.reject('invalid-date-time')

    def test_plan_not_observation(self):
        self.value['equipment'] = {'status': 'planned'}
        self.reject('invalid-observation-shape')

    def test_unknown_status_cannot_hide_payload(self):
        self.value['equipment'] = {'status': 'unavailable', 'data': {'slots': []}}
        self.reject('invalid-observation-shape')

    def test_partial_not_complete(self):
        self.value['equipment']['status'] = 'observed'
        self.reject('incomplete-observed-equipment')

    def test_conflicting_talent_ranks(self):
        self.value['talents']['data']['selected'] = [{'id': 1, 'rank': 1}, {'id': 1, 'rank': 2}]
        self.reject('duplicate-talent-id')

    def test_conflicting_slot_observations(self):
        def slot(item):
            return {'slot': 1, 'item': observed(item), 'itemLink': {'status': 'unavailable'},
                    'statsStatus': 'unknown', 'effectsStatus': 'unknown'}
        self.value['equipment']['data']['slots'] = [slot(1), slot(2)]
        self.reject('duplicate-equipment-slot')

    def test_observed_summary_requires_values(self):
        self.value['summary']['data']['level'] = {'status': 'restricted'}
        self.reject('incomplete-observed-summary')

    def test_boolean_not_integer(self):
        self.value['summary']['data']['level'] = observed(True)
        self.reject('invalid-observation-shape')

    def test_arbitrary_fields(self):
        self.value['command'] = 'do-something'
        self.reject('unknown-field')

    def test_input_byte_cap(self):
        with self.assertRaisesRegex(InvalidObservation, 'byte-limit'):
            self.run_import(raw=b' ' * (MAX_BYTES + 1))

    def test_duplicate_json_keys(self):
        with self.assertRaisesRegex(InvalidObservation, 'duplicate-json-key'):
            self.run_import(raw=b'{"game":"wow-forever","game":"wow-retail"}')

    def test_lua_is_not_executed(self):
        with self.assertRaisesRegex(InvalidObservation, 'invalid-json'):
            self.run_import(raw=b'AlfadorProbeReport = { dangerous = os.execute("test") }')

    def test_deep_input(self):
        with self.assertRaisesRegex(InvalidObservation, 'nesting-limit'):
            self.run_import(raw=b'[' * 21 + b'0' + b']' * 21)

    def test_nonfinite_json(self):
        for value in (b'NaN', b'Infinity', b'-Infinity'):
            with self.assertRaisesRegex(InvalidObservation, 'non-finite-number'):
                self.run_import(raw=value)

    def test_invalid_utf8(self):
        with self.assertRaisesRegex(InvalidObservation, 'invalid-json'):
            self.run_import(raw=b'\xff')

    def test_invalid_unicode_escape(self):
        self.value['revision'] = '\ud800'
        self.reject('invalid-unicode')

    def test_structural_unavailable_example(self):
        from observation_import import SCHEMA_PATH
        raw = (SCHEMA_PATH.parent / 'examples' / 'unavailable.json').read_bytes()
        validate_structure(raw)
        with self.assertRaisesRegex(InvalidObservation, 'character-mismatch'):
            self.run_import(raw=raw)


if __name__ == '__main__':
    unittest.main()
