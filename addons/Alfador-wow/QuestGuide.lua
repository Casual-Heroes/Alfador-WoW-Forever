-- Local guidance only. WoW supplies journal progress; Polestar supplies reference names.
local _, addon = ...
local panel
local lookup
local sharing = false
local checkingCompletion = false
local showingOffers = false
local showingZone = false
local localView
local shownPickup
local navigator
local destination
local routeVoice = false
local lastSpeech
local tips
local seenTips = {}
local lastTip
local startQuestRoute
local showNavigatorSettings
local displayChoices = {card = true, portrait = true, arrow = true, portrait_arrow = true}
local displayModes = {{'card', 'Card', 86, 'Card'}, {'portrait', 'Portrait', 94, 'Portrait'},
    {'arrow', 'Arrow', 86, 'Arrow'}, {'portrait_arrow', 'Portrait + Arrow', 128, 'PortraitArrow'}}
local settingsCategory
local screenAnchors = {TOPLEFT = true, TOP = true, TOPRIGHT = true, LEFT = true, CENTER = true,
    RIGHT = true, BOTTOMLEFT = true, BOTTOM = true, BOTTOMRIGHT = true}

local function validArrowAnchor(point, relativePoint, x, y)
    return screenAnchors[point] and screenAnchors[relativePoint] and type(x) == 'number'
        and type(y) == 'number' and math.abs(x) <= 10000 and math.abs(y) <= 10000
end

local function displayPreferences()
    if type(AlfadorWowDisplay) ~= 'table' then AlfadorWowDisplay = {} end
    local prefs = AlfadorWowDisplay
    if not displayChoices[prefs.mode] then prefs.mode = 'card' end
    if type(prefs.always) ~= 'boolean' then prefs.always = true end
    if type(prefs.follow) ~= 'boolean' then prefs.follow = true end
    if type(prefs.scale) ~= 'number' or not (prefs.scale >= .75 and prefs.scale <= 1.5) then prefs.scale = 1 end
    return prefs
end

local function read(fn, ...)
    if type(fn) ~= 'function' or type(issecretvalue) ~= 'function' then return nil end
    local ok, value = pcall(fn, ...)
    if not ok or issecretvalue(value) then return nil end
    return value
end

local function reviewedClient()
    if type(GetBuildInfo) ~= 'function' or type(issecretvalue) ~= 'function' then return false end
    local ok, version, build, _, interface = pcall(GetBuildInfo)
    if not ok or issecretvalue(version) or issecretvalue(build) or issecretvalue(interface) then return false end
    return version == '1.60.1' and (build == '71037' or build == '70959') and interface == 16001, build
end

local function plain(value)
    return value:gsub('|', '||'):gsub('[%z\1-\31]', ' ')
end

local function title(id, liveTitle)
    local record = addon.catalog[id]
    return type(liveTitle) == 'string' and #liveTitle > 0 and #liveTitle <= 256 and liveTitle
        or (record and record.title) or ('Quest ' .. id)
end

local function status(value)
    if value == true then return 'Yes' end
    if value == false then return 'No' end
    return 'Unavailable'
end

local function completedListStatus(id)
    local ids = read(C_QuestLog.GetAllCompletedQuestIDs)
    if type(ids) ~= 'table' then return 'Unavailable' end
    local found, count = false, 0
    for key, value in next, ids do
        count = count + 1
        if count > 20000 or issecretvalue(key) or issecretvalue(value)
            or type(key) ~= 'number' or key < 1 or key % 1 ~= 0
            or type(value) ~= 'number' or value < 1 or value >= 10000000 or value % 1 ~= 0 then
            return 'Unavailable or exceeded check limit'
        end
        if value == id then found = true end
    end
    return found and 'Present' or 'Not listed'
end

