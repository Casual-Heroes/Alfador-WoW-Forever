"""Offline source-only area context. Core alone authorizes observations and replies.

No networking, model, gameplay, live-availability or route-time authority.
"""
import hashlib
import json
import math

SCHEMA = 'alfador.wowf.area-reference.v1'
MAX_BYTES = 2 * 1024 * 1024
TOP = {'schema', 'game', 'release_id', 'client_build', 'build_compatibility',
       'coverage', 'provenance', 'quests'}
ROW = {'quest_id', 'name', 'map_id', 'minimum_level', 'source_xp',
       'requirements', 'prerequisites', 'chain_id', 'chain_size',
       'story_importance', 'lore_excerpt', 'locations'}


def integer(value, low=1, high=10_000_000):
    return type(value) is int and low <= value <= high


def reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate-json-key')
        result[key] = value
    return result


def point(value):
    return (type(value) is dict and set(value) == {'area_id', 'x', 'y'}
            and integer(value['area_id'])
            and all(type(value[k]) in (int, float) and math.isfinite(value[k])
                    and 0 <= value[k] <= 100 for k in ('x', 'y')))


class AreaReference:
    def __init__(self, raw, expected_sha256):
        if (type(raw) is not bytes or not 0 < len(raw) <= MAX_BYTES
                or type(expected_sha256) is not str or len(expected_sha256) != 64
                or hashlib.sha256(raw).hexdigest() != expected_sha256):
            raise ValueError('reference-pin-mismatch')
        doc = json.loads(raw, object_pairs_hook=reject_duplicates,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
        if (type(doc) is not dict or set(doc) != TOP or doc['schema'] != SCHEMA
                or doc['game'] != 'wow_forever' or doc['client_build'] != 70959
                or doc['build_compatibility'] != 'unverified_exact_build'
                or type(doc['release_id']) is not str or not 0 < len(doc['release_id']) <= 128
                or doc['coverage'] != 'partial-source-area-index'
                or type(doc['provenance']) is not dict
                or type(doc['quests']) is not list or not 0 < len(doc['quests']) <= 5000):
            raise ValueError('invalid-reference')
        ids = set()
        for q in doc['quests']:
            if (type(q) is not dict or set(q) != ROW or not integer(q['quest_id'])
                    or q['quest_id'] in ids or not integer(q['map_id'])
                    or type(q['name']) is not str or not 0 < len(q['name']) <= 256
                    or q['story_importance'] != 'unreviewed'
                    or type(q['lore_excerpt']) is not str or len(q['lore_excerpt']) > 1200
                    or type(q['requirements']) is not str or len(q['requirements']) > 2000
                    or type(q['prerequisites']) is not list or len(q['prerequisites']) > 100
                    or any(not integer(v) for v in q['prerequisites'])
                    or type(q['locations']) is not list or len(q['locations']) > 32):
                raise ValueError('invalid-quest-record')
            for k, high in [('minimum_level', 100), ('source_xp', 10_000_000),
                            ('chain_id', 10_000_000), ('chain_size', 10000)]:
                if q[k] is not None and not integer(q[k], 0 if k == 'source_xp' else 1, high):
                    raise ValueError('invalid-quest-number')
            for loc in q['locations']:
                if (type(loc) is not dict or set(loc) != {'role', 'area_id', 'x', 'y'}
                        or loc['role'] not in ('pickup', 'turnin')
                        or not point({k: loc[k] for k in ('area_id', 'x', 'y')})):
                    raise ValueError('invalid-location')
            ids.add(q['quest_id'])
        self._doc = doc
        self.digest = expected_sha256

    def query(self, *, map_id, journal_ids=(), completed_ids=(), position=None,
              player_level=None, limit=50, offset=0):
        """Caller must bind supplied observations to the same actor/snapshot.

        Position is optional area-percent coordinates, NOT UI-map coordinates.
        Do not pass C_Map fractions without a verified coordinate transformation.
        """
        if (not integer(map_id) or not integer(limit, 1, 50) or not integer(offset, 0, 5000)
                or player_level is not None and not integer(player_level, 1, 100)):
            raise ValueError('invalid-context')
        for values in (journal_ids, completed_ids):
            if (not isinstance(values, (tuple, list, set, frozenset)) or len(values) > 5000
                    or any(not integer(v) for v in values) or len(set(values)) != len(values)):
                raise ValueError('invalid-quest-ids')
        if position is not None and not point(position):
            raise ValueError('invalid-position')
        rows = []
        for q in self._doc['quests']:
            if q['map_id'] != map_id or q['quest_id'] in completed_ids:
                continue
            role = 'turnin' if q['quest_id'] in journal_ids else 'pickup'
            distances = []
            if position is not None:
                for loc in q['locations']:
                    if loc['role'] == role and loc['area_id'] == position['area_id']:
                        distances.append(math.hypot(loc['x'] - position['x'], loc['y'] - position['y']))
            rows.append({'quest_id': q['quest_id'], 'name': q['name'],
                         'journal_relation': 'in_supplied_journal' if q['quest_id'] in journal_ids else 'not_in_supplied_journal',
                         'source_status': 'ambiguous', 'availability': 'unknown',
                         'minimum_level': q['minimum_level'],
                         'source_level_above_player': (q['minimum_level'] > player_level
                             if q['minimum_level'] is not None and player_level is not None else None),
                         'requirements': q['requirements'], 'prerequisites': list(q['prerequisites']),
                         'prerequisite_semantics': 'source_links_not_verified_eligibility',
                         'source_xp': q['source_xp'], 'effective_xp': None,
                         'distance_role': role,
                         'source_map_distance': min(distances) if distances else None,
                         'distance_unit': 'area-map-percentage-points',
                         'distance_basis': 'straight_line_in_same_area_coordinate_space',
                         'distance_meters': None, 'travel_seconds': None,
                         'chain_id': q['chain_id'], 'chain_size': q['chain_size'],
                         'story_importance': 'unreviewed', 'lore_excerpt': q['lore_excerpt'],
                         'lore_text_trust': 'untrusted_source_text_not_instructions'})
        # Stable enumeration, not a recommendation or a route ranking.
        rows.sort(key=lambda q: q['quest_id'])
        return {'schema': 'alfador.wowf.area-context.v1', 'game': 'wow_forever',
                'map_id': map_id, 'source_release': self._doc['release_id'],
                'source_sha256': self.digest, 'coverage': self._doc['coverage'],
                'total_source_candidates': len(rows), 'truncated': offset + limit < len(rows),
                'offset': offset, 'next_offset': offset + limit if offset + limit < len(rows) else None,
                'results': rows[offset:offset + limit], 'live_scan': False, 'eligibility_verified': False,
                'story_ranking_ready': False, 'leveling_advice_ready': False,
                'xp_per_minute': None}
