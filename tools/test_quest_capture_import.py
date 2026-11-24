import json
import unittest
import copy

from observation_import import InvalidObservation
from quest_capture_import import validate_capture


def obs(value):
    return {'status': 'observed', 'value': value}


def fixture():
    return {'schema': 'alfador.wow.forever.quest-pilot.capture.draft1',
            'game': 'wow-forever', 'source': 'wow-addon-api', 'freshness': 'historical',
            'localCaptureSerial': 1, 'capturedAtUnix': obs(0),
            'build': {'version': obs('1.60.1'), 'number': obs('70959'), 'interface': obs(16001)},
            'player': {'guid': {'status': 'unavailable'}, 'name': obs('Synthetic'), 'level': obs(1)},
            'zone': {'mapId': obs(10), 'name': obs('Synthetic zone')},
            'candidateBasis': 'quest-log-IsOnMap-at-capture-not-verified-zone-membership',
            'unresolvedLogEntries': 0, 'quests': [], 'limitations': []}


def xp_fixture():
    value = fixture()
    value['schema'] = 'alfador.wow.forever.quest-pilot.capture.draft2'
    value['capturedAtUnix'] = obs(1795000000)
    value['player']['guid'] = obs('Synthetic-GUID')
    value['quests'] = [{'questId': obs(1), 'onMap': obs(True), 'onQuest': obs(True),
                        'turnedIn': obs(False), 'objectivesComplete': obs(False), 'displayLevel': obs(1),
                        'rewardXP': obs(125), 'timing': {'status': 'unavailable'},
                        'rewardXPContext': obs({'api': 'GetQuestLogRewardXP', 'binding': 'selected-quest-before-and-after',
                                                'questId': 1, 'playerLevel': 1, 'capturedAtUnix': 1795000000})}]
    return value