local function completionText(id, build)
    if type(C_QuestLog) ~= 'table' then return 'Quest status unavailable.' end
    local turnedIn = read(C_QuestLog.IsQuestFlaggedCompleted, id)
    local inJournal = read(C_QuestLog.IsOnQuest, id)
    local lines = {
        'In your journal: ' .. status(inJournal),
        'Turned in (game flag): ' .. status(turnedIn),
    }
    if inJournal == true then
        lines[#lines + 1] = 'Objectives complete: ' .. status(read(C_QuestLog.IsComplete, id))
    end
    if checkingCompletion then
        lines[#lines + 1] = 'Completed quest list: ' .. completedListStatus(id)
        lines[#lines + 1] = 'Forever build: ' .. build
    end
    lines[#lines + 1] = 'Quest availability is unknown.'
    return table.concat(lines, '\n')
end

local function offeredQuests()
    if not GossipFrame or read(GossipFrame.IsShown, GossipFrame) ~= true then
        return 'Open a quest giver?s dialogue, then run this command again.'
    end
    local offers = read(C_GossipInfo and C_GossipInfo.GetAvailableQuests)
    if type(offers) ~= 'table' then return 'WoW did not expose the offers for this dialogue.' end

    local rows, seen, count = {}, {}, 0
    local partial = false
    for _, offer in next, offers do
        count = count + 1
        if count > 100 then return 'Too many offers to verify in this dialogue.' end
        if not issecretvalue(offer) and type(offer) == 'table' then
            local id = read(function() return offer.questID end)
            local name = read(function() return offer.title end)
            if type(id) == 'number' and id >= 1 and id < 10000000 and id % 1 == 0 then
                if not seen[id] then
                    seen[id] = true
                    rows[#rows + 1] = plain(title(id, name)) .. ' (ID ' .. id .. ')'
                end
            else
                partial = true
            end
        else
            partial = true
        end
    end
    if #rows == 0 then
        return partial and 'WoW did not expose a readable offer in this dialogue.'
            or 'This dialogue lists no available quests.'
    end
    table.sort(rows)
    if partial then rows[#rows + 1] = 'Some offers could not be read.' end
    return 'Available from this quest giver now\n\n' .. table.concat(rows, '\n')
end

local function playerId(fn)
    return read(function() return select(3, fn('player')) end)
end

local function matchesMask(mask, id)
    if mask == 0 then return true end
    if not mask or type(id) ~= 'number' or id < 1 or id > 53 or id % 1 ~= 0 then
        return nil
    end
    return math.floor(mask / (2 ^ (id - 1))) % 2 == 1
end

local function zoneQuestStatus(id, record, player)
    local inJournal = read(C_QuestLog.IsOnQuest, id)
    if inJournal == true then return 'journal' end
    local completed = read(C_QuestLog.IsQuestFlaggedCompleted, id)
    if completed == true and record.repeatable == false then return 'completed' end
    if completed == true and record.repeatable == nil then return 'prior' end
    if record.min_level and player.level and player.level < record.min_level then
        return 'excluded'
    end
    if record.side and record.side ~= 0 and player.side and record.side ~= player.side then
        return 'excluded'
    end
    local race = matchesMask(record.races, player.race)
    local class = matchesMask(record.classes, player.class)
    if race == false or class == false then return 'excluded' end

    local prerequisitesKnown = not record.complex_prereq
    for _, prerequisite in ipairs(record.requires or {}) do
        local done = read(C_QuestLog.IsQuestFlaggedCompleted, prerequisite)
        if done == false then return 'excluded' end
        if done ~= true then prerequisitesKnown = false end
    end
    if inJournal == false and completed == false and race == true and class == true
        and player.level and record.min_level and player.side and record.side
        and prerequisitesKnown then
        return 'matches'
    end
    return 'uncertain'
end

local function currentPlayer()
    local level = read(UnitLevel, 'player')
    local faction = read(UnitFactionGroup, 'player')
    return {
        level = type(level) == 'number' and level >= 1 and level <= 1000 and level % 1 == 0 and level or nil,
        side = faction == 'Alliance' and 1 or faction == 'Horde' and 2 or nil,
        race = playerId(UnitRace),
        class = playerId(UnitClass),
    }
end

local function validCoord(value)
    return type(value) == 'number' and value >= 0 and value <= 1
end

local function worldCorner(map, x, y)
    return read(function()
        local instance, point = C_Map.GetWorldPosFromMapPos(map, {x = x, y = y})
        if issecretvalue(instance) or issecretvalue(point) or not point then return end
        local wx, wy = point:GetXY()
        if issecretvalue(wx) or issecretvalue(wy) then return end
        if type(instance) == 'number' and type(wx) == 'number' and type(wy) == 'number' then
            return {instance, wx, wy}
        end
    end)
end

local function playerPosition(map, build)
    local frame = addon.pickupFrames[map]
    if build ~= '71037' or not frame or read(IsInInstance) ~= false then return end
    local first, last = worldCorner(map, 0, 0), worldCorner(map, 1, 1)
    if not first or not last or first[1] ~= frame[1] or last[1] ~= frame[1]
        or not (math.abs(first[2] - frame[2]) <= 2 and math.abs(first[3] - frame[3]) <= 2
            and math.abs(last[2] - frame[4]) <= 2 and math.abs(last[3] - frame[5]) <= 2) then return end
    return read(function()
        local point = C_Map.GetPlayerMapPosition(map, 'player')
        if issecretvalue(point) or not point then return end
        local x, y = point:GetXY()
        if issecretvalue(x) or issecretvalue(y) or not validCoord(x) or not validCoord(y) then return end
        if read(C_Map.GetBestMapForUnit, 'player') ~= map then return end
        return {x, y, math.abs(frame[5] - frame[3]), math.abs(frame[4] - frame[2])}
    end)
end

local function gameQuestWaypoint(id, map, build)
    if build ~= '71037' or type(map) ~= 'number' or read(IsInInstance) ~= false
        or type(C_QuestLog) ~= 'table' then return end
    return read(function()
        local waypointMap, x, y
        if type(C_QuestLog.GetNextWaypoint) == 'function' then
            waypointMap, x, y = C_QuestLog.GetNextWaypoint(id)
        end
        if issecretvalue(waypointMap) or issecretvalue(x) or issecretvalue(y) then return end
        if waypointMap ~= map and type(C_QuestLog.GetNextWaypointForMap) == 'function' then
            x, y = C_QuestLog.GetNextWaypointForMap(id, map)
            if issecretvalue(x) or issecretvalue(y) then return end
            if validCoord(x) and validCoord(y) then waypointMap = map end
        end
        if waypointMap == nil and type(C_QuestLog.GetQuestsOnMap) == 'function' then
            local pois = C_QuestLog.GetQuestsOnMap(map)
            if not issecretvalue(pois) and type(pois) == 'table' and #pois <= 200 then
                for _, poi in ipairs(pois) do
                    if not issecretvalue(poi) and type(poi) == 'table' and not issecretvalue(poi.questID)
                        and poi.questID == id and not issecretvalue(poi.x) and not issecretvalue(poi.y) then
                        waypointMap, x, y = map, poi.x, poi.y
                        break
                    end
                end
            end
        end
        if waypointMap ~= map or not validCoord(x) or not validCoord(y) then return end
        local width, height = C_Map.GetMapWorldSize(map)
        if issecretvalue(width) or issecretvalue(height) or type(width) ~= 'number' or type(height) ~= 'number'
            or not (width > 0 and width <= 50000 and height > 0 and height <= 50000) then return end
        local player = C_Map.GetPlayerMapPosition(map, 'player')
        if issecretvalue(player) or not player then return end
        local px, py = player.x, player.y
        if not issecretvalue(px) and not issecretvalue(py) and px == nil and py == nil and player.GetXY then
            px, py = player:GetXY()
        end
        if issecretvalue(px) or issecretvalue(py) or not validCoord(px) or not validCoord(py)
            or read(C_Map.GetBestMapForUnit, 'player') ~= map then return end
        return {{x, y, 'Tracked waypoint'}, {px, py, width, height}}
    end)
end

local function nearestPickup(points, position)
    if not points or not position then return end
    local best, shortest
    for _, point in ipairs(points) do
        local dx, dy = (point[1] - position[1]) * position[3], (point[2] - position[2]) * position[4]
        local distance = dx * dx + dy * dy
        if not shortest or distance < shortest then best, shortest = point, distance end
    end
    return best, shortest
end

local function placeNativeWaypoint(map, point)
    local waypoint = read(UiMapPoint and UiMapPoint.CreateFromCoordinates, map, point[1], point[2])
    return waypoint and read(C_Map.SetUserWaypoint, waypoint) == true
end

local function routeSpeech(text)
    if not routeVoice or not C_VoiceChat then return end
    local now = read(GetTime)
    if type(now) ~= 'number' or (lastSpeech and now - lastSpeech < 4) then return end
    local voices = read(C_VoiceChat.GetTtsVoices)
    local first = type(voices) == 'table' and read(function() return voices[1] end)
    local id = type(first) == 'table' and read(function() return first.voiceID end)
    if type(id) == 'number' then
        lastSpeech = now
        read(C_VoiceChat.SpeakText, id, text:gsub('[<>&|]', ''), 0, 80, false)
    end
end

local function objectiveStop(id, map, position)
    local catalog = addon.routeObjectives[id]
    local live = read(C_QuestLog.GetQuestObjectives, id)
    if not catalog or type(live) ~= 'table' then return end
    local length = read(function() return #live end)
    if length ~= #catalog or length == 0 or length > 24 then return end
    for index = 1, length do
        local observed = read(function() return live[index] end)
        local row = catalog[index]
        if row and row[2] and type(observed) == 'table' and read(function() return observed.finished end) == false then
            local description = read(function() return observed.text end)
            local required = read(function() return observed.numRequired end)
            if type(description) == 'string' and #description <= 512
                and description:lower():find(row[2]:lower(), 1, true)
                and (not row[3] or row[3] == required) then
                local point, distance = nearestPickup(row[4][map], position)
                if point then
                    local action = ({item = 'Collect', kill = 'Defeat', talk = 'Speak to', object = 'Find'})[row[1]]
                    return {id = id, point = point, distance = distance, key = 'objective:' .. id .. ':' .. index,
                        verb = action .. ' ' .. row[2], label = row[1] == 'item' and ('Source lead: ' .. point[3]) or point[3]}
                end
            end
        end
    end
end

local function routeStop(route, position)
    local pickup, work, finish, pending
    local player = currentPlayer()
    for _, entry in ipairs(route.entries) do
        local id = entry.id
        if entry.after and entry.after.skipped then entry.skipped = true end
        local inJournal = read(C_QuestLog.IsOnQuest, id)
        if not entry.done and not entry.skipped and inJournal == true then
            if not entry.accepted then entry.initialTurnIn = read(C_QuestLog.IsQuestFlaggedCompleted, id) end
            entry.accepted = true
            pending = true
            local complete = read(C_QuestLog.IsComplete, id)
            if complete == true then
                local mapPoints = addon.turninPoints[route.map] or {}
                local point, distance = nearestPickup(mapPoints[id], position)
                if point and (not finish or distance < finish.distance) then
                    finish = {id = id, point = point, distance = distance, key = 'turnin:' .. id,
                        verb = 'Turn in', label = point[3]}
                end
            elseif complete == false then
                local stop = objectiveStop(id, route.map, position)
                if stop and (not work or stop.distance < work.distance) then work = stop end
            end
        elseif not entry.done and not entry.skipped and inJournal == false then
            local turnedIn = read(C_QuestLog.IsQuestFlaggedCompleted, id)
            if turnedIn == true and (entry.initialTurnIn == false or addon.catalog[id].repeatable == false) then
                entry.done = true
            elseif not entry.accepted and not (entry.after and not entry.after.done) then
                local state = zoneQuestStatus(id, addon.catalog[id], player)
                if entry.point and (state == 'matches' or state == 'uncertain') then
                    pickup = pickup or {id = id, point = entry.point, key = 'pickup:' .. id,
                        verb = 'Check for pickup', label = entry.point[3]}
                else
                    pending = true
                end
            else
                pending = true
            end
        elseif not entry.done and not entry.skipped then
            pending = true
        end
    end
    return pickup or work or finish, pending
end

local function offeredByOpenNPC()
    if not GossipFrame or read(GossipFrame.IsShown, GossipFrame) ~= true then return end
    local name = read(UnitName, 'npc')
    local offers = read(C_GossipInfo and C_GossipInfo.GetAvailableQuests)
    if type(name) ~= 'string' or type(offers) ~= 'table' then return end
    local ids, count = {}, 0
    for _, row in next, offers do
        count = count + 1
        if count > 100 then return end
        if not issecretvalue(row) and type(row) == 'table' then
            local id = read(function() return row.questID end)
            if type(id) == 'number' then ids[id] = true end
        end
    end
    return name, ids
end

local function catalogTravel(id, map, pickup, distance, position)
    local objectives = addon.routeObjectives[id]
    if not objectives or #objectives == 0 or #objectives > 12 then return end
    local here = pickup
    local function onward(points)
        local nextPoint, leg = nearestPickup(points, {here[1], here[2], position[3], position[4]})
        if not nextPoint then return false end
        distance, here = distance + math.sqrt(leg), nextPoint
        return true
    end
    for _, step in ipairs(objectives) do
        if not onward(step[4][map]) then return end
    end
    local ends = addon.turninPoints[map]
    if onward(ends and ends[id]) then return distance end
end

local function nextQuestRecommendation(route, position)
    local excluded, followUps = {}, {}
    for _, entry in ipairs(route.entries) do excluded[entry.id] = true end
    for _, entry in ipairs(route.entries) do
        if entry.done then
            for _, link in ipairs(addon.catalog[entry.id].next or {}) do
                followUps[link[1]] = followUps[link[1]] or entry.id
            end
        end
    end
    local player = currentPlayer()
    local npc, offers = offeredByOpenNPC()
    local rows, best = {}, nil
    for id, points in pairs(addon.pickupPoints[route.map] or {}) do
        local record = addon.catalog[id]
        if record and not excluded[id] then
            local point, squared = nearestPickup(points, position)
            if point and squared <= 1200 * 1200 then
                local offered = offers and offers[id] and npc == point[3]
                local state = zoneQuestStatus(id, record, player)
                if state == 'matches' or (state == 'uncertain' and (offered or followUps[id])) then
                    rows[#rows + 1] = {id = id, point = point, distance = math.sqrt(squared), offered = offered,
                        followUp = followUps[id], record = record}
                end
            end
        end
    end
    for _, row in ipairs(rows) do
        row.travel = catalogTravel(row.id, route.map, row.point, row.distance, position)
        local xp = row.record.xp or 0
        -- Prefer worthwhile work close by. Derived distances are not ETAs.
        local cost = row.travel or (row.distance + 950)
        local story = row.record.story and (route.focus == 'story' and 3 or .4) or 0
        local chain = row.record.next and (route.focus == 'chains' and 2 or .35) or 0
        row.score = xp / (450 + cost) + story + chain + (row.followUp and 1.75 or 0)
            + (row.offered and 2 or 0)
        if not best or row.score > best.score or (row.score == best.score and row.id < best.id) then best = row end
    end
    return best
end

local function showCompletedRoute(target, position)
    local now = read(GetTime)
    if not target.recommendationChecked or (type(now) == 'number' and now - (target.recommendationAt or 0) >= 3) then
        target.recommendation = nextQuestRecommendation(target.route, position)
        target.recommendationChecked = true
        target.recommendationAt = now
    end
    local nextQuest = target.recommendation
    if not nextQuest then
        navigator.quest:SetText('Route complete')
        navigator.location:SetText('')
        navigator.status:SetText('No nearby pickup with enough evidence.')
        return
    end
    local instruction = (nextQuest.offered and 'Pick up from ' or 'Check with ') .. nextQuest.point[3]
    navigator.quest:SetText(plain(title(nextQuest.id)))
    navigator.location:SetText(plain(instruction))
    local reason = nextQuest.followUp and 'Catalog follow-up' or nextQuest.record.story and 'Story quest'
        or nextQuest.record.next and 'Quest chain lead'
    local detail = string.format('%s%d yd to pickup', nextQuest.record.xp and (nextQuest.record.xp .. ' listed XP / ') or '',
        math.floor(nextQuest.distance + 0.5))
    navigator.distance:SetText(string.format('~%d yd to pickup', math.floor(nextQuest.distance + 0.5)))
    if nextQuest.travel then detail = detail .. string.format('\n~%d yd across mapped stops', math.floor(nextQuest.travel + 0.5)) end
    navigator.status:SetText('Route complete\n' .. (reason and (reason .. '\n') or '') .. detail)
    if displayPreferences().mode == 'card' then navigator.nextQuest:Show() end
    if not target.announced.complete then
        target.announced.complete = true
        routeSpeech('Route complete. ' .. instruction .. ' for ' .. title(nextQuest.id) .. '.')
    end
end

local function refreshRoute(target, position)
    local stop, pending = routeStop(target.route, position)
    if not stop then
        target.stop = nil
        local skipped = false
        for _, entry in ipairs(target.route.entries) do skipped = skipped or entry.skipped end
        if pending or skipped then
            navigator.status:SetText(pending and 'Route step unavailable. Check your quest journal.'
                or 'Route ended. Some quests were skipped.')
        else
            showCompletedRoute(target, position)
        end
        return
    end
    if target.stop and target.stop.key == stop.key then return target.stop end
    target.stop = stop
    navigator.quest:SetText(plain(title(stop.id)))
    navigator.location:SetText(plain(stop.label))
    -- Update only our previous pin. A player-selected pin takes precedence.
    local hasWaypoint = read(C_Map.HasUserWaypoint)
    local previous = hasWaypoint == true and read(C_Map.GetUserWaypoint)
    local ownsWaypoint = previous and target.owned and read(function()
        if previous.uiMapID ~= target.map then return false end
        local x, y = previous.position:GetXY()
        if issecretvalue(x) or issecretvalue(y) then return false end
        return type(x) == 'number' and type(y) == 'number'
            and math.abs(x - target.owned[1]) < 0.00001 and math.abs(y - target.owned[2]) < 0.00001
    end)
    if (hasWaypoint == false or ownsWaypoint == true) and placeNativeWaypoint(target.map, stop.point) then
        target.owned = stop.point
    end
    if not target.announced[stop.key] then
        target.announced[stop.key] = true
        routeSpeech(stop.verb .. '. ' .. title(stop.id) .. '. ' .. stop.label)
    end
    return stop
end

local function updateNavigation()
    navigator.arrow:Hide()
    navigator.pinStop:Hide()
    navigator.skipStop:Hide()
    navigator.nextQuest:Hide()
    navigator.distance:SetText('Distance unavailable')
    local target = destination
    if not target then
        navigator.quest:SetText('Track a quest to start')
        navigator.location:SetText('')
        navigator.status:SetText('')
        navigator.distance:SetText('No quest tracked')
        return
    end
    local combat = read(InCombatLockdown)
    if combat == nil then
        navigator.status:SetText('Navigation temporarily unavailable')
        return
    end
    if not combat and not target.route and not target.tracked and read(C_QuestLog and C_QuestLog.IsOnQuest, target.id) == true then
        navigator.status:SetText('Quest accepted. Check your journal for objectives.')
        return
    end
    if not combat and not target.route and not target.tracked and addon.catalog[target.id].repeatable == false
        and read(C_QuestLog and C_QuestLog.IsQuestFlaggedCompleted, target.id) == true then
        navigator.status:SetText('Quest turned in')
        return
    end
    local map = read(C_Map and C_Map.GetBestMapForUnit, 'player')
    local tracked = target.tracked and gameQuestWaypoint(target.id, map, target.build)
    local position = tracked and tracked[2] or (target.tracked or map == target.map) and playerPosition(map, target.build)
    if not position then
        navigator.status:SetText('Direction unavailable on this map')
        return
    end
    local stop
    if target.route then
        if combat then
            stop = target.stop
            if not stop then
                navigator.status:SetText('No navigation stop selected')
                return
            end
        else
            stop = refreshRoute(target, position)
            if not stop then return end
        end
    end
    if stop and not combat and displayPreferences().mode == 'card' then
        navigator.pinStop:Show()
        navigator.skipStop:Show()
    end
    local point = tracked and tracked[1] or stop and stop.point or target.point
    if target.tracked and not tracked and not combat then
        local ready = read(C_QuestLog and C_QuestLog.IsComplete, target.id)
        if ready == true then
            point = nearestPickup((addon.turninPoints[map] or {})[target.id], position)
        elseif ready == false and read(C_QuestLog and C_QuestLog.IsOnQuest, target.id) == true then
            local objective = objectiveStop(target.id, map, position)
            point = objective and objective.point
        end
    end
    if not point then
        navigator.location:SetText('')
        navigator.status:SetText('WoW has no readable destination on this map')
        return
    end
    if target.tracked then navigator.location:SetText(plain(point[3])) end
    local west = (position[1] - point[1]) * position[3]
    local north = (position[2] - point[2]) * position[4]
    local distance = math.sqrt(west * west + north * north)
    navigator.distance:SetText(string.format('~%d yd', math.floor(distance + 0.5)))
    if distance <= 20 then
        navigator.status:SetText(stop and ('At the stop. ' .. plain(stop.verb)) or 'Near the pickup. Check the quest giver.')
        if stop and not combat and not target.announced['at:' .. stop.key] then
            target.announced['at:' .. stop.key] = true
            routeSpeech('You are near your next stop. ' .. stop.verb .. '.')
        end
        return
    end
    local facing = read(GetPlayerFacing)
    if displayPreferences().mode ~= 'portrait' and type(facing) == 'number' and facing >= 0 and facing <= 2 * math.pi then
        local atan2 = math.atan2 or math.atan
        navigator.arrow:SetRotation(atan2(west, north) - facing)
        navigator.arrow:Show()
    end
    local distanceText = string.format('~%d yd straight line', math.floor(distance + 0.5))
    navigator.status:SetText(stop and (plain(stop.verb) .. '\n' .. distanceText) or distanceText)
end

local function layoutNavigator()
    local prefs = displayPreferences()
    local card, portrait = prefs.mode == 'card', prefs.mode == 'portrait'
    local combined = prefs.mode == 'portrait_arrow'
    navigator:SetSize(card and 362 or 128, card and 163 or (portrait or combined) and 133 or 81)
    navigator:SetBackdropColor(0.054, 0.032, 0.087, card and .96 or 0)
    for _, widget in ipairs(navigator.cardElements) do
        if card then widget:Show() else widget:Hide() end
    end
    if card or portrait or combined then navigator.portrait:Show(); navigator.janus:Show()
    else navigator.portrait:Hide(); navigator.janus:Hide() end
    local direction = navigator.direction
    direction:ClearAllPoints()
    direction:EnableMouse(combined)
    navigator.arrow:ClearAllPoints()
    navigator.distance:ClearAllPoints()
    if combined then
        direction:SetSize(116, 72)
        local anchor = prefs.arrowAnchor
        if type(anchor) == 'table' and validArrowAnchor(anchor.point, anchor.relativePoint, anchor.x, anchor.y) then
            direction:SetPoint(anchor.point, UIParent, anchor.relativePoint, anchor.x, anchor.y)
        else
            direction:SetPoint('TOP', navigator.portrait, 'BOTTOM', 0, -3)
        end
        navigator.arrow:SetPoint('TOP', 0, -1)
        navigator.distance:SetPoint('BOTTOM', 0, 5)
    else
        direction:SetAllPoints(navigator)
        navigator.arrow:SetPoint('BOTTOMRIGHT', card and -5 or -39, card and 4 or 25)
        if card then navigator.distance:SetPoint('BOTTOMRIGHT', -8, 55)
        else navigator.distance:SetPoint('BOTTOM', 0, 4) end
    end
end

local function startNavigation(id, map, point, build, route, tracked)
    if not navigator then
        local media = 'Interface\\AddOns\\Alfador-wow\\Media\\'
        navigator = CreateFrame('Frame', 'AlfadorWowNavigator', UIParent, 'BackdropTemplate')
        navigator:SetSize(362, 163)
        navigator:SetPoint('TOP', 0, -155)
        navigator:SetFrameStrata('MEDIUM')
        navigator:SetBackdrop({bgFile = 'Interface\\Buttons\\WHITE8X8'})
        navigator:SetBackdropColor(0.054, 0.032, 0.087, 0.96)
        navigator:SetClampedToScreen(true)
        navigator:SetMovable(true)
        navigator:EnableMouse(true)
        navigator:RegisterForDrag('LeftButton')
        navigator:SetScript('OnDragStart', navigator.StartMoving)
        navigator:SetScript('OnDragStop', navigator.StopMovingOrSizing)
        navigator:EnableMouseWheel(true)
        navigator:SetScript('OnMouseWheel', function(frame, delta)
            frame:SetScale(math.max(0.75, math.min(1.5, frame:GetScale() + delta * 0.1)))
            displayPreferences().scale = frame:GetScale()
        end)
        navigator:SetScript('OnMouseUp', function(_, button)
            if button == 'RightButton' then showNavigatorSettings() end
        end)
        navigator:SetScale(displayPreferences().scale)

        local portrait = navigator:CreateTexture(nil, 'ARTWORK')
        portrait:SetPoint('TOPLEFT', 10, -10)
        portrait:SetSize(109, 109)
        portrait:SetTexture(media .. 'Alfador.tga')
        portrait:SetTexCoord(0.15, 0.85, 0.07, 0.77)
        local janus = navigator:CreateTexture(nil, 'OVERLAY')
        -- Match the Desktop familiar's anchor on the portrait, including its crop.
        janus:SetPoint('TOPLEFT', portrait, 'TOPLEFT', 22, -65)
        janus:SetSize(21, 21)
        janus:SetTexture(media .. 'Janus.tga')
        navigator.portrait, navigator.janus = portrait, janus
        local accent = navigator:CreateTexture(nil, 'ARTWORK')
        accent:SetPoint('TOPLEFT', 126, -11)
        accent:SetSize(2, 111)
        accent:SetColorTexture(0.60, 0.30, 0.88, 0.8)
        local direction = CreateFrame('Frame', nil, navigator)
        direction:SetMovable(true)
        direction:SetClampedToScreen(true)
        direction:RegisterForDrag('LeftButton')
        direction:SetScript('OnDragStart', function(frame)
            if displayPreferences().mode == 'portrait_arrow' then frame:StartMoving() end
        end)
        direction:SetScript('OnDragStop', function(frame)
            frame:StopMovingOrSizing()
            local point, relative, relativePoint, x, y = frame:GetPoint(1)
            if (relative == UIParent or relative == nil) and validArrowAnchor(point, relativePoint, x, y) then
                displayPreferences().arrowAnchor = {point = point, relativePoint = relativePoint, x = x, y = y}
            end
        end)
        direction:SetScript('OnMouseUp', function(_, button)
            if button == 'RightButton' then showNavigatorSettings() end
        end)
        navigator.direction = direction
        local arrow = direction:CreateTexture(nil, 'OVERLAY')
        arrow:SetSize(50, 50)
        arrow:SetPoint('BOTTOMRIGHT', -5, 4)
        arrow:SetTexture(media .. 'Direction.tga')
        navigator.arrow = arrow

        local label = navigator:CreateFontString(nil, 'OVERLAY', 'GameFontNormal')
        label:SetPoint('TOPLEFT', 140, -12)
        label:SetTextColor(0.85, 0.64, 1)
        label:SetText('Alfador')
        local quest = navigator:CreateFontString(nil, 'OVERLAY', 'GameFontHighlight')
        quest:SetPoint('TOPLEFT', label, 'BOTTOMLEFT', 0, -5)
        quest:SetWidth(201)
        quest:SetJustifyH('LEFT')
        navigator.quest = quest
        local location = navigator:CreateFontString(nil, 'OVERLAY', 'GameFontHighlightSmall')
        location:SetPoint('TOPLEFT', quest, 'BOTTOMLEFT', 0, -5)
        location:SetWidth(195)
        location:SetJustifyH('LEFT')
        location:SetTextColor(0.81, 0.72, 0.91)
        navigator.location = location
        local statusText = navigator:CreateFontString(nil, 'OVERLAY', 'GameFontHighlightSmall')
        statusText:SetPoint('TOPLEFT', location, 'BOTTOMLEFT', 0, -6)
        statusText:SetWidth(169)
        statusText:SetJustifyH('LEFT')
        navigator.status = statusText
        local distance = direction:CreateFontString(nil, 'OVERLAY', 'GameFontNormal')
        navigator.distance = distance

        local close = CreateFrame('Button', nil, navigator, 'UIPanelCloseButton')
        close:SetPoint('TOPRIGHT', 1, 1)
        close:SetScript('OnClick', function()
            displayPreferences().always = false
            navigator:Hide()
            if settingsCategory and type(Settings.NotifyUpdate) == 'function' then
                Settings.NotifyUpdate('AlfadorWowAlwaysShow')
            end
        end)
        navigator.cardElements = {accent, label, quest, location, statusText, close}
        local function routeButton(label, offset, action)
            local button = CreateFrame('Button', nil, navigator, 'UIPanelButtonTemplate')
            button:SetSize(80, 22)
            button:SetPoint('BOTTOMLEFT', offset, 7)
            button:SetText(label)
            button:SetScript('OnClick', function()
                local target = destination
                if not target or not target.route or read(InCombatLockdown) ~= false then return end
                local map = read(C_Map and C_Map.GetBestMapForUnit, 'player')
                if map ~= target.map then return end
                updateNavigation()
                if button:IsShown() and target.stop then action(target) end
            end)
            return button
        end
        navigator.pinStop = routeButton('Pin stop', 137, function(target)
            if placeNativeWaypoint(target.map, target.stop.point) then target.owned = target.stop.point end
        end)
        navigator.skipStop = routeButton('Skip quest', 223, function(target)
            for _, entry in ipairs(target.route.entries) do
                if entry.id == target.stop.id then entry.skipped = true end
            end
            updateNavigation()
        end)
        local nextQuest = CreateFrame('Button', nil, navigator, 'UIPanelButtonTemplate')
        nextQuest:SetSize(115, 22)
        nextQuest:SetPoint('BOTTOMLEFT', 137, 7)
        nextQuest:SetText('Guide me there')
        nextQuest:SetScript('OnClick', function()
            local target = destination
            if not target or read(InCombatLockdown) ~= false then return end
            updateNavigation()
            if nextQuest:IsShown() and target.recommendation then
                DEFAULT_CHAT_FRAME:AddMessage('Alfador-wow: ' .. startQuestRoute(tostring(target.recommendation.id), target.route.focus))
            end
        end)
        navigator.nextQuest = nextQuest
        navigator:RegisterEvent('QUEST_TURNED_IN')
        navigator:SetScript('OnEvent', function(_, _, questID)
            if not destination or not destination.route or issecretvalue(questID) then return end
            for _, entry in ipairs(destination.route.entries) do
                if entry.id == questID then entry.done = true end
            end
        end)
        navigator:SetScript('OnHide', function() destination = nil end)
        navigator:SetScript('OnUpdate', function(frame, elapsed)
            frame.elapsed = (frame.elapsed or 0) + elapsed
            if frame.elapsed < 0.5 then return end
            frame.elapsed = 0
            updateNavigation()
        end)
    end
    destination = id and {id = id, map = map, point = point, build = build, route = route, tracked = tracked,
        announced = {}} or nil
    local liveTitle = id and read(C_QuestLog and C_QuestLog.GetTitleForQuestID, id)
    navigator.quest:SetText(id and plain(title(id, liveTitle)) or '')
    navigator.location:SetText(point and plain(point[3]) or '')
    navigator.elapsed = 0
    layoutNavigator()
    navigator:Show()
    updateNavigation()
end

local function followTrackedQuest()
    local reviewed, build = reviewedClient()
    if not reviewed then return end
    local prefs = displayPreferences()
    if prefs.follow then
        local id = read(C_SuperTrack and C_SuperTrack.GetSuperTrackedQuestID)
        if type(id) == 'number' and id > 0 and id < 10000000 and id % 1 == 0 then
            if not destination or destination.id ~= id then
                startNavigation(id, nil, nil, build, nil, true)
            end
            return
        end
        if destination and destination.tracked then
            if prefs.always then startNavigation() else navigator:Hide() end
        end
    end
    if not destination and prefs.always then startNavigation() end
end

local settingsFrame
local function setDisplayMode(value)
    if not displayChoices[value] then return end
    displayPreferences().mode = value
    if navigator and navigator:IsShown() then layoutNavigator(); updateNavigation() end
end

local function setAlwaysShow(value)
    displayPreferences().always = value
    if value then followTrackedQuest()
    elseif navigator and not destination then navigator:Hide() end
end

local function setFollowTracked(value)
    local prefs = displayPreferences()
    prefs.follow = value
    if value then followTrackedQuest()
    elseif destination and destination.tracked then
        if prefs.always then startNavigation() else navigator:Hide() end
    end
end

local function registerNavigatorSettings()
    if settingsCategory or type(Settings) ~= 'table' then return end
    for _, api in ipairs({'RegisterVerticalLayoutCategory', 'RegisterAddOnCategory', 'RegisterProxySetting',
        'CreateDropdown', 'CreateCheckbox', 'CreateControlTextContainer', 'OpenToCategory'}) do
        if type(Settings[api]) ~= 'function' then return end
    end
    local category = Settings.RegisterVerticalLayoutCategory('Alfador-wow')
    local mode = Settings.RegisterProxySetting(category, 'AlfadorWowDisplayMode', 'string', 'Display mode', 'card',
        function() return displayPreferences().mode end, setDisplayMode)
    Settings.CreateDropdown(category, mode, function()
        local options = Settings.CreateControlTextContainer()
        for _, entry in ipairs(displayModes) do options:Add(entry[1], entry[2]) end
        return options:GetData()
    end, 'Choose how Alfador shows your quest direction and distance.')
    local always = Settings.RegisterProxySetting(category, 'AlfadorWowAlwaysShow', 'boolean', 'Always show', true,
        function() return displayPreferences().always end, setAlwaysShow)
    Settings.CreateCheckbox(category, always, 'Keep Alfador on screen between quests.')
    local follow = Settings.RegisterProxySetting(category, 'AlfadorWowFollowTracked', 'boolean', 'Follow tracked quests', true,
        function() return displayPreferences().follow end, setFollowTracked)
    Settings.CreateCheckbox(category, follow, 'Use the quest selected in the WoW tracker as your navigation target.')
    Settings.RegisterAddOnCategory(category)
    settingsCategory = category
end

showNavigatorSettings = function()
    registerNavigatorSettings()
    if settingsCategory then
        Settings.OpenToCategory(settingsCategory:GetID())
        return
    end
    if not settingsFrame then
        local frame = CreateFrame('Frame', 'AlfadorWowDisplaySettings', UIParent, 'BackdropTemplate')
        frame:SetSize(438, 160)
        frame:SetPoint('CENTER')
        frame:SetFrameStrata('DIALOG')
        frame:SetBackdrop({bgFile = 'Interface\\Buttons\\WHITE8X8'})
        frame:SetBackdropColor(0.075, 0.04, 0.12, 0.97)
        local heading = frame:CreateFontString(nil, 'OVERLAY', 'GameFontNormalLarge')
        heading:SetPoint('TOP', 0, -14)
        heading:SetText('Alfador navigator')
        local close = CreateFrame('Button', nil, frame, 'UIPanelCloseButton')
        close:SetPoint('TOPRIGHT')
        close:SetScript('OnClick', function() frame:Hide() end)
        local function button(text, x, y, width, action, name)
            local control = CreateFrame('Button', name, frame, 'UIPanelButtonTemplate')
            control:SetSize(width, 24)
            control:SetPoint('TOPLEFT', x, y)
            control:SetText(text)
            control:SetScript('OnClick', action)
            return control
        end
        local controls = {}
        local function refreshSettings()
            local prefs = displayPreferences()
            for _, mode in ipairs(displayModes) do
                controls[mode[1]]:SetText(mode[2] .. (prefs.mode == mode[1] and ' (on)' or ''))
            end
            frame.always:SetText('Always show: ' .. (prefs.always and 'on' or 'off'))
            frame.follow:SetText('Follow tracked quests: ' .. (prefs.follow and 'on' or 'off'))
        end
        local x = 13
        for _, mode in ipairs(displayModes) do
            local value = mode[1]
            controls[value] = button(mode[2], x, -46, mode[3], function()
                setDisplayMode(value)
                refreshSettings()
            end, 'AlfadorWowMode' .. mode[4])
            x = x + mode[3] + 6
        end
        frame.always = button('', 13, -79, 412, function()
            setAlwaysShow(not displayPreferences().always)
            refreshSettings()
        end)
        frame.follow = button('', 13, -110, 412, function()
            setFollowTracked(not displayPreferences().follow)
            refreshSettings()
        end)
        frame.refresh = refreshSettings
        settingsFrame = frame
    end
    settingsFrame.refresh()
    settingsFrame:Show()
end

local trackingEvents = CreateFrame('Frame', 'AlfadorWowTrackingEvents')
trackingEvents:RegisterEvent('ADDON_LOADED')
trackingEvents:RegisterEvent('PLAYER_ENTERING_WORLD')
trackingEvents:RegisterEvent('SUPER_TRACKING_CHANGED')
trackingEvents:SetScript('OnEvent', function(_, event, loadedAddon)
    if event == 'ADDON_LOADED' then
        if loadedAddon == 'Alfador-wow' then registerNavigatorSettings() end
        return
    end
    if event == 'PLAYER_ENTERING_WORLD' then registerNavigatorSettings() end
    followTrackedQuest()
end)

local function questDetails(record)
    local lines = {}
    if record.xp and record.xp > 0 then lines[#lines + 1] = record.xp .. ' listed XP' end
    if record.money_copper and record.money_copper > 0 then
        local copper = record.money_copper
        lines[#lines + 1] = string.format('Listed coin: %dg %ds %dc', math.floor(copper / 10000),
            math.floor(copper / 100) % 100, copper % 100)
    end
    if record.item then lines[#lines + 1] = 'Listed items: ' .. plain(record.item) end
    if record.choice then lines[#lines + 1] = 'Choose one: ' .. plain(record.choice) end
    for _, link in ipairs(record.next or {}) do
        if addon.catalog[link[1]] then
            local suffix = link[1] == 2926 and ' (Gnomeregan quest)' or ''
            local label = link[2] == 'breadcrumb' and 'Catalog breadcrumb to ' or 'Catalog link to '
            lines[#lines + 1] = label .. plain(title(link[1])) .. suffix
        end
    end
    return lines
end

local function pickupLine(point)
    return string.format('Check pickup at %s (%.1f, %.1f)', plain(point[3]), point[1] * 100, point[2] * 100)
end

local function localQuestList(build)
    if type(C_QuestLog) ~= 'table' then return 'Quest journal unavailable.' end
    local map = read(C_Map and C_Map.GetBestMapForUnit, 'player')
    local candidates = addon.pickupsByMap[map]
    if not candidates or #candidates > 1200 then return 'No local quest list for this map.' end
    local position = playerPosition(map, build)
    local points = addon.pickupPoints[map] or {}
    if localView ~= 'lore' and not position then
        return 'Comparable outdoor position is unavailable. Use /alfadorwowguide zone for zone-wide leads.'
    end

    local player = currentPlayer()
    local rows = {}
    for _, id in ipairs(candidates) do
        local record = addon.catalog[id]
        if (localView ~= 'lore' or record.story) and (localView ~= 'chains' or record.next) then
            local state = zoneQuestStatus(id, record, player)
            local point, distance = nearestPickup(points[id], position)
            if localView == 'lore' or (state == 'matches' or state == 'uncertain')
                and point and distance <= 1200 * 1200 then
                rows[#rows + 1] = {id = id, record = record, state = state, point = point, distance = distance}
            end
        end
    end
    table.sort(rows, function(a, b)
        if localView == 'xp' and (a.record.xp or 0) ~= (b.record.xp or 0) then
            return (a.record.xp or 0) > (b.record.xp or 0)
        end
        if (a.distance or math.huge) ~= (b.distance or math.huge) then
            return (a.distance or math.huge) < (b.distance or math.huge)
        end
        return a.id < b.id
    end)
    local headings = {nearby = 'Nearby quest leads', xp = 'Nearby quests by listed XP',
        chains = 'Nearby quests with follow-up links', lore = 'Local story quests'}
    local lines = {headings[localView]}
    if #rows == 0 then
        return lines[1] .. (localView == 'lore' and '\nNo reviewed story notes for this area.' or '\nNo eligible catalog leads within the pilot range.')
    end
    lines[#lines + 1] = 'Catalog pickups and rewards. Check offers in the NPC dialogue.'
    for i = 1, math.min(#rows, 12) do
        local row = rows[i]
        lines[#lines + 1] = '\n' .. plain(title(row.id)) .. ' (ID ' .. row.id .. ')'
        if row.record.story and localView == 'lore' then lines[#lines + 1] = plain(row.record.story) end
        if row.state ~= 'matches' then
            local labels = {journal = 'Already in your journal', completed = 'Turned in',
                prior = 'Previously turned in. Repeatability unavailable.',
                excluded = 'Does not match current catalog checks', uncertain = 'Availability needs more evidence'}
            lines[#lines + 1] = labels[row.state]
        end
        if row.point and (row.state == 'matches' or row.state == 'uncertain') then
            lines[#lines + 1] = pickupLine(row.point)
            shownPickup = shownPickup or {id = row.id, map = map}
        end
        for _, detail in ipairs(questDetails(row.record)) do lines[#lines + 1] = detail end
    end
    if shownPickup then lines[#lines + 1] = '\nUse Pin first pickup, or /alfadorwowguide pin <quest ID> for another lead.' end
    return table.concat(lines, '\n')
end

local function setPickupPin(id, build, expectedMap)
    if type(C_QuestLog) ~= 'table' then return 'Quest journal unavailable.' end
    local map = read(C_Map and C_Map.GetBestMapForUnit, 'player')
    if expectedMap and map ~= expectedMap then return 'Your map changed. Refresh the guide first.' end
    local position = playerPosition(map, build)
    local points = addon.pickupPoints[map]
    local record = addon.catalog[id]
    local point = record and points and nearestPickup(points[id], position)
    if not point then return 'A comparable pickup point is unavailable on your current map.' end
    local state = zoneQuestStatus(id, record, currentPlayer())
    if state ~= 'matches' and state ~= 'uncertain' then return 'This quest is not a current pickup lead.' end
    startNavigation(id, map, point, build)
    local waypoint = read(UiMapPoint and UiMapPoint.CreateFromCoordinates, map, point[1], point[2])
    if waypoint and read(C_Map.SetUserWaypoint, waypoint) == true then return 'Waypoint set. ' .. pickupLine(point) end
    local tomtom = _G.TomTom
    if type(tomtom) == 'table' and read(tomtom.AddWaypoint, tomtom, map, point[1], point[2],
        {title = title(id)}) then return 'Waypoint set. ' .. pickupLine(point) end
    return 'Waypoint unavailable. ' .. pickupLine(point)
end

local function requestPickupPin(id, expectedMap)
    local reviewed, build = reviewedClient()
    local message = reviewed and read(InCombatLockdown) == false and setPickupPin(id, build, expectedMap)
        or 'Pickup waypoints are unavailable on this build or during combat.'
    DEFAULT_CHAT_FRAME:AddMessage('Alfador-wow: ' .. message)
end

local function mappedObjectives(id, map)
    local result = {}
    for _, objective in pairs(addon.routeObjectives[id] or {}) do
        for _, point in ipairs(objective[4][map] or {}) do result[#result + 1] = point end
    end
    return result
end

local function sharesObjectiveArea(first, other, position)
    for _, point in ipairs(first) do
        local frame = {point[1], point[2], position[3], position[4]}
        local _, distance = nearestPickup(other, frame)
        if distance and distance <= 120 * 120 then return true end
    end
    return false
end

startQuestRoute = function(mode, followFocus)
    local reviewed, build = reviewedClient()
    if not reviewed or read(InCombatLockdown) ~= false or type(C_QuestLog) ~= 'table' then
        return 'Open routing outside combat on a supported client.'
    end
    local map = read(C_Map and C_Map.GetBestMapForUnit, 'player')
    local position = playerPosition(map, build)
    if not position then return 'Route coordinates are unavailable on this map.' end
    local pickups = addon.pickupPoints[map] or {}
    local turnins = addon.turninPoints[map] or {}
    local player = currentPlayer()
    local wanted = tonumber(mode)
    local rows, seen = {}, {}
    local function add(id)
        if seen[id] or (wanted and id ~= wanted) then return end
        seen[id] = true
        local record = addon.catalog[id]
        if not record or (mode == 'story' and not record.story) or (mode == 'chains' and not record.next) then return end
        local state = zoneQuestStatus(id, record, player)
        if state ~= 'matches' and state ~= 'uncertain' and state ~= 'journal' then return end
        local point, distance = nearestPickup(pickups[id], position)
        if state ~= 'journal' and (not point or (not wanted and distance > 1200 * 1200)) then return end
        local work = mappedObjectives(id, map)
        if not wanted and #work == 0 and (state ~= 'journal' or not turnins[id]) then return end
        if state == 'journal' then
            local _, remainingDistance = nearestPickup(#work > 0 and work or turnins[id], position)
            distance = remainingDistance
        end
        rows[#rows + 1] = {id = id, point = point, distance = distance or math.huge, state = state, work = work}
    end
    if wanted then
        local quest = addon.catalog[wanted]
        local prior = quest and zoneQuestStatus(wanted, quest, player)
        if prior == 'prior' or prior == 'completed' then
            return plain(title(wanted)) .. ' is marked turned in by WoW.'
        end
        add(wanted)
    else
        for id in pairs(pickups) do add(id) end
        local count = read(C_QuestLog.GetNumQuestLogEntries)
        if type(count) == 'number' and count >= 0 and count <= 200 then
            for index = 1, count do
                local info = read(C_QuestLog.GetInfo, index)
                local id = type(info) == 'table' and read(function() return info.questID end)
                if type(id) == 'number' then add(id) end
            end
        end
    end
    table.sort(rows, function(a, b)
        if (a.state == 'journal') ~= (b.state == 'journal') then return a.state == 'journal' end
        if mode == 'xp' then
            local ax, bx = addon.catalog[a.id].xp or 0, addon.catalog[b.id].xp or 0
            if ax ~= bx then return ax > bx end
        end
        if a.distance ~= b.distance then return a.distance < b.distance end
        return a.id < b.id
    end)
    local first = rows[1]
    if not first then return 'No route lead with usable evidence here. Try /alfadorwowguide nearby.' end
    local route = {map = map, entries = {first}, focus = followFocus or mode}
    if mode == 'story' then
        for _, link in ipairs(addon.catalog[first.id].next or {}) do
            local id = link[1]
            local record = addon.catalog[id]
            local point = nearestPickup(pickups[id], position)
            if record and record.story and point then
                route.entries[2] = {id = id, point = point, after = first}
                break
            end
        end
    elseif not wanted then
        local anchor = first.point and {first.point[1], first.point[2], position[3], position[4]} or position
        for i = 2, #rows do
            local row = rows[i]
            local _, distance = nearestPickup(row.point and {row.point}, anchor)
            local pickupNear = row.state == 'journal' or (distance and distance <= 350 * 350)
            if pickupNear and sharesObjectiveArea(first.work, row.work, position) then
                route.entries[#route.entries + 1] = row
                if #route.entries == 3 then break end
            end
        end
    end
    startNavigation(first.id, map, first.point, build, route)
    local names = {}
    for _, entry in ipairs(route.entries) do names[#names + 1] = plain(title(entry.id)) end
    local reason = mode == 'story' and 'Story route: ' or #names > 1 and 'Shared objective area: ' or 'Route: '
    local record = addon.catalog[first.id]
    local context = mode == 'story' and (' ' .. plain(record.story))
        or (record.xp and (' ' .. record.xp .. ' listed XP for the first quest.') or '')
    return reason .. table.concat(names, ', ') .. '.' .. context
end

local function updateTravelTips(frame)
    local reviewed, build = reviewedClient()
    if not reviewed or destination or read(InCombatLockdown) ~= false then
        frame.previous = nil
        return
    end
    local map = read(C_Map and C_Map.GetBestMapForUnit, 'player')
    local position = playerPosition(map, build)
    local previous = frame.previous
    frame.previous = position and {map = map, position = position} or nil
    if not position or not previous or map ~= previous.map or type(C_QuestLog) ~= 'table' then return end
    local dx = (previous.position[1] - position[1]) * position[3]
    local dy = (previous.position[2] - position[2]) * position[4]
    local moved = dx * dx + dy * dy
    if moved == 0 or moved > 100 * 100 then return end
    local now = read(GetTime)
    if type(now) ~= 'number' or (lastTip and now - lastTip < 300) then return end

    local player = currentPlayer()
    local best
    for id, points in pairs(addon.pickupPoints[map] or {}) do
        local record = addon.catalog[id]
        if not seenTips[id] and record and (record.story or record.next or (record.xp or 0) >= 300)
            and addon.routeObjectives[id] then
            local point, distance = nearestPickup(points, position)
            local _, oldDistance = nearestPickup(points, previous.position)
            if distance and distance <= 75 * 75 and oldDistance > 90 * 90
                and zoneQuestStatus(id, record, player) == 'matches'
                and (not best or distance < best.distance or (distance == best.distance and id < best.id)) then
                best = {id = id, point = point, distance = distance}
            end
        end
    end
    if best then
        lastTip = now
        seenTips[best.id] = true
        local record = addon.catalog[best.id]
        local message = 'Nearby: ' .. plain(title(best.id)) .. '. ' .. pickupLine(best.point) .. '.'
        if record.xp and record.xp > 0 then message = message .. ' ' .. record.xp .. ' listed XP.' end
        DEFAULT_CHAT_FRAME:AddMessage('Alfador-wow: ' .. message .. ' /alfadorwowguide route ' .. best.id)
        routeSpeech(message)
    end
end

local function setTravelTips(enabled)
    if enabled and not tips then
        tips = CreateFrame('Frame', 'AlfadorWowTravelTips', UIParent)
        tips:SetScript('OnUpdate', function(frame, elapsed)
            frame.elapsed = (frame.elapsed or 0) + elapsed
            if frame.elapsed >= 2 then
                frame.elapsed = 0
                updateTravelTips(frame)
            end
        end)
    end
    if tips then
        tips.previous = nil
        if enabled then tips:Show() else tips:Hide() end
    end
end

local function zoneList(build)
    if type(C_QuestLog) ~= 'table' then return 'Quest journal unavailable.' end
    local map = read(C_Map and C_Map.GetBestMapForUnit, 'player')
    if type(map) ~= 'number' or map < 1 or map % 1 ~= 0 then
        return 'Current map unavailable.'
    end
    local candidates = addon.pickupsByMap[map]
    if not candidates then return 'No catalog pickups mapped to your current map. Coverage is unknown.' end

    local player = currentPlayer()
    local groups = {journal = {}, matches = {}, uncertain = {}}
    local excluded, completed = 0, 0
    if #candidates > 1200 then return 'This map is too broad. Open the guide inside a smaller zone.' end
    for _, id in ipairs(candidates) do
        local record = addon.catalog[id]
        local result = zoneQuestStatus(id, record, player)
        if result == 'excluded' then
            excluded = excluded + 1
        elseif result == 'completed' or result == 'prior' then
            completed = completed + 1
        else
            local group = groups[result]
            group[#group + 1] = { id = id, xp = record.xp or 0, record = record }
        end
    end

    local zone = read(GetZoneText)
    local heading = type(zone) == 'string' and #zone <= 256 and plain(zone) or ('Map ' .. map)
    local lines = {heading .. ' (map ' .. map .. '), Forever build ' .. build}
    if player.level then lines[#lines + 1] = 'Player level at check: ' .. player.level end
    lines[#lines + 1] = 'Catalog pickups mapped from starter spawns. Listed XP may differ for your character.'
    lines[#lines + 1] = 'Use the offers view to confirm what a quest giver is offering.'
    lines[#lines + 1] = string.format('Screened %d pickups. %d did not match catalog checks. %d prior turn-ins hidden.', #candidates, excluded, completed)
    local function addGroup(key, label, maximum)
        local group = groups[key]
        if #group == 0 then return end
        table.sort(group, function(a, b)
            if a.xp == b.xp then return a.id < b.id end
            return a.xp > b.xp
        end)
        lines[#lines + 1] = '\n' .. label .. ' (' .. #group .. ')'
        for i = 1, math.min(#group, maximum) do
            local row = group[i]
            local who = row.record.pickup
            lines[#lines + 1] = string.format('%s (ID %d)%s%s', plain(title(row.id)), row.id,
                row.xp > 0 and (' - ' .. row.xp .. ' listed XP') or '',
                who and (' - Pickup: ' .. plain(who)) or '')
        end
        if #group > maximum then lines[#lines + 1] = 'Showing ' .. maximum .. ' of ' .. #group .. '.' end
    end
    addGroup('journal', 'Already in your journal', 15)
    addGroup('matches', 'Match the available catalog checks. Offer unconfirmed', 35)
    addGroup('uncertain', 'More evidence needed', 20)
    return table.concat(lines, '\n')
end

local function display()
    shownPickup = nil
    local reviewed, build = reviewedClient()
    if not reviewed then return 'Quest guide unavailable on this client build.' end
    if read(InCombatLockdown) ~= false then return 'Quest guide paused until you are out of combat.' end

    if localView then return localQuestList(build) end

    if showingOffers then return offeredQuests() end
    if showingZone then
        local body = zoneList(build)
        if sharing then
            return 'Which of these WoW Forever quest leads should I check first? Use the following snapshot as evidence.\n\n' .. body
        end
        return body
    end

    if lookup then
        local record = addon.catalog[lookup]
        local lines = {plain(title(lookup)) .. ' (ID ' .. lookup .. ')', '', completionText(lookup, build)}
        if record then
            lines[#lines + 1] = '\nPickup: ' .. plain(record.pickup or 'Unknown')
            lines[#lines + 1] = 'Turn-in: ' .. plain(record.turnin or 'Unknown')
            for _, detail in ipairs(questDetails(record)) do lines[#lines + 1] = detail end
            if record.story then lines[#lines + 1] = plain(record.story) end
            lines[#lines + 1] = 'NPC names from Polestar reference data.'
        else
            lines[#lines + 1] = '\nQuest details unavailable in the reference catalog.'
        end
        return table.concat(lines, '\n')
    end

    if type(C_QuestLog) ~= 'table' then return 'Quest journal unavailable.' end
    local count = read(C_QuestLog.GetNumQuestLogEntries)
    if type(count) ~= 'number' or count < 0 or count > 200 or count % 1 ~= 0 then
        return 'Quest journal unavailable.'
    end
    local ready, other, seen = {}, {}, {}
    local incomplete = false
    for index = 1, count do
        local info = read(C_QuestLog.GetInfo, index)
        local header = type(info) == 'table' and read(function() return info.isHeader end)
        if header == false then
            local id = read(function() return info.questID end)
            if type(id) == 'number' and id > 0 and id < 10000000 and id % 1 == 0 and not seen[id] then
                seen[id] = true
                local name = plain(title(id, read(function() return info.title end)))
                local complete = read(C_QuestLog.IsComplete, id)
                local record = addon.catalog[id]
                if complete == true then
                    local turnin = record and record.turnin
                    ready[#ready + 1] = name .. (turnin and (' - Turn in: ' .. plain(turnin)) or ' - Ready to turn in')
                else
                    other[#other + 1] = name .. (complete == false and ' - Check objectives' or ' - Progress unavailable')
                end
            else
                incomplete = true
            end
        elseif header ~= true then
            incomplete = true
        end
    end
    local zone = read(GetZoneText)
    local lines
    if sharing then
        lines = {
            'What should I do next with my quests in WoW Forever?',
            'Here is my quest journal at the time I copied it.',
        }
    else
        lines = {'Your quest journal'}
    end
    if type(zone) == 'string' and #zone > 0 and #zone <= 256 then
        lines[#lines + 1] = 'Zone: ' .. plain(zone)
    end
    if not sharing and #ready > 0 then
        lines[#lines + 1] = ''
        lines[#lines + 1] = 'Suggested next step: ' .. ready[1]
        lines[#lines + 1] = 'Already complete. Check travel before choosing a turn-in.'
    end
    lines[#lines + 1] = ''
    if #ready > 0 then
        lines[#lines + 1] = 'Ready to turn in'
        for _, row in ipairs(ready) do lines[#lines + 1] = row end
        lines[#lines + 1] = ''
    end
    for _, row in ipairs(other) do lines[#lines + 1] = row end
    if #ready + #other == 0 and not incomplete then lines[#lines + 1] = 'No journal quests found.' end
    if incomplete then lines[#lines + 1] = 'Some quest entries could not be read.' end
    lines[#lines + 1] = '\nNPC names from Polestar reference data.'
    return table.concat(lines, '\n')
end

local function refresh()
    if panel:IsShown() and not sharing then
        panel.body:SetText(display())
        if shownPickup then panel.pin:Show() else panel.pin:Hide() end
        if shownPickup then panel.route:Show() else panel.route:Hide() end
    end
end

local function createPanel()
    panel = CreateFrame('Frame', 'AlfadorWowGuide', UIParent, 'BackdropTemplate')
    panel:SetSize(640, 420)
    panel:SetPoint('CENTER')
    panel:SetFrameStrata('DIALOG')
    if panel.SetBackdrop then
        panel:SetBackdrop({bgFile = 'Interface\\Buttons\\WHITE8X8'})
        panel:SetBackdropColor(0.055, 0.065, 0.09, 0.97)
    end
    local heading = panel:CreateFontString(nil, 'OVERLAY', 'GameFontNormalLarge')
    heading:SetPoint('TOP', 0, -14)
    heading:SetText('Alfador-wow Guide')
    local scroll = CreateFrame('ScrollFrame', nil, panel, 'UIPanelScrollFrameTemplate')
    scroll:SetPoint('TOPLEFT', 18, -44)
    scroll:SetPoint('BOTTOMRIGHT', -34, 44)
    local body = CreateFrame('EditBox', nil, scroll)
    body:SetMultiLine(true)
    body:SetAutoFocus(false)
    body:SetFontObject(ChatFontNormal)
    body:SetWidth(568)
    body:SetMaxLetters(180000)
    body:SetScript('OnEscapePressed', function() panel:Hide() end)
    scroll:SetScrollChild(body)
    panel.body = body
    local close = CreateFrame('Button', nil, panel, 'UIPanelButtonTemplate')
    close:SetSize(90, 24)
    close:SetPoint('BOTTOMRIGHT', -16, 10)
    close:SetText('Close')
    close:SetScript('OnClick', function() panel:Hide() end)
    local pin = CreateFrame('Button', 'AlfadorWowGuidePinPickup', panel, 'UIPanelButtonTemplate')
    pin:SetSize(154, 24)
    pin:SetPoint('BOTTOMLEFT', 18, 10)
    pin:SetText('Pin first pickup')
    pin:SetScript('OnClick', function()
        if panel:IsShown() and shownPickup then requestPickupPin(shownPickup.id, shownPickup.map) end
    end)
    pin:Hide()
    panel.pin = pin
    local route = CreateFrame('Button', nil, panel, 'UIPanelButtonTemplate')
    route:SetSize(116, 24)
    route:SetPoint('LEFT', pin, 'RIGHT', 8, 0)
    route:SetText('Plan route')
    route:SetScript('OnClick', function()
        if not panel:IsShown() or not shownPickup then return end
        local mode = localView == 'lore' and 'story' or localView
        DEFAULT_CHAT_FRAME:AddMessage('Alfador-wow: ' .. startQuestRoute(mode))
    end)
    route:Hide()
    panel.route = route
    local share = CreateFrame('Button', nil, panel, 'UIPanelButtonTemplate')
    share:SetSize(154, 24)
    share:SetPoint('BOTTOMLEFT', 18, 10)
    share:SetText('Copy for Alfador')
    share:SetScript('OnClick', function()
        if sharing then
            sharing = false
            share:SetText('Copy for Alfador')
            refresh()
            return
        end
        sharing = true
        checkingCompletion = false
        showingOffers = false
        lookup = nil
        panel.body:SetText(display())
        panel.body:SetFocus()
        panel.body:HighlightText()
        share:SetText('Back to guide')
        DEFAULT_CHAT_FRAME:AddMessage('Alfador-wow: Press Ctrl+C, then paste into Alfador Desktop chat.')
    end)
    panel.share = share
    panel:SetScript('OnEvent', function() if not checkingCompletion then refresh() end end)
    for _, event in ipairs({'QUEST_LOG_UPDATE', 'QUEST_TURNED_IN', 'PLAYER_REGEN_DISABLED', 'PLAYER_REGEN_ENABLED', 'PLAYER_ENTERING_WORLD', 'ZONE_CHANGED_NEW_AREA', 'GOSSIP_SHOW', 'GOSSIP_CLOSED', 'GOSSIP_OPTIONS_REFRESHED'}) do
        panel:RegisterEvent(event)
    end
end

SLASH_ALFADORWOWGUIDE1 = '/alfadorwowguide'
SlashCmdList.ALFADORWOWGUIDE = function(command)
    local input = command:match('^%s*(.-)%s*$')
    if input == 'settings' then showNavigatorSettings(); return end
    if input == 'tips on' or input == 'tips off' then
        setTravelTips(input == 'tips on')
        DEFAULT_CHAT_FRAME:AddMessage('Alfador-wow: Local travel ' .. input .. '.')
        return
    end
    if input == 'voice on' or input == 'voice off' then
        routeVoice = input == 'voice on'
        DEFAULT_CHAT_FRAME:AddMessage(routeVoice and 'Alfador-wow: Local route voice on.' or 'Alfador-wow: Local route voice off.')
        return
    end
    local routeMode = input == 'route' and 'nearby' or input:match('^route%s+(%w+)$')
    if routeMode == 'nearby' or routeMode == 'xp' or routeMode == 'story' or routeMode == 'chains'
        or (routeMode and #routeMode <= 7 and routeMode:match('^%d+$') and tonumber(routeMode) > 0) then
        DEFAULT_CHAT_FRAME:AddMessage('Alfador-wow: ' .. startQuestRoute(routeMode))
        return
    end
    local pin = input:match('^pin%s+(%d+)$')
    if pin and #pin <= 7 and tonumber(pin) > 0 then
        requestPickupPin(tonumber(pin))
        return
    end
    local view = (input == 'nearby' or input == 'xp' or input == 'chains' or input == 'lore') and input or nil
    local check = input:match('^check%s+(%d+)$')
    local digits = check or input
    local id = #digits <= 7 and digits:match('^%d+$') and tonumber(digits)
    if not view and input ~= '' and input ~= 'offers' and input ~= 'zone' and (not id or id == 0) then
        DEFAULT_CHAT_FRAME:AddMessage('Alfador-wow: use /alfadorwowguide with settings, nearby, xp, chains, lore, route [xp|story|chains|quest ID], tips on/off, voice on/off, zone, offers, check <quest ID>, or pin <quest ID>.')
        return
    end
    lookup = id or nil
    checkingCompletion = check ~= nil
    showingOffers = input == 'offers'
    showingZone = input == 'zone'
    localView = view
    sharing = false
    if not panel then createPanel() end
    panel.share:SetText('Copy for Alfador')
    if localView then panel.share:Hide() else panel.share:Show() end
    panel:Show()
    refresh()
end
