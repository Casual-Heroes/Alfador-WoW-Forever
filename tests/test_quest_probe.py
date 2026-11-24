"""Execute trusted repository Lua with synthetic WoW APIs; never imported Lua.

These are mocked Lua runtime checks, not game API/secret-value or visual tests.
"""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.builddeps'))
sys.path.insert(0, str(ROOT / 'tools'))
from lupa.lua51 import LuaRuntime as Lua51
from lupa.lua54 import LuaRuntime as Lua54
from quest_capture_import import validate_capture

MOCK = r'''
messages = {}
secret = {}
issecretvalue = function(value) return value == secret end
DEFAULT_CHAT_FRAME = { AddMessage = function(_, text) messages[#messages + 1] = text end }
SlashCmdList = {}
UIParent = {}
ChatFontNormal = {}
objects = {}
local methods = {}
function methods:SetSize(...) end
function methods:SetPoint(...) end
function methods:SetFrameStrata(...) end
function methods:SetAllPoints(...) end
function methods:SetColorTexture(...) end
function methods:SetMultiLine(...) end
function methods:SetAutoFocus(...) end
function methods:SetFontObject(...) end
function methods:SetWidth(...) end
function methods:SetMaxLetters(...) end
function methods:SetEnabled(value) self.enabled = value end
function methods:IsShown() return self.visible end
function methods:RegisterEvent(name) self.events = self.events or {}; self.events[name] = true end
function methods:UnregisterAllEvents() self.events = {} end
function methods:SetScript(name, fn) self[name] = fn end
function methods:SetScrollChild(child) self.child = child end
function methods:SetFocus() end
function methods:HighlightText() end
function methods:Hide() local was = self.visible; self.visible = false; if was and self.OnHide then self:OnHide() end end
function methods:Show() local was = self.visible; self.visible = true; if not was and self.OnShow then self:OnShow() end end
function methods:SetText(text) self.text = text; if self.kind == 'EditBox' then exported = text end end
local function object(kind, name)
    local value = setmetatable({kind = kind, visible = false}, {__index = methods})
    if name then objects[name] = value end
    return value
end
function methods:CreateTexture(...) return object('Texture') end
function methods:CreateFontString(...) return object('FontString') end
function CreateFrame(kind, name, ...) return object(kind, name) end
function InCombatLockdown() return false end
function GetBuildInfo() return '1.60.1', '70959', 'Nov 13 2026', 16001 end
function GetServerTime() return 1795000000 end
function UnitGUID(unit) assert(unit == 'player'); return 'Synthetic-GUID' end
function UnitName(unit) assert(unit == 'player'); return 'Synthetic' end
function UnitLevel(unit) assert(unit == 'player'); return 10 end
function GetZoneText() return 'Synthetic zone' end
C_Map = { GetBestMapForUnit = function(unit) assert(unit == 'player'); return 10 end }
log = {{isHeader = true}, {isHeader = false, questID = 1, level = 5, title = 'Synthetic One'},
       {isHeader = false, questID = 2, level = 6, title = 'Synthetic Two'},
       {isHeader = false, questID = 3, level = 7, title = 'Synthetic Three'}}
C_QuestLog = {
    GetNumQuestLogEntries = function() return #log end,
    GetInfo = function(index) return log[index] end,
    IsOnMap = function(id) return true end,
    IsOnQuest = function(id) return true end,
    IsQuestFlaggedCompleted = function(id) return false end,
    IsComplete = function(id) return false end,
}
'''