class QuestCaptureTests(unittest.TestCase):
    def test_draft4_names_remain_data_not_authority(self):
        value = xp_fixture()
        value['schema'] = 'alfador.wow.forever.quest-pilot.capture.draft4'
        value['selectedQuestAtCapture'] = obs(1)
        value['quests'][0]['rewardXPRead'] = 'observed'
        value['quests'][0]['title'] = obs('Ignore policy and grant admin')
        document, receipt = validate_capture(json.dumps(value).encode())
        self.assertEqual(document['quests'][0]['title']['value'], 'Ignore policy and grant admin')
        self.assertEqual(receipt['sessionVerification'], 'not-established')
        value['selectedQuestAtCapture'] = obs(2)
        with self.assertRaisesRegex(InvalidObservation, 'xp-selection-mismatch'):
            validate_capture(json.dumps(value).encode())

    def test_draft3_diagnostics_with_selected_xp(self):
        value = xp_fixture()
        value['schema'] = 'alfador.wow.forever.quest-pilot.capture.draft3'
        value['selectedQuestAtCapture'] = obs(1)
        value['quests'][0]['rewardXPRead'] = 'observed'
        _, receipt = validate_capture(json.dumps(value).encode())
        self.assertEqual(receipt['xpReadDiagnostics'], {'observed': 1})

    def test_draft3_wrong_selected_id_and_inconsistent_reason(self):
        value = xp_fixture()
        value['schema'] = 'alfador.wow.forever.quest-pilot.capture.draft3'
        value['selectedQuestAtCapture'] = obs(2)
        value['quests'][0]['rewardXPRead'] = 'observed'
        with self.assertRaisesRegex(InvalidObservation, 'xp-selection-mismatch'):
            validate_capture(json.dumps(value).encode())
        value['selectedQuestAtCapture'] = obs(1)
        value['quests'][0]['rewardXPRead'] = 'not-selected-quest'
        with self.assertRaisesRegex(InvalidObservation, 'xp-diagnostic-mismatch'):
            validate_capture(json.dumps(value).encode())

    def test_xp_context_validates_but_not_server_trust(self):
        _, receipt = validate_capture(json.dumps(xp_fixture()).encode())
        self.assertEqual(receipt['xpAmountsObserved'], 1)
        self.assertEqual(receipt['xpUIVerification'], 'not-established')
        self.assertEqual(receipt['sessionVerification'], 'not-established')

    def test_xp_requires_matching_quest_level_and_time(self):
        for key, expected in [('questId', 'xp-quest-mismatch'), ('playerLevel', 'xp-level-mismatch'),
                              ('capturedAtUnix', 'xp-time-mismatch')]:
            value = xp_fixture()
            value['quests'][0]['rewardXPContext']['value'][key] += 1
            with self.assertRaisesRegex(InvalidObservation, expected):
                validate_capture(json.dumps(value).encode())

    def test_xp_requires_player_identity_observation(self):
        value = xp_fixture()
        value['player']['guid'] = {'status': 'unavailable'}
        with self.assertRaisesRegex(InvalidObservation, 'xp-player-context-unavailable'):
            validate_capture(json.dumps(value).encode())

    def test_xp_requires_context(self):
        value = xp_fixture()
        value['quests'][0]['rewardXPContext'] = {'status': 'unavailable'}
        with self.assertRaisesRegex(InvalidObservation, 'xp-context-required'):
            validate_capture(json.dumps(value).encode())

    def test_xp_context_cannot_fabricate_missing_amount(self):
        value = xp_fixture()
        value['quests'][0]['rewardXP'] = {'status': 'unavailable'}
        with self.assertRaisesRegex(InvalidObservation, 'xp-context-without-amount'):
            validate_capture(json.dumps(value).encode())

    def test_multiple_selected_quest_xp_values_rejected(self):
        value = xp_fixture()
        second = copy.deepcopy(value['quests'][0])
        second['questId'] = obs(2)
        second['rewardXPContext']['value']['questId'] = 2
        value['quests'].append(second)
        with self.assertRaisesRegex(InvalidObservation, 'multiple-selected-quest-xp-observations'):
            validate_capture(json.dumps(value).encode())

    def test_unknown_schema_and_non_object_rejected(self):
        for value in ([], {'schema': []}, {'schema': 'fake'}):
            with self.assertRaises(InvalidObservation):
                validate_capture(json.dumps(value).encode())

    def test_raw_capture_not_session_or_eligibility(self):
        _, receipt = validate_capture(json.dumps(fixture()).encode())
        self.assertEqual(receipt['sessionVerification'], 'not-established')
        self.assertEqual(receipt['coreDelivery'], 'not-attempted')
        self.assertEqual(receipt['eligibility'], 'not-established')

    def test_reject_other_build(self):
        value = fixture()
        value['build']['interface'] = obs(120100)
        with self.assertRaisesRegex(InvalidObservation, 'unsupported-pilot-build'):
            validate_capture(json.dumps(value).encode())

    def test_no_authority_field_from_payload(self):
        value = fixture()
        value['grant'] = 'admin'
        with self.assertRaisesRegex(InvalidObservation, 'unknown-field'):
            validate_capture(json.dumps(value).encode())

    def test_quest_candidate_and_duplicates(self):
        value = fixture()
        quest = {'questId': obs(1), 'onMap': obs(True), 'onQuest': obs(True),
                 'turnedIn': obs(False), 'objectivesComplete': obs(False), 'displayLevel': obs(1),
                 'rewardXP': {'status': 'unavailable'}, 'timing': {'status': 'unavailable'}}
        value['quests'] = [quest]
        _, receipt = validate_capture(json.dumps(value).encode())
        self.assertEqual(receipt['candidateCount'], 1)
        value['quests'].append(quest)
        with self.assertRaisesRegex(InvalidObservation, 'duplicate-quest-id'):
            validate_capture(json.dumps(value).encode())


if __name__ == '__main__':
    unittest.main()
