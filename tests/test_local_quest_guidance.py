"""Exercise the in-game entry points with mocked APIs and the pinned catalog."""
import unittest

from test_quest_probe import Lua51, Lua54, MOCK, ROOT
from build_quest_catalog import catalog_lua


class GuidanceChecks:
    def setUp(self):
        self.lua = self.runtime(unpack_returned_tuples=True, register_eval=False, register_builtins=False)
        self.lua.execute(MOCK)
        self.lua.execute('''
            local methods = getmetatable(CreateFrame('Frame')).__index
            for _, key in ipairs({'SetBackdrop', 'SetBackdropColor', 'SetClampedToScreen', 'SetMovable',
                    'EnableMouse', 'EnableMouseWheel', 'RegisterForDrag', 'StartMoving', 'StopMovingOrSizing',
                    'SetTextColor', 'SetJustifyH', 'SetTexture', 'SetTexCoord', 'ClearAllPoints'}) do methods[key] = function() end end
            function methods:SetRotation(value) self.rotation = value end
            function methods:SetScale(value) self.scale = value end
            function methods:GetScale() return self.scale or 1 end
            addon = {}
            function GetBuildInfo() return '1.60.1', '71037', '', 16001 end
            function IsInInstance() return false end
            function GetPlayerFacing() return 0 end
            function UnitLevel() return 20 end
            function UnitFactionGroup() return 'Alliance' end
            function UnitRace() return 'Human', 'Human', 1 end
            function UnitClass() return 'Paladin', 'PALADIN', 2 end
            function point(x, y) return { GetXY = function() return x, y end } end
            C_Map.GetBestMapForUnit = function() return 1455 end
            C_Map.GetPlayerMapPosition = function(map, unit)
                assert(map == 1455 and unit == 'player'); return point(.48, .43)
            end
            C_Map.GetWorldPosFromMapPos = function(map, corner)
                assert(map == 1455)
                local f = addon.pickupFrames[map]
                if corner.x == 0 then return f[1], point(f[2], f[3]) end
                return f[1], point(f[4], f[5])
            end
            C_QuestLog.IsOnQuest = function() return false end
            UiMapPoint = { CreateFromCoordinates = function(...) return {...} end }
            C_Map.SetUserWaypoint = function(p) waypoint = p; return true end
        ''')
        addon = self.lua.globals().addon
        self.lua.execute(catalog_lua().decode(), 'Alfador-wow', addon)
        self.lua.execute((ROOT / 'addons/Alfador-wow/QuestGuide.lua').read_text(encoding='utf-8'), 'Alfador-wow', addon)

    def command(self, command):
        self.lua.globals().SlashCmdList.ALFADORWOWGUIDE(command)
        return self.lua.globals().exported

    def test_catalog_breadcrumb_and_item_choices(self):
        self.assertIn('Catalog breadcrumb to Gnogaine (Gnomeregan quest)', self.command('2927'))
        body = self.command('218')
        self.assertIn('550 listed XP', body)
        self.assertIn('Dwarven Kite Shield', body)
        self.assertIn('Smooth Walking Staff', body)

    def test_player_position_and_explicit_waypoint(self):
        body = self.command('nearby')
        self.assertIn('Nearby quest leads', body)
        self.assertIn('Check pickup at', body)
        self.assertIsNone(self.lua.globals().waypoint)
        self.command('pin 2927')
        waypoint = self.lua.globals().waypoint
        self.assertEqual(waypoint[1], 1455)
        self.assertTrue(0 <= waypoint[2] <= 1 and 0 <= waypoint[3] <= 1)
        self.lua.execute("C_Map.GetWorldPosFromMapPos = function() return 1, point(0, 0) end; waypoint = nil")
        self.assertIn('Comparable outdoor position is unavailable', self.command('nearby'))
        self.command('pin 2927')
        self.assertIsNone(self.lua.globals().waypoint)

    def test_pin_button_revalidates_map_and_hides_without_a_pickup(self):
        self.command('nearby')
        button = self.lua.globals().objects.AlfadorWowGuidePinPickup
        self.assertTrue(button.visible)
        button.OnClick()
        self.assertEqual(self.lua.globals().waypoint[1], 1455)
        self.lua.execute('C_Map.GetBestMapForUnit = function() return 1426 end; waypoint = nil')
        button.OnClick()
        self.assertIsNone(self.lua.globals().waypoint)
        self.assertIn('Your map changed', self.lua.globals().messages[2])
        self.command('')
        self.assertFalse(button.visible)

    def test_navigator_tracks_direction_and_stops_when_quest_accepted(self):
        self.lua.execute('addon.pickupPoints[1455][2927] = {{.48,.30,"Gnoarn"}}')
        self.command('pin 2927')
        nav = self.lua.globals().objects.AlfadorWowNavigator
        self.assertTrue(nav.visible)
        self.assertIn('The Day After', nav.quest.text)
        self.assertIn('straight line', nav.status.text)
        self.assertAlmostEqual(nav.arrow.rotation, 0)
        self.lua.execute('GetPlayerFacing = function() return math.pi / 2 end')
        nav.OnUpdate(nav, .5)
        self.assertAlmostEqual(nav.arrow.rotation, -1.5707963267948966)
        self.lua.execute('C_QuestLog.IsOnQuest = function(id) return id == 2927 end')
        nav.OnUpdate(nav, .5)
        self.assertFalse(nav.arrow.visible)
        self.assertIn('Quest accepted', nav.status.text)

    def test_operation_recombobulation_route_advances_and_speaks_locally(self):
        self.lua.execute('''
            C_Map.GetBestMapForUnit = function() return 1426 end
            C_Map.GetPlayerMapPosition = function() return point(.45,.50) end
            C_Map.GetWorldPosFromMapPos = function(map, corner)
                local f = addon.pickupFrames[map]
                if corner.x == 0 then return f[1], point(f[2], f[3]) end
                return f[1], point(f[4], f[5])
            end
            C_Map.HasUserWaypoint = function() return waypoint ~= nil end
            C_Map.GetUserWaypoint = function()
                return {uiMapID=waypoint[1], position=point(waypoint[2], waypoint[3])}
            end
            now = 0
            GetTime = function() return now end
            spoken = {}
            C_VoiceChat = {
                GetTtsVoices = function() return {{voiceID=2}} end,
                SpeakText = function(id, text, rate, volume, overlap)
                    assert(id == 2 and rate == 0 and volume == 80 and overlap == false)
                    spoken[#spoken+1] = text
                end,
            }
        ''')
        self.command('voice on')
        self.command('route 412')
        nav = self.lua.globals().objects.AlfadorWowNavigator
        self.assertIn('Razzle Sprysprocket', nav.location.text)
        initial = self.lua.globals().waypoint[2]
        self.lua.execute('''
            now = 5
            C_QuestLog.IsOnQuest = function() return true end
            C_QuestLog.GetQuestObjectives = function()
                return {{text='Restabilization Cog: 0/8', finished=false, numRequired=8},
                        {text='Gyromechanic Gear: 0/8', finished=false, numRequired=8}}
            end
        ''')
        nav.OnUpdate(nav, .5)
        self.assertIn('Source lead:', nav.location.text)
        self.assertIn('Collect Restabilization Cog', nav.status.text)
        self.assertNotEqual(initial, self.lua.globals().waypoint[2])
        self.lua.execute('now=10; C_QuestLog.IsComplete = function() return true end; waypoint = {1426,.99,.99}')
        nav.OnUpdate(nav, .5)
        self.assertIn('Razzle Sprysprocket', nav.location.text)
        self.assertIn('Turn in', nav.status.text)
        self.assertEqual(self.lua.globals().waypoint[2], .99)
        self.assertEqual(len(self.lua.globals().spoken), 3)
        nav.OnEvent(nav, 'QUEST_TURNED_IN', 412)
        nav.OnUpdate(nav, .5)
        self.assertTrue('Route complete' in nav.status.text or nav.quest.text == 'Route complete')

    def test_evershine_completion_recommends_rejolds_follow_up_and_starts_it(self):
        self.lua.execute('''
            C_Map.GetBestMapForUnit = function() return 1426 end
            C_Map.GetPlayerMapPosition = function()
                local pickup = addon.pickupPoints[1426][320][1]
                return point(pickup[1],pickup[2])
            end
            C_Map.GetWorldPosFromMapPos = function(map, corner)
                local f = addon.pickupFrames[map]
                if corner.x == 0 then return f[1], point(f[2], f[3]) end
                return f[1], point(f[4], f[5])
            end
            local pickups = addon.pickupPoints[1426]
            addon.pickupPoints[1426] = {[319]=pickups[319],[320]=pickups[320]}
            C_QuestLog.IsOnQuest = function(id) return id == 319 end
            C_QuestLog.IsComplete = function(id) return id == 319 end
            now=0
            GetTime = function() return now end
        ''')
        self.command('route 319')
        nav = self.lua.globals().objects.AlfadorWowNavigator
        self.assertIn('Turn in', nav.status.text)
        nav.OnEvent(nav, 'QUEST_TURNED_IN', 319)
        self.lua.execute('C_QuestLog.IsOnQuest = function() return false end')
        nav.OnUpdate(nav, .5)
        self.assertIn('Route complete', nav.status.text)
        self.assertIn('Catalog follow-up', nav.status.text)
        self.assertEqual(nav.quest.text, 'Return to Bellowfiz')
        self.assertEqual(nav.location.text, 'Check with Rejold Barleybrew')
        self.assertTrue(nav.nextQuest.visible)
        self.lua.execute('''
            now=4
            GossipFrame = {IsShown=function() return true end}
            UnitName = function(unit) assert(unit == 'npc'); return 'Rejold Barleybrew' end
            C_GossipInfo = {GetAvailableQuests=function() return {{questID=320}} end}
        ''')
        nav.OnUpdate(nav, .5)
        self.assertEqual(nav.location.text, 'Pick up from Rejold Barleybrew')
        nav.nextQuest.OnClick()
        self.assertEqual(nav.quest.text, 'Return to Bellowfiz')
        self.assertFalse(nav.nextQuest.visible)

    def test_tracked_quest_uses_saved_display_and_updates_distance_in_all_modes(self):
        self.lua.execute('''
            local methods = getmetatable(CreateFrame('Frame')).__index
            function methods:SetPoint(...) self.points = {...} end
            function methods:GetPoint() return (table.unpack or unpack)(self.points) end
            tracked = 320
            C_SuperTrack = {GetSuperTrackedQuestID=function() return tracked end}
            C_QuestLog.GetNextWaypoint = function(id)
                assert(id == 320); return 1455, .58, .43
            end
            C_Map.GetMapWorldSize = function() return 1000,800 end
            AlfadorWowDisplay = {mode='portrait',scale=1.25,always=true,follow=true}
        ''')
        objects = self.lua.globals().objects
        objects.AlfadorWowTrackingEvents.OnEvent(objects.AlfadorWowTrackingEvents, 'PLAYER_ENTERING_WORLD')
        nav = objects.AlfadorWowNavigator
        self.assertTrue(nav.visible and nav.portrait.visible)
        self.assertTrue(nav.janus.visible)
        self.assertEqual(nav.cardElements[2].text, 'Alfador')
        self.assertFalse(nav.arrow.visible)
        self.assertEqual(nav.distance.text, '~100 yd')
        self.assertEqual(nav.scale, 1.25)
        self.command('settings')
        objects.AlfadorWowModeArrow.OnClick()
        self.assertFalse(nav.portrait.visible)
        self.assertFalse(nav.janus.visible)
        self.assertTrue(nav.arrow.visible)
        self.assertEqual(nav.distance.text, '~100 yd')
        objects.AlfadorWowModePortraitArrow.OnClick()
        self.assertTrue(nav.portrait.visible and nav.janus.visible and nav.arrow.visible)
        self.assertFalse(nav.quest.visible)
        self.assertEqual(nav.distance.text, '~100 yd')
        self.assertEqual(self.lua.globals().AlfadorWowDisplay.mode, 'portrait_arrow')
        self.assertEqual(nav.direction.points[1], 'TOP')
        self.assertEqual(nav.direction.points[3], 'BOTTOM')
        nav.direction.SetPoint(nav.direction, 'CENTER', self.lua.globals().UIParent, 'CENTER', 50, -40)
        nav.direction.OnDragStop(nav.direction)
        self.assertEqual(self.lua.globals().AlfadorWowDisplay.arrowAnchor.x, 50)
        self.assertEqual(nav.points[1], 'TOP')
        objects.AlfadorWowModePortraitArrow.OnClick()
        self.assertEqual(nav.direction.points[4], 50)
        objects.AlfadorWowModeCard.OnClick()
        self.assertTrue(nav.quest.visible)
        self.assertEqual(nav.quest.text, 'Return to Bellowfiz')
        self.assertEqual(nav.distance.text, '~100 yd')
        self.lua.execute('C_QuestLog.GetNextWaypoint = function() return 1426, .58, .43 end')
        nav.OnUpdate(nav, .5)
        self.assertFalse(nav.arrow.visible)
        self.assertEqual(nav.distance.text, 'Distance unavailable')
        self.lua.execute('tracked = 0')
        objects.AlfadorWowTrackingEvents.OnEvent(objects.AlfadorWowTrackingEvents, 'SUPER_TRACKING_CHANGED')
        self.assertEqual(nav.distance.text, 'No quest tracked')

    def test_native_addon_settings_register_and_open_the_same_category(self):
        self.lua.execute('''
            variables = {}
            Settings = {
                RegisterVerticalLayoutCategory = function(name)
                    return {name=name, GetID=function() return 75 end}
                end,
                RegisterAddOnCategory = function(category) registered=category end,
                RegisterProxySetting = function(category, key, typ, name, default, get, set)
                    local setting={get=get,set=set,kind=typ}
                    variables[key]=setting
                    return setting
                end,
                CreateDropdown=function(_, setting, options) dropdown=options(); dropdownSetting=setting end,
                CreateCheckbox=function() checkboxes=(checkboxes or 0)+1 end,
                CreateControlTextContainer=function()
                    local items = {}
                    return {Add=function(_, value, label) items[#items+1]={value,label} end,
                            GetData=function() return items end}
                end,
                OpenToCategory=function(id) opened=id end,
            }
        ''')
        globals_ = self.lua.globals()
        events = globals_.objects.AlfadorWowTrackingEvents
        events.OnEvent(events, 'ADDON_LOADED', 'OtherAddon')
        self.assertIsNone(globals_.registered)
        events.OnEvent(events, 'ADDON_LOADED', 'Alfador-wow')
        self.assertEqual(globals_.registered.name, 'Alfador-wow')
        self.assertEqual(globals_.checkboxes, 2)
        self.assertEqual(globals_.dropdown[4][2], 'Portrait + Arrow')
        globals_.dropdownSetting.set('portrait_arrow')
        self.assertEqual(globals_.dropdownSetting.get(), 'portrait_arrow')
        globals_.variables.AlfadorWowAlwaysShow.set(False)
        self.assertFalse(globals_.AlfadorWowDisplay.always)
        self.command('settings')
        self.assertEqual(globals_.opened, 75)
        self.assertIsNone(globals_.objects.AlfadorWowDisplaySettings)

    def test_previously_turned_in_unknown_repeatability_is_not_routed(self):
        self.lua.execute('C_QuestLog.IsQuestFlaggedCompleted = function(id) return id == 412 end')
        self.command('route 412')
        self.assertIn('Operation Recombobulation is marked turned in', self.lua.globals().messages[1])
        self.assertIsNone(self.lua.globals().objects.AlfadorWowNavigator)

    def test_combat_preserves_readable_direction_and_defers_route_changes(self):
        self.lua.execute('addon.pickupPoints[1455][2927] = {{.48,.30,"Gnoarn"}}')
        self.command('route 2927')
        nav = self.lua.globals().objects.AlfadorWowNavigator
        self.assertTrue(nav.arrow.visible)
        self.lua.execute('''
            InCombatLockdown = function() return true end
            C_QuestLog.IsOnQuest = function() error('quest state should stay frozen') end
            GetPlayerFacing = function() return math.pi / 2 end
        ''')
        nav.OnUpdate(nav, .5)
        self.assertTrue(nav.arrow.visible)
        self.assertAlmostEqual(nav.arrow.rotation, -1.5707963267948966)
        self.assertFalse(nav.pinStop.visible)
        self.lua.execute('C_Map.GetPlayerMapPosition = function() return secret end')
        nav.OnUpdate(nav, .5)
        self.assertFalse(nav.arrow.visible)

    def test_route_groups_shared_objectives_and_excludes_distant_sources(self):
        self.lua.execute('''
            addon.pickupPoints[1455] = {[1]={{.48,.43,'First'}},[2]={{.49,.43,'Second'}},[3]={{.50,.43,'Third'}}}
            for id=1,3 do
                addon.catalog[id] = {title='Lead '..id, xp=10, side=1, min_level=1, classes=0, races=0}
            end
            addon.routeObjectives[1] = {{'kill','Enemy',1,{[1455]={{.7,.7,'Enemy'}}}}}
            addon.routeObjectives[2] = {{'kill','Enemy',2,{[1455]={{.7,.7,'Enemy'}}}}}
            addon.routeObjectives[3] = {{'kill','Other',1,{[1455]={{.1,.1,'Other'}}}}}
        ''')
        self.command('route')
        self.assertIn('Shared objective area: Lead 1, Lead 2.', self.lua.globals().messages[1])

    def test_travel_tip_requires_crossing_and_does_not_repeat(self):
        self.lua.execute('''
            x = .48
            now = 60
            GetTime = function() return now end
            C_Map.GetPlayerMapPosition = function() return point(x,.43) end
            addon.pickupPoints[1455] = {[1]={{.63,.43,'Starter'}}}
            addon.catalog[1] = {title='Lead', xp=350, side=1, min_level=1, classes=0, races=0}
            addon.routeObjectives[1] = {{'kill','Enemy',1,{[1455]={{.7,.7,'Enemy'}}}}}
        ''')
        self.command('tips on')
        tip = self.lua.globals().objects.AlfadorWowTravelTips
        tip.OnUpdate(tip, 2)
        self.assertEqual(len(self.lua.globals().messages), 1)
        self.lua.execute('x = .55')
        tip.OnUpdate(tip, 2)
        self.assertIn('Nearby: Lead', self.lua.globals().messages[2])
        self.lua.execute('x = .48; now = 500')
        tip.OnUpdate(tip, 2)
        self.lua.execute('x = .55')
        tip.OnUpdate(tip, 2)
        self.assertEqual(len(self.lua.globals().messages), 2)
        self.assertIsNone(self.lua.globals().waypoint)

    def test_rank_modes_filter_active_and_completed(self):
        self.lua.execute('''
            addon.pickupsByMap[1455] = {1, 2, 3, 4}
            addon.catalog[1] = {title='Closer', xp=20, side=1, min_level=1, classes=0, races=0, next={{2, 'all'}}}
            addon.catalog[2] = {title='More XP', xp=50, side=1, min_level=1, classes=0, races=0}
            addon.catalog[3] = {title='Active', xp=100, side=1, min_level=1, classes=0, races=0}
            addon.catalog[4] = {title='Done', xp=120, side=1, min_level=1, classes=0, races=0, repeatable=false}
            addon.pickupPoints[1455] = {
                [1]={{.48,.43,'Starter One'}}, [2]={{.6,.5,'Starter Two'}},
                [3]={{.48,.43,'Starter Three'}}, [4]={{.48,.43,'Starter Four'}},
            }
            C_QuestLog.IsOnQuest = function(id) return id == 3 end
            C_QuestLog.IsQuestFlaggedCompleted = function(id) return id == 4 end
        ''')
        nearby = self.command('nearby')
        xp = self.command('xp')
        self.assertLess(nearby.index('Closer'), nearby.index('More XP'))
        self.assertLess(xp.index('More XP'), xp.index('Closer'))
        self.assertNotIn('Active', xp)
        self.assertNotIn('Done', xp)
        self.assertIn('Catalog link to More XP', self.command('chains'))

    def test_story_works_without_a_position(self):
        self.lua.execute('C_Map.GetBestMapForUnit = function() return 1426 end; IsInInstance = function() return true end')
        body = self.command('lore')
        self.assertIn('Local story quests', body)
        self.assertIn('The Stolen Journal', body)
        self.assertIn('Grelin Whitebeard', body)
        self.assertNotIn('Set a waypoint', body)


class Lua51Guidance(GuidanceChecks, unittest.TestCase):
    runtime = Lua51


class Lua54Guidance(GuidanceChecks, unittest.TestCase):
    runtime = Lua54
