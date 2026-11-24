import hashlib
import json
from dataclasses import replace
from pathlib import Path
import unittest

from quest_decision import JournalStop, Observation, Pickup, Point, QuestMeasurement, Weapon, decide_pickup, render_pickup_advice
from quest_pilot import Timing


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'reference_data' / 'polestar-forever-db-2026.11.1'
SPACE = 'dun-morogh-verified-test-world-yards'


def point(x, y):
    return Point(1426, SPACE, x, y)


class QuestDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = json.loads((SOURCE / 'datapackage.json').read_bytes())
        resources = {row['name']: row for row in manifest['resources']}

        def read(table):
            resource = resources[table]
            raw = (SOURCE / resource['path']).read_bytes()
            if f'sha256:{hashlib.sha256(raw).hexdigest()}' != resource['hash']:
                raise ValueError(f'Pinned Polestar table changed: {table}')
            return list(map(json.loads, raw.splitlines()))

        quest = next(row for row in read('quest') if row['id'] == 320)
        starter = next(row for row in read('quest_start') if row['quest'] == 320)
        ending = next(row for row in read('quest_end') if row['quest'] == 320)
        names = {row['id']: row.get('name') for row in read('npc')}
        frame = next(row for row in read('ui_map') if row['ui_map'] == 1426)

        def map_point(x, y):
            coords = (round(100 * (y - frame['left']) / (frame['right'] - frame['left']), 1),
                      round(100 * (x - frame['top']) / (frame['bottom'] - frame['top']), 1))
            return replace(point(x, y), map_percent=coords)

        spawn_rows = read('spawn')
        spawns = {row['id']: map_point(row['x'], row['y']) for row in spawn_rows
                  if row['kind'] == 'npc' and row['map'] == frame['map']
                  and row['id'] in {starter['id'], ending['id']}}
        rewards = {row['id'] for row in read('quest_reward') if row['quest'] == 320 and row['kind'] == 'choice'}
        weapons = tuple(Weapon(row['name'], 'main hand', 2 if row['id'] == 1010 else 1)
                        for row in read('item') if row['id'] in rewards)
        chain = tuple(row['pre'] for row in read('quest_prereq') if row['quest'] == 320)
        cls.quest = Pickup(320, quest['title'], names[starter['id']], spawns[starter['id']], quest['xp'],
                           'Polestar 2026.11.1', '71037', spawns[ending['id']], names[ending['id']],
                           True, quest['min_level'], 'Alliance', chain, weapons=weapons)
        # The nearby Stout objective is a fixture for live progress, using the
        # mapped source discussed in the evidence note, not an observed journal.
        stout = next(row for row in read('quest_objective') if row['quest'] == 315 and row['kind'] == 'item')
        source = next(row for row in read('item_source')
                      if row['item'] == stout['target'] and row['kind'] == 'npc' and row['id'] == 1397)
        spawn = next(row for row in spawn_rows
                     if row['kind'] == 'npc' and row['id'] == source['id'] and row['map'] == frame['map'])
        cls.stop = JournalStop(315, 'The Perfect Stout', map_point(spawn['x'], spawn['y']), True)
        cls.observation = Observation('synthetic-actor', 'synthetic-paladin', '71037', 100, cls.quest.pickup,
                                      9, 'Alliance', frozenset({(320, cls.quest.giver)}), frozenset({315}),
                                      frozenset({319}), (cls.stop,))

    def decide(self, obs=None, quests=None, **options):
        scope = {'actor': 'synthetic-actor', 'character': 'synthetic-paladin', 'build': '71037', 'now': 106}
        return decide_pickup(tuple(quests if quests is not None else (self.quest,)),
                             obs or self.observation, **(scope | options))

    def test_rejold_delivery_uses_offers_listed_xp_and_an_unfinished_detour(self):
        result = self.decide()['recommendation']
        self.assertEqual(result['instruction'], 'pick up')
        self.assertEqual(result['quest'], 'Return to Bellowfiz')
        self.assertEqual(result['quest_giver'], 'Rejold Barleybrew')
        self.assertEqual(result['turnin_giver'], 'Pilot Bellowfiz')
        self.assertEqual(result['listed_xp'], 875)
        self.assertEqual(result['pickup_yards_straight_line'], 0)
        self.assertEqual(result['delivery_yards_straight_line'], 952)
        self.assertEqual(result['turnin_map_percent'], (49.4, 48.4))
        self.assertEqual(result['chain_from_ids'], [319])
        self.assertEqual(result['possible_stops'][0]['quest_id'], 315)
        self.assertEqual(result['possible_stops'][0]['off_direct_line_yards'], 56)
        self.assertIsNone(result['completion_time_seconds'])
        self.assertIsNone(result['xp_per_minute'])
        self.assertEqual({item['name'] for item in result['weapon_choices']},
                         {'Sharp Axe', 'Gnarled Short Staff', 'Camping Knife'})
        self.assertTrue(all(item['weapon_dps_delta'] is None for item in result['weapon_choices']))

    def test_unfinished_journal_and_matching_npc_evidence_are_required(self):
        observation = replace(self.observation, offers=frozenset({(320, 'Other NPC')}),
                              journal_stops=(replace(self.stop, unfinished=False),))
        result = self.decide(observation)['recommendation']
        self.assertEqual(result['instruction'], 'check with quest giver')
        self.assertEqual(result['possible_stops'], [])

    def test_wrong_actor_character_build_and_stale_observation_are_rejected(self):
        for override in ({'actor': 'other'}, {'character': 'other'}, {'build': '70959'}, {'now': 116}, {'now': 99}):
            with self.subTest(override=override):
                self.assertEqual(self.decide(**override)['status'], 'current observation unavailable')

    def test_gates_front_and_backtrack_and_coordinates(self):
        for observation in (replace(self.observation, active=frozenset({320})),
                            replace(self.observation, completed=frozenset({319, 320})),
                            replace(self.observation, position=replace(self.quest.pickup, space='other floor'))):
            with self.subTest(observation=observation):
                self.assertIsNone(self.decide(observation)['recommendation'])
        behind = replace(self.stop, point=point(self.quest.pickup.x, self.quest.pickup.y + 30))
        self.assertEqual(self.decide(replace(self.observation, journal_stops=(behind,)))['recommendation']['possible_stops'], [])

    def test_weapon_delta_needs_known_usable_comparable_weapons(self):
        equipped = Weapon('Synthetic equipped axe', 'main hand', 1, 3.0)
        rewards = (Weapon('Synthetic faster axe', 'main hand', 1, 4.5, True),
                   Weapon('Synthetic staff', 'main hand', 2, 9.0, True),
                   Weapon('Synthetic unidentified proficiency', 'main hand', 1, 10.0))
        result = self.decide(replace(self.observation, equipped_weapon=equipped),
                             [replace(self.quest, weapons=rewards)], focus='weapon')['recommendation']
        self.assertEqual([choice['weapon_dps_delta'] for choice in result['weapon_choices']], [1.5, None, None])

    def test_focus_and_confirmed_offers_affect_ranking(self):
        leveling = replace(self.quest, quest_id=501, name='Leveling', listed_xp=500, follow_up_to=(), delivery=False)
        story = replace(leveling, quest_id=502, name='Story', listed_xp=100, story='Continues the local story.')
        observation = replace(self.observation, offers=frozenset())
        self.assertEqual(self.decide(observation, [story, leveling])['recommendation']['quest_id'], 501)
        self.assertEqual(self.decide(observation, [story, leveling], focus='story')['recommendation']['quest_id'], 502)
        observed_offer = replace(observation, offers=frozenset({(501, leveling.giver)}))
        self.assertEqual(self.decide(observed_offer, [story, leveling], focus='story')['recommendation']['quest_id'], 501)

    def test_player_position_changes_rank_for_comparable_leveling_leads(self):
        first = replace(self.quest, quest_id=501, listed_xp=500, delivery=False, follow_up_to=())
        other = replace(first, quest_id=502, pickup=point(first.pickup.x + 700, first.pickup.y))
        nearby_first = replace(self.observation, offers=frozenset())
        nearby_other = replace(nearby_first, position=other.pickup)
        self.assertEqual(self.decide(nearby_first, [first, other])['recommendation']['quest_id'], 501)
        self.assertEqual(self.decide(nearby_other, [first, other])['recommendation']['quest_id'], 502)

    def test_time_budget_and_xp_rate_use_verified_remaining_time_and_effective_xp(self):
        quick = replace(self.quest, quest_id=501, listed_xp=500, follow_up_to=())
        slow = replace(quick, quest_id=502, listed_xp=1000)
        near = QuestMeasurement(501, Timing(60, 90, 30, 'timed test route', 'r1'), 450, 'test reward UI')
        far = QuestMeasurement(502, Timing(120, 300, 60, 'timed test route', 'r1'), 900, 'test reward UI')
        obs = replace(self.observation, offers=frozenset(), progress_revision='r1', measurements=(near, far))
        result = self.decide(obs, [slow, quick], budget_seconds=300)
        best = result['recommendation']
        self.assertEqual(best['quest_id'], 501)
        self.assertEqual(best['travel_time_seconds'], 60)
        self.assertEqual(best['completion_time_seconds'], 180)
        self.assertEqual(best['xp_per_minute'], 150)
        self.assertTrue(best['fits_time_budget'])
        self.assertEqual(self.decide(obs, [slow, quick], budget_seconds=100)['status'],
                         'no estimated pickup fits the time budget')

    def test_partial_and_old_timing_cannot_become_a_rate_or_budget_claim(self):
        measurement = QuestMeasurement(320, Timing(45, None, 5, 'test travel estimate', 'r1'), 850, 'test reward UI')
        obs = replace(self.observation, progress_revision='r1', measurements=(measurement,))
        result = self.decide(obs, focus='nearby', budget_seconds=1200)
        self.assertEqual(result['timing_coverage'], 'partial')
        self.assertEqual(result['recommendation']['travel_time_seconds'], 45)
        self.assertIsNone(result['recommendation']['xp_per_minute'])
        self.assertIsNone(result['recommendation']['fits_time_budget'])
        old = self.decide(replace(obs, progress_revision='r2'), focus='nearby')['recommendation']
        self.assertIsNone(old['effective_xp'])
        self.assertIsNone(old['travel_time_seconds'])
        self.assertEqual(old['comparison_basis'], 'straight-line pickup distance')

    def test_follow_up_changes_goal_without_relabeling_unknown_quests(self):
        story = replace(self.quest, quest_id=501, name='Story quest', story_kind='story', story='Explains the area.')
        side = replace(story, quest_id=502, name='Side quest', story_kind='side', story=None, rewards=('Bag',))
        unknown = replace(side, quest_id=503, name='Unknown quest', listed_xp=2000, story_kind='unknown', rewards=())
        obs = replace(self.observation, offers=frozenset())
        choices = [unknown, story, side]
        self.assertEqual(self.decide(obs, choices, focus='story')['recommendation']['quest_id'], 501)
        result = self.decide(obs, choices, focus='side')
        self.assertEqual(result['recommendation']['quest_id'], 502)
        unknown_row = next(row for row in result['alternatives'] if row['quest_id'] == 503)
        self.assertEqual(unknown_row['story_kind'], 'unknown')
        self.assertEqual(self.decide(obs, choices, focus='rewards', quest_id=502)['recommendation']['reward_choices'], ['Bag'])

    def test_core_reply_explains_a_reward_follow_up_and_uncertain_speed(self):
        reply = render_pickup_advice(self.decide())
        self.assertIn('Pick up Return to Bellowfiz from Rejold Barleybrew', reply)
        self.assertIn('875 XP', reply)
        self.assertIn('compare completion speed', reply)
        self.assertIn('The Perfect Stout', reply)
        self.assertNotIn('XP per minute', reply)
        follow_up = render_pickup_advice(self.decide(focus='weapon', quest_id=320))
        self.assertIn('Sharp Axe', follow_up)
        self.assertIn('can’t confirm a weapon upgrade', follow_up)
