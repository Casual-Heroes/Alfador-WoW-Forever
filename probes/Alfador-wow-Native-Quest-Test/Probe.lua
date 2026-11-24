-- Source-only Forever experiment. No catalog, events, SavedVariables, or I/O.
-- Call the returned function with "baseline", "gossip", "offer", or "journal".
local function read(fn, ...)
    if type(fn) ~= 'function' then return end
    local ok, a, b, c, d, e, f = pcall(fn, ...)
    if not ok then return end
    return {a, b, c, d, e, f}
end

local function safe(value, kind)
    if not issecretvalue(value) and type(value) == kind then return value end
end

local function first(fn, kind, ...)
    local values = read(fn, ...)
    if values then return safe(values[1], kind) end
end

local function integer(value, limit)
    value = safe(value, 'number')
    if value and value >= 0 and value <= limit and value % 1 == 0 then return value end
end

local function stringField(value, limit)
    value = safe(value, 'string')
    if value and #value > 0 and #value <= limit then return value end
end

local function coords(x, y)
    x, y = safe(x, 'number'), safe(y, 'number')
    if x and y and x >= 0 and x <= 1 and y >= 0 and y <= 1 then return {x = x, y = y} end
end

local function mapID()
    return integer(first(C_Map and C_Map.GetBestMapForUnit, 'number', 'player'), 100000)
end

local function playerPoint(map)
    if not map or not C_Map then return end
    return first(function()
        local point = C_Map.GetPlayerMapPosition(map, 'player')
        if issecretvalue(point) or point == nil then return end
        local x, y = point.x, point.y
        if not issecretvalue(x) and not issecretvalue(y) and x == nil and y == nil and point.GetXY then
            x, y = point:GetXY()
        end
        return coords(x, y)
    end, 'table')
end

local function questPOIs(map, questID)
    if not map then return end
    local rows = first(C_QuestLog.GetQuestsOnMap, 'table', map)
    if not rows or #rows > 200 then return end
    local points = {}
    for _, row in ipairs(rows) do
        if safe(row, 'table') then
            local id = integer(row.questID, 9999999)
            local point = coords(row.x, row.y)
            if id and id > 0 and point and (not questID or questID == id) then
                point.questID = id
                points[#points + 1] = point
            end
        end
    end
    return points
end

local function visible(frame)
    return frame and first(frame.IsShown, 'boolean', frame) == true
end

local function itemRewards(countFn, getter)
    local count = integer(first(countFn, 'number'), 25)
    if count == nil then return {status = 'unavailable'} end
    local result = {reportedCount = count, items = {}, status = 'observed'}
    for i = 1, count do
        local row = getter(i)
        local name = row and stringField(row[1], 256)
        if name then
            result.items[#result.items + 1] = {name = name, count = integer(row[3], 10000),
                id = integer(row[6], 9999999)}
        else
            result.status = 'partial'
        end
    end
    return result
end

local function questDetails(context, id, map)
    local detail, readID = {}, context == 'offer' and GetQuestID or C_QuestLog.GetSelectedQuest
    if context == 'offer' then
        detail.title = stringField(first(GetTitleText, 'string'), 256)
        detail.description = stringField(first(GetQuestText, 'string'), 16384)
        detail.objectiveText = stringField(first(GetObjectiveText, 'string'), 8192)
        detail.xpAPI = 'GetRewardXP'
        detail.xp = integer(first(GetRewardXP, 'number'), 100000000)
        detail.money = integer(first(GetRewardMoney, 'number'), 10000000000)
        detail.rewards = itemRewards(GetNumQuestRewards, function(i) return read(GetQuestItemInfo, 'reward', i) end)
        detail.choices = itemRewards(GetNumQuestChoices, function(i) return read(GetQuestItemInfo, 'choice', i) end)
    else
        detail.title = stringField(first(C_QuestLog.GetTitleForQuestID, 'string', id), 256)
        local index = integer(first(C_QuestLog.GetLogIndexForQuestID, 'number', id), 200)
        local lines = index and index > 0 and read(GetQuestLogQuestText, index)
        detail.description = lines and stringField(lines[1], 16384) or nil
        detail.objectiveText = lines and stringField(lines[2], 8192) or nil
        detail.xpAPI = 'GetQuestLogRewardXP'
        detail.xp = integer(first(GetQuestLogRewardXP, 'number'), 100000000)
        detail.money = integer(first(GetQuestLogRewardMoney, 'number'), 10000000000)
        detail.rewards = itemRewards(GetNumQuestLogRewards, function(i) return read(GetQuestLogRewardInfo, i) end)
        detail.choices = itemRewards(GetNumQuestLogChoices, function(i) return read(GetQuestLogChoiceInfo, i) end)
    end
    local waypoint = read(C_QuestLog.GetNextWaypoint, id)
    if waypoint then
        local targetMap = integer(waypoint[1], 100000)
        local target = coords(waypoint[2], waypoint[3])
        if targetMap and targetMap > 0 and target then
            target.mapID = targetMap
            detail.waypoint = target
        end
    end
    detail.mapPOIs = questPOIs(map, id)
    if first(readID, 'number') ~= id or mapID() ~= map or (context == 'offer' and not visible(QuestFrame)) then
        return {status = 'context changed'}
    end
    detail.questID = id
    detail.status = 'observed context'
    detail.xpStatus = detail.xp == nil and 'unavailable' or detail.xp == 0 and 'zero, verify in UI' or 'API value'
    return detail
end

return function(context)
    if type(issecretvalue) ~= 'function' or first(InCombatLockdown, 'boolean') ~= false then
        return {status = 'observation unavailable'}
    end
    local build = read(GetBuildInfo)
    if not build or safe(build[1], 'string') ~= '1.60.1' or safe(build[4], 'number') ~= 16001
        or type(C_QuestLog) ~= 'table' then return {status = 'unsupported client'} end
    local map = mapID()
    local result = {status = 'observed context', context = context, build = stringField(build[2], 32),
        mapID = map, position = playerPoint(map), level = integer(first(UnitLevel, 'number', 'player'), 1000)}
    if context == 'baseline' then
        result.journalRows = integer(first(C_QuestLog.GetNumQuestLogEntries, 'number'), 200)
        result.mapPOIs = questPOIs(map)
    elseif context == 'gossip' and visible(GossipFrame) then
        local rows = first(C_GossipInfo and C_GossipInfo.GetAvailableQuests, 'table')
        if rows and #rows <= 100 then
            result.offers = {}
            for _, row in ipairs(rows) do
                if safe(row, 'table') then
                    local id = integer(row.questID, 9999999)
                    if id and id > 0 then
                        result.offers[#result.offers + 1] = {questID = id, title = stringField(row.title, 256)}
                    end
                end
            end
        end
    elseif context == 'offer' and visible(QuestFrame) then
        local id = integer(first(GetQuestID, 'number'), 9999999)
        if id and id > 0 and first(C_QuestLog.IsOnQuest, 'boolean', id) == false then
            result.quest = questDetails(context, id, map)
        end
    elseif context == 'journal' then
        local id = integer(first(C_QuestLog.GetSelectedQuest, 'number'), 9999999)
        if id and id > 0 and first(C_QuestLog.IsOnQuest, 'boolean', id) == true then
            result.quest = questDetails(context, id, map)
        end
    else
        result.status = 'requested context unavailable'
    end
    if mapID() ~= map then return {status = 'map changed'} end
    return result
end