class ProbeChecks:
    runtime = None

    def setUp(self):
        self.lua = self.runtime(unpack_returned_tuples=True, register_eval=False, register_builtins=False)
        self.lua.execute(MOCK)
        # Trusted source only: never execute user-exported JSON or SavedVariables.
        self.lua.execute((ROOT / 'addons/Alfador-wow/Alfador.lua').read_text(encoding='utf-8'))

    def capture(self):
        self.lua.execute("SlashCmdList.ALFADORWOW('')")
        self.lua.execute('''local p = objects.AlfadorWowExport
            if p and p.visible and not p.showingReport then p.copyButton.OnClick() end''')
        raw = self.lua.globals().exported
        return json.loads(raw) if raw is not None else None

    def test_lua_to_json_import_round_trip(self):
        value = self.capture()
        _, receipt = validate_capture(self.lua.globals().exported.encode())
        self.assertEqual(receipt['candidateCount'], 3)
        self.assertEqual(value['freshness'], 'historical')
        self.assertEqual(value['quests'][0]['rewardXP'], {'status': 'unavailable'})
        self.assertEqual(receipt['coreDelivery'], 'not-attempted')

    def test_same_second_captures_increment_serial(self):
        first = self.capture()
        second = self.capture()
        self.assertEqual(first['capturedAtUnix'], second['capturedAtUnix'])
        self.assertEqual(first['localCaptureSerial'], 1)
        self.assertEqual(second['localCaptureSerial'], 2)

    def test_hiding_panel_does_not_reset_serial(self):
        first = self.capture()
        self.lua.execute('objects.AlfadorWowExport:Hide()')
        second = self.capture()
        self.assertEqual(second['localCaptureSerial'], first['localCaptureSerial'] + 1)

    def test_new_addon_runtime_restarts_serial_at_one(self):
        self.capture()
        self.assertEqual(self.capture()['localCaptureSerial'], 2)
        # Reinitialize mock runtime and trusted addon, not a claim of in-game reload acceptance.
        self.setUp()
        self.assertEqual(self.capture()['localCaptureSerial'], 1)

    def test_clock_regression_does_not_reset_or_correct_serial(self):
        first = self.capture()
        self.lua.execute('function GetServerTime() return 1794999999 end')
        second = self.capture()
        self.assertLess(second['capturedAtUnix']['value'], first['capturedAtUnix']['value'])
        self.assertEqual(second['localCaptureSerial'], first['localCaptureSerial'] + 1)

    def test_escaping_real_json_control_chars(self):
        self.lua.execute(r'''function GetZoneText() return 'quote" slash\\ newline\n tab\t null\000' end''')
        value = self.capture()
        self.assertEqual(value['zone']['name']['value'], 'quote" slash\\ newline\n tab\t null\x00')

    def test_utf8_round_trip(self):
        self.lua.execute("function UnitName() return 'Synthétique' end")
        self.assertEqual(self.capture()['player']['name']['value'], 'Synthétique')

    def test_wrong_build_refuses_export(self):
        self.lua.execute("function GetBuildInfo() return '12.1.5', '70961', '', 120105 end")
        self.assertIsNone(self.capture())

    def test_combat_refuses_export(self):
        self.lua.execute('function InCombatLockdown() return true end')
        self.assertIsNone(self.capture())

    def test_unknown_combat_refuses_export(self):
        self.lua.execute('InCombatLockdown = nil')
        self.assertIsNone(self.capture())

    def test_missing_secret_checker_refuses_export(self):
        self.lua.execute('issecretvalue = nil')
        self.assertIsNone(self.capture())

    def test_restricted_scalar_not_serialized(self):
        self.lua.execute('function UnitName() return secret end')
        self.assertEqual(self.capture()['player']['name'], {'status': 'restricted'})

    def test_failed_completion_stays_unknown(self):
        self.lua.execute("C_QuestLog.IsComplete = function() error('unavailable') end")
        self.assertEqual(self.capture()['quests'][0]['objectivesComplete'], {'status': 'call-failed'})

    def test_unavailable_on_map_not_false_or_full_coverage(self):
        self.lua.execute('C_QuestLog.IsOnMap = nil')
        value = self.capture()
        self.assertEqual(value['quests'], [])
        self.assertEqual(value['unresolvedLogEntries'], 3)

    def test_candidate_limit_refuses_truncation(self):
        self.lua.execute('log = {}; for id=1,51 do log[id]={isHeader=false,questID=id,level=5} end')
        self.assertIsNone(self.capture())

    def test_fifty_candidates_are_accepted(self):
        self.lua.execute('log = {}; for id=1,50 do log[id]={isHeader=false,questID=id,level=5} end')
        self.assertEqual(len(self.capture()['quests']), 50)

    def test_bad_log_count_refuses_export(self):
        self.lua.execute('C_QuestLog.GetNumQuestLogEntries = function() return 201 end')
        self.assertIsNone(self.capture())

    def test_fresh_capture_tracks_map_changes(self):
        first = self.capture()
        self.lua.execute('C_Map.GetBestMapForUnit = function() return 99 end')
        second = self.capture()
        self.assertEqual(first['zone']['mapId']['value'], 10)
        self.assertEqual(second['zone']['mapId']['value'], 99)
        self.assertEqual(second['localCaptureSerial'], first['localCaptureSerial'] + 1)

    def test_failed_refresh_hides_old_snapshot(self):
        self.capture()
        self.lua.execute('function InCombatLockdown() return true end')
        self.capture()
        self.assertFalse(self.lua.eval("objects.AlfadorWowExport.visible"))

    def test_unrecognized_slash_text_does_not_execute(self):
        self.lua.execute("SlashCmdList.ALFADORWOW('arbitrary-command')")
        self.assertIsNone(self.lua.globals().exported)

    def enable_xp(self):
        self.lua.execute('''
            selectedQuest = 1
            C_QuestLog.GetSelectedQuest = function() return selectedQuest end
            C_QuestLog.ShouldShowQuestRewards = function() return true end
            GetQuestLogRewardXP = function(...) assert(select('#', ...) == 0); return 125 end
        ''')

    def test_xp_only_bound_to_selected_quest(self):
        self.enable_xp()
        value = self.capture()
        self.assertEqual(value['quests'][0]['rewardXP'], {'status': 'observed', 'value': 125})
        self.assertEqual(value['quests'][1]['rewardXP'], {'status': 'unavailable'})
        context = value['quests'][0]['rewardXPContext']['value']
        self.assertEqual(context['questId'], 1)
        self.assertEqual(context['playerLevel'], 10)
        _, receipt = validate_capture(self.lua.globals().exported.encode())
        self.assertEqual(receipt['xpAmountsObserved'], 1)
        self.assertEqual(receipt['xpUIVerification'], 'not-established')

    def test_selection_change_during_xp_read_discards_amount(self):
        self.enable_xp()
        self.lua.execute('GetQuestLogRewardXP = function() selectedQuest = 2; return 125 end')
        self.assertEqual(self.capture()['quests'][0]['rewardXP'], {'status': 'unavailable'})

    def test_level_change_during_xp_read_discards_amount(self):
        self.enable_xp()
        self.lua.execute('GetQuestLogRewardXP = function() UnitLevel = function() return 11 end; return 125 end')
        self.assertEqual(self.capture()['quests'][0]['rewardXP'], {'status': 'unavailable'})

    def test_character_change_during_xp_read_discards_amount(self):
        self.enable_xp()
        self.lua.execute("GetQuestLogRewardXP = function() UnitGUID = function() return 'other' end; return 125 end")
        self.assertEqual(self.capture()['quests'][0]['rewardXP'], {'status': 'unavailable'})

    def test_hidden_rewards_are_not_read(self):
        self.enable_xp()
        self.lua.execute('C_QuestLog.ShouldShowQuestRewards = function() return false end; xpCalls = 0; GetQuestLogRewardXP = function() xpCalls = xpCalls + 1; return 125 end')
        self.assertEqual(self.capture()['quests'][0]['rewardXP'], {'status': 'unavailable'})
        self.assertEqual(self.lua.globals().xpCalls, 0)

    def test_restricted_xp_remains_restricted(self):
        self.enable_xp()
        self.lua.execute('GetQuestLogRewardXP = function() return secret end')
        self.assertEqual(self.capture()['quests'][0]['rewardXP'], {'status': 'restricted'})

    def test_invalid_xp_types_and_ranges(self):
        self.enable_xp()
        for expression in ('true', "'125'", '-1', '1.5', '1000000001'):
            self.lua.execute('GetQuestLogRewardXP = function() return ' + expression + ' end')
            self.assertEqual(self.capture()['quests'][0]['rewardXP'], {'status': 'invalid'})

    def test_zero_xp_is_a_reported_value_not_ui_verification(self):
        self.enable_xp()
        self.lua.execute('GetQuestLogRewardXP = function() return 0 end')
        self.assertEqual(self.capture()['quests'][0]['rewardXP'], {'status': 'observed', 'value': 0})
        _, receipt = validate_capture(self.lua.globals().exported.encode())
        self.assertEqual(receipt['xpUIVerification'], 'not-established')

    def test_selection_changes_do_not_reuse_old_quest_xp(self):
        self.enable_xp()
        first = self.capture()
        self.lua.execute('selectedQuest = 2; GetQuestLogRewardXP = function() return 250 end')
        second = self.capture()
        self.assertEqual(first['quests'][0]['rewardXP']['value'], 125)
        self.assertEqual(second['quests'][0]['rewardXP']['status'], 'unavailable')
        self.assertEqual(second['quests'][1]['rewardXP']['value'], 250)

    def test_missing_selection_has_specific_diagnostic(self):
        value = self.capture()
        self.assertEqual(value['selectedQuestAtCapture'], {'status': 'api-unavailable'})
        self.assertEqual(value['quests'][0]['rewardXPRead'], 'selection-unavailable')

    def test_zero_selected_quest_is_not_guessed(self):
        self.enable_xp()
        self.lua.execute('selectedQuest = 0')
        value = self.capture()
        self.assertEqual(value['selectedQuestAtCapture']['value'], 0)
        self.assertTrue(all(q['rewardXPRead'] == 'not-selected-quest' for q in value['quests']))

    def test_display_gate_has_specific_diagnostic(self):
        self.enable_xp()
        self.lua.execute('C_QuestLog.ShouldShowQuestRewards = function() return false end')
        self.assertEqual(self.capture()['quests'][0]['rewardXPRead'], 'rewards-not-shown')

    def test_xp_api_missing_has_specific_diagnostic(self):
        self.enable_xp()
        self.lua.execute('GetQuestLogRewardXP = nil')
        self.assertEqual(self.capture()['quests'][0]['rewardXPRead'], 'xp-api-unavailable')

    def test_selected_quest_outside_candidates_reported(self):
        self.enable_xp()
        self.lua.execute('selectedQuest = 99')
        value = self.capture()
        self.assertEqual(value['selectedQuestAtCapture']['value'], 99)
        self.assertTrue(all(q['rewardXPRead'] == 'not-selected-quest' for q in value['quests']))

    def test_secret_selection_kept_restricted(self):
        self.enable_xp()
        self.lua.execute('selectedQuest = secret')
        value = self.capture()
        self.assertEqual(value['selectedQuestAtCapture'], {'status': 'restricted'})
        self.assertEqual(value['quests'][0]['rewardXPRead'], 'selection-unavailable')

    def test_malformed_selection_does_not_break_json(self):
        self.enable_xp()
        self.lua.execute('selectedQuest = true')
        self.capture()
        _, receipt = validate_capture(self.lua.globals().exported.encode())
        self.assertEqual(receipt['xpAmountsObserved'], 0)

    def test_quest_titles_are_observed_from_game_log(self):
        value = self.capture()
        self.assertEqual(value['quests'][0]['title'], {'status': 'observed', 'value': 'Synthetic One'})

    def test_default_view_uses_names_instead_of_ids(self):
        self.lua.execute("SlashCmdList.ALFADORWOW('')")
        visible = self.lua.eval('objects.AlfadorWowExport.edit.text')
        self.assertIn('Synthetic One', visible)
        self.assertIn('Objectives in progress', visible)
        self.assertNotIn('questId', visible)
        self.assertNotIn('Synthetic-GUID', visible)
        self.assertFalse(self.lua.eval('objects.AlfadorWowExport.showingReport'))

    def test_report_button_round_trips_back_to_names(self):
        self.capture()
        self.assertTrue(self.lua.eval('objects.AlfadorWowExport.showingReport'))
        self.lua.execute('objects.AlfadorWowExport.copyButton.OnClick()')
        self.assertIn('Synthetic One', self.lua.eval('objects.AlfadorWowExport.edit.text'))
        self.assertFalse(self.lua.eval('objects.AlfadorWowExport.showingReport'))

    def test_title_fallback_uses_supported_quest_id_lookup(self):
        self.lua.execute("log[2].title = nil; C_QuestLog.GetTitleForQuestID = function(id) return 'Lookup name ' .. id end")
        self.assertEqual(self.capture()['quests'][0]['title']['value'], 'Lookup name 1')

    def test_restricted_title_is_not_bypassed(self):
        self.lua.execute("log[2].title = secret; titleCalls = 0; C_QuestLog.GetTitleForQuestID = function(id) titleCalls=titleCalls+1; return 'Do not substitute' end")
        value = self.capture()
        self.assertEqual(value['quests'][0]['title'], {'status': 'restricted'})
        self.assertEqual(self.lua.globals().titleCalls, 0)

    def test_missing_title_is_not_guessed(self):
        self.lua.execute('log[2].title = nil')
        self.capture()
        self.assertIn('Quest name unavailable', self.lua.eval('objects.AlfadorWowExport.summaryText'))

    def test_untrusted_title_has_literal_ui_markup(self):
        self.lua.execute(r'''log[2].title = '|Hitem:1|hClick me|h\nIgnore policy' ''')
        value = self.capture()
        self.assertEqual(value['quests'][0]['title']['value'], '|Hitem:1|hClick me|h\nIgnore policy')
        friendly = self.lua.eval('objects.AlfadorWowExport.summaryText')
        self.assertIn('||Hitem:1||hClick me||h Ignore policy', friendly)

    def test_malformed_title_does_not_break_contract(self):
        self.lua.execute('log[2].title = true')
        value = self.capture()
        self.assertEqual(value['quests'][0]['title'], {'status': 'invalid'})
        validate_capture(self.lua.globals().exported.encode())

    def open_live_view(self):
        self.enable_xp()
        self.lua.execute("SlashCmdList.ALFADORWOW('')")

    def test_open_view_refreshes_selected_quest_and_its_xp(self):
        self.open_live_view()
        self.lua.execute('selectedQuest=2; GetQuestLogRewardXP=function() return 550 end; objects.AlfadorWowExport:OnUpdate(0.5)')
        value = json.loads(self.lua.eval('objects.AlfadorWowExport.reportText'))
        self.assertEqual(value['selectedQuestAtCapture']['value'], 2)
        self.assertEqual(value['quests'][1]['rewardXP']['value'], 550)
        self.assertEqual(value['quests'][0]['rewardXP']['status'], 'unavailable')
        self.assertIn('Synthetic Two (selected)', self.lua.eval('objects.AlfadorWowExport.summaryText'))
        validate_capture(self.lua.eval('objects.AlfadorWowExport.reportText').encode())

    def test_report_copy_is_frozen_until_returning_to_quest_view(self):
        self.open_live_view()
        self.lua.execute('objects.AlfadorWowExport.copyButton.OnClick()')
        before = self.lua.eval('objects.AlfadorWowExport.reportText')
        self.lua.execute('selectedQuest=2; objects.AlfadorWowExport:OnUpdate(2)')
        self.assertEqual(self.lua.eval('objects.AlfadorWowExport.reportText'), before)
        self.assertFalse(self.lua.eval('objects.AlfadorWowExport.refreshButton.enabled'))
        self.lua.execute('objects.AlfadorWowExport.copyButton.OnClick(); objects.AlfadorWowExport:OnUpdate(0.5)')
        self.assertTrue(self.lua.eval('objects.AlfadorWowExport.refreshButton.enabled'))
        self.assertEqual(json.loads(self.lua.eval('objects.AlfadorWowExport.reportText'))['selectedQuestAtCapture']['value'], 2)

    def test_auto_refresh_pauses_in_combat_and_resumes(self):
        self.open_live_view()
        before = self.lua.eval('objects.AlfadorWowExport.reportText')
        self.lua.execute('selectedQuest=2; function InCombatLockdown() return true end; objects.AlfadorWowExport:OnUpdate(0.5)')
        self.assertEqual(self.lua.eval('objects.AlfadorWowExport.reportText'), before)
        self.assertIn('paused', self.lua.eval('objects.AlfadorWowExport.title.text'))
        self.lua.execute('function InCombatLockdown() return false end; objects.AlfadorWowExport:OnUpdate(0.5)')
        self.assertEqual(json.loads(self.lua.eval('objects.AlfadorWowExport.reportText'))['selectedQuestAtCapture']['value'], 2)

    def test_refresh_button_updates_immediately(self):
        self.open_live_view()
        self.lua.execute('selectedQuest=2; objects.AlfadorWowExport.refreshButton.OnClick()')
        self.assertEqual(json.loads(self.lua.eval('objects.AlfadorWowExport.reportText'))['selectedQuestAtCapture']['value'], 2)

    def test_hidden_view_unregisters_and_does_not_refresh(self):
        self.open_live_view()
        self.assertTrue(self.lua.eval("objects.AlfadorWowExport.events.QUEST_LOG_UPDATE"))
        before = self.lua.eval('objects.AlfadorWowExport.reportText')
        self.lua.execute('objects.AlfadorWowExport:Hide(); selectedQuest=2; objects.AlfadorWowExport:OnUpdate(2)')
        self.assertIsNone(self.lua.eval("objects.AlfadorWowExport.events.QUEST_LOG_UPDATE"))
        self.assertEqual(self.lua.eval('objects.AlfadorWowExport.reportText'), before)

    def test_auto_refresh_throttles_and_does_not_spam_chat(self):
        self.open_live_view()
        messages = self.lua.eval('#messages')
        self.lua.execute('selectedQuest=2; objects.AlfadorWowExport:OnUpdate(0.25)')
        self.assertEqual(json.loads(self.lua.eval('objects.AlfadorWowExport.reportText'))['localCaptureSerial'], 1)
        self.lua.execute('objects.AlfadorWowExport:OnUpdate(0.25); objects.AlfadorWowExport:OnUpdate(0.5)')
        self.assertEqual(json.loads(self.lua.eval('objects.AlfadorWowExport.reportText'))['localCaptureSerial'], 2)
        self.assertEqual(self.lua.eval('#messages'), messages)

    def test_quest_log_event_refreshes_objective_flags(self):
        self.open_live_view()
        self.lua.execute('C_QuestLog.IsComplete=function() return true end; objects.AlfadorWowExport:OnEvent("QUEST_LOG_UPDATE"); objects.AlfadorWowExport:OnUpdate(0.5)')
        self.assertIn('Objectives complete', self.lua.eval('objects.AlfadorWowExport.summaryText'))

    def test_current_map_and_level_changes_refresh(self):
        self.open_live_view()
        self.lua.execute('C_Map.GetBestMapForUnit=function() return 20 end; UnitLevel=function() return 11 end; objects.AlfadorWowExport:OnUpdate(0.5)')
        value = json.loads(self.lua.eval('objects.AlfadorWowExport.reportText'))
        self.assertEqual(value['zone']['mapId']['value'], 20)
        self.assertEqual(value['player']['level']['value'], 11)
        self.assertEqual(value['quests'][0]['rewardXPContext']['value']['playerLevel'], 11)


class Lua51ProbeTests(ProbeChecks, unittest.TestCase):
    runtime = Lua51


class Lua54ProbeTests(ProbeChecks, unittest.TestCase):
    runtime = Lua54


if __name__ == '__main__':
    unittest.main()
