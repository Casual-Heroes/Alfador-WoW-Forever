-- No network, gameplay actions or persistence. Local refresh while UI is visible.
-- TOC interface is owner-reported. API behavior still needs in-game acceptance.
local serial = 0
local panel
local capture
local arrayTag = {}
local function array(values) return setmetatable(values, arrayTag) end
local function notify(text) DEFAULT_CHAT_FRAME:AddMessage('Alfador-wow: ' .. text) end

local function scalar(value)
    if type(issecretvalue) ~= 'function' then return { status = 'secret-check-unavailable' } end
    if issecretvalue(value) then return { status = 'restricted' } end
    local kind = type(value)
    if kind == 'string' then
        if #value > 1024 then return { status = 'value-limit' } end
    elseif kind == 'number' then
        if value ~= value or value == math.huge or value == -math.huge then return { status = 'invalid' } end
    elseif kind ~= 'boolean' then
        return { status = 'unavailable' }
    end
    return { status = 'observed', value = value }
end

local function call(fn, ...)
    if type(fn) ~= 'function' then return { status = 'api-unavailable' } end
    local ok, value = pcall(fn, ...)
    if not ok then return { status = 'call-failed' } end
    return scalar(value)
end

local function known(value, kind)
    return value.status == 'observed' and type(value.value) == kind
end

local function selectedRewardXP(questId, player, capturedAt, selectionAtCapture)
    local missing = { status = 'unavailable' }
    if not known(player.level, 'number') or player.level.value < 1 or player.level.value % 1 ~= 0
        or not known(player.guid, 'string') or player.guid.value == ''
        or not known(capturedAt, 'number') or capturedAt.value < 1 or capturedAt.value % 1 ~= 0 then return missing, missing, 'player-context-unavailable' end
    if not known(selectionAtCapture, 'number') then return missing, missing, 'selection-unavailable' end
    if selectionAtCapture.value ~= questId then return missing, missing, 'not-selected-quest' end
    local selected = call(C_QuestLog.GetSelectedQuest)
    if not known(selected, 'number') or selected.value ~= questId then return missing, missing, 'selection-or-player-changed' end
    local showRewards = call(C_QuestLog.ShouldShowQuestRewards, questId)
    if not known(showRewards, 'boolean') then return missing, missing, 'reward-display-check-unavailable' end
    if showRewards.value ~= true then return missing, missing, 'rewards-not-shown' end
    -- Blizzard's UI uses this no-argument call for the selected log quest.
    -- Passing questId here could silently attach the wrong quest's reward.
    local xp = call(GetQuestLogRewardXP)
    local after = call(C_QuestLog.GetSelectedQuest)
    local levelAfter = call(UnitLevel, 'player')
    local guidAfter = call(UnitGUID, 'player')
    if not known(after, 'number') or after.value ~= questId
        or not known(levelAfter, 'number') or levelAfter.value ~= player.level.value
        or not known(guidAfter, 'string') or guidAfter.value ~= player.guid.value then return missing, missing, 'selection-or-player-changed' end
    if xp.status ~= 'observed' then
        local reasons = { ['api-unavailable'] = 'xp-api-unavailable', ['call-failed'] = 'xp-call-failed',
            restricted = 'xp-restricted', unavailable = 'xp-unavailable' }
        return xp, missing, reasons[xp.status] or 'xp-invalid'
    end
    if not known(xp, 'number') then return { status = 'invalid' }, missing, 'xp-invalid' end
    if xp.value < 0 or xp.value % 1 ~= 0 or xp.value > 1000000000 then return { status = 'invalid' }, missing, 'xp-invalid' end
    return xp, { status = 'observed', value = {
        api = 'GetQuestLogRewardXP', binding = 'selected-quest-before-and-after',
        questId = questId, playerLevel = player.level.value, capturedAtUnix = capturedAt.value,
    } }, 'observed'
end

local function objectCall(fn, ...)
    if type(fn) ~= 'function' then return nil end
    local ok, value = pcall(fn, ...)
    if not ok or issecretvalue(value) or type(value) ~= 'table' then return nil end
    return value
end

local function questTitle(info, questId)
    local title = scalar(info.title)
    if known(title, 'string') and title.value == '' then title = { status = 'unavailable' } end
    if title.status == 'unavailable' then title = call(C_QuestLog.GetTitleForQuestID, questId) end
    if title.status == 'observed' and not known(title, 'string') then return { status = 'invalid' } end
    if known(title, 'string') and title.value == '' then return { status = 'unavailable' } end
    return title
end

local function plain(value, fallback)
    if not known(value, 'string') then return fallback end
    -- Literal UI text: never activate links, textures or embedded line breaks.
    return value.value:gsub('[%z\1-\31]', ' '):gsub('|', '||')
end

local function summary(report)
    local level = known(report.player.level, 'number') and tostring(report.player.level.value) or '?'
    local lines = { plain(report.player.name, 'Character') .. ' - Level ' .. level .. ' - ' .. plain(report.zone.name, 'Zone unavailable'),
        'Select a quest in your quest log; this window refreshes while open.', '' }
    for _, quest in ipairs(report.quests) do
        local name = plain(quest.title, 'Quest name unavailable')
        if known(report.selectedQuestAtCapture, 'number') and report.selectedQuestAtCapture.value == quest.questId.value then
            name = name .. ' (selected)'
        end
        local progress = 'Progress unavailable'
        if known(quest.turnedIn, 'boolean') and quest.turnedIn.value then progress = 'Turned in'
        elseif known(quest.objectivesComplete, 'boolean') then
            progress = quest.objectivesComplete.value and 'Objectives complete' or 'Objectives in progress'
        end
        local reward = 'XP unavailable'
        if known(quest.rewardXP, 'number') then reward = 'Reward: ' .. tostring(quest.rewardXP.value) .. ' XP (check quest log)'
        elseif quest.rewardXPRead == 'not-selected-quest' then reward = 'Select this quest to read its reward XP'
        elseif quest.rewardXPRead == 'rewards-not-shown' then reward = 'Reward XP is not currently shown'
        end
        lines[#lines + 1] = name
        lines[#lines + 1] = '  ' .. progress .. ' | ' .. reward
        lines[#lines + 1] = ''
    end
    if #report.quests == 0 then lines[#lines + 1] = 'No quest candidates in this capture; coverage may be unavailable.' end
    lines[#lines + 1] = 'This is a local snapshot, not a recommendation or Core connection.'
    return table.concat(lines, '\n')
end

local function quote(text)
    return '"' .. text:gsub('[%z\1-\31\\"]', function(char)
        if char == '"' then return '\\"' end
        if char == '\\' then return '\\\\' end
        return string.format('\\u%04x', string.byte(char))
    end) .. '"'
end

local function encode(value, depth)
    if depth > 12 then error('JSON nesting limit') end
    local kind = type(value)
    if kind == 'string' then return quote(value) end
    if kind == 'number' then return tostring(value) end
    if kind == 'boolean' then return value and 'true' or 'false' end
    if kind ~= 'table' then error('Unsupported JSON value') end
    local parts = {}
    if getmetatable(value) == arrayTag then
        for _, item in ipairs(value) do parts[#parts + 1] = encode(item, depth + 1) end
        return '[' .. table.concat(parts, ',') .. ']'
    end
    for key, item in pairs(value) do
        parts[#parts + 1] = quote(key) .. ':' .. encode(item, depth + 1)
    end
    return '{' .. table.concat(parts, ',') .. '}'
end

local function showExport(text, report)
    if not panel then
        panel = CreateFrame('Frame', 'AlfadorWowExport', UIParent)
        panel:SetSize(620, 400)
        panel:SetPoint('CENTER')
        panel:SetFrameStrata('DIALOG')
        local background = panel:CreateTexture(nil, 'BACKGROUND')
        background:SetAllPoints()
        background:SetColorTexture(0.04, 0.04, 0.06, 0.96)
        local title = panel:CreateFontString(nil, 'OVERLAY', 'GameFontNormal')
        title:SetPoint('TOP', 0, -12)
        title:SetText('Alfador-wow - Quests')
        panel.title = title
        local scroll = CreateFrame('ScrollFrame', nil, panel, 'UIPanelScrollFrameTemplate')
        scroll:SetPoint('TOPLEFT', 16, -36)
        scroll:SetPoint('BOTTOMRIGHT', -34, 42)
        local edit = CreateFrame('EditBox', nil, scroll)
        edit:SetMultiLine(true)
        edit:SetAutoFocus(false)
        edit:SetFontObject(ChatFontNormal)
        edit:SetWidth(560)
        edit:SetMaxLetters(262144)
        edit:SetScript('OnEscapePressed', function() panel:Hide() end)
        scroll:SetScrollChild(edit)
        panel.edit = edit
        local copy = CreateFrame('Button', nil, panel, 'UIPanelButtonTemplate')
        copy:SetSize(150, 24)
        copy:SetPoint('BOTTOMLEFT', 16, 10)
        copy:SetText('Show report')
        panel.copyButton = copy
        copy:SetScript('OnClick', function()
            panel.showingReport = not panel.showingReport
            panel.edit:SetText(panel.showingReport and panel.reportText or panel.summaryText)
            panel.title:SetText(panel.showingReport and 'Report - Ctrl+C to copy' or 'Alfador-wow - Quests')
            copy:SetText(panel.showingReport and 'Back to quests' or 'Show report')
            panel.refreshButton:SetEnabled(not panel.showingReport)
            if panel.showingReport then panel.edit:SetFocus(); panel.edit:HighlightText() end
        end)
        local refresh = CreateFrame('Button', nil, panel, 'UIPanelButtonTemplate')
        refresh:SetSize(100, 24)
        refresh:SetPoint('BOTTOMLEFT', 180, 10)
        refresh:SetText('Refresh')
        refresh:SetScript('OnClick', function() if not panel.showingReport then capture() end end)
        panel.refreshButton = refresh
        panel:SetScript('OnShow', function()
            -- Event name only; no event payloads or combat telemetry.
            pcall(panel.RegisterEvent, panel, 'QUEST_LOG_UPDATE')
        end)
        panel:SetScript('OnHide', function() panel:UnregisterAllEvents() end)
        panel:SetScript('OnEvent', function(_, event)
            if event == 'QUEST_LOG_UPDATE' then panel.needsRefresh = true end
        end)
        panel:SetScript('OnUpdate', function(_, elapsed)
            if not panel:IsShown() or panel.showingReport then return end
            panel.refreshElapsed = (panel.refreshElapsed or 0) + elapsed
            if panel.refreshElapsed < 0.5 then return end
            panel.refreshElapsed = 0
            if type(issecretvalue) ~= 'function' then
                panel.title:SetText('Alfador-wow - Quests (refresh paused)')
                return
            end
            local combat = call(InCombatLockdown)
            if not known(combat, 'boolean') or combat.value ~= false then
                panel.title:SetText('Alfador-wow - Quests (refresh paused)')
                return
            end
            panel.title:SetText('Alfador-wow - Quests')
            local function same(a, b)
                return a.status == b.status and a.value == b.value
            end
            local selected = call(C_QuestLog and C_QuestLog.GetSelectedQuest)
            local level = call(UnitLevel, 'player')
            local guid = call(UnitGUID, 'player')
            local map = call(C_Map and C_Map.GetBestMapForUnit, 'player')
            if panel.needsRefresh or not same(selected, panel.lastReport.selectedQuestAtCapture)
                or not same(level, panel.lastReport.player.level) or not same(guid, panel.lastReport.player.guid)
                or not same(map, panel.lastReport.zone.mapId) then capture(true) end
        end)
        local close = CreateFrame('Button', nil, panel, 'UIPanelButtonTemplate')
        close:SetSize(90, 24)
        close:SetPoint('BOTTOMRIGHT', -16, 10)
        close:SetText('Close')
        close:SetScript('OnClick', function() panel:Hide() end)
    end
    panel.reportText = text
    panel.summaryText = summary(report)
    panel.showingReport = false
    panel.lastReport = report
    panel.needsRefresh = false
    panel.refreshElapsed = 0
    panel.refreshButton:SetEnabled(true)
    panel.title:SetText('Alfador-wow - Quests')
    panel.copyButton:SetText('Show report')
    panel.edit:SetText(panel.summaryText)
    panel:Show()
end

capture = function(automatic)
    -- A refused capture must not leave an older snapshot looking refreshed.
    if panel then panel:Hide() end
    if type(issecretvalue) ~= 'function' then notify('No secret-value checker; capture refused.'); return end
    local combat = call(InCombatLockdown)
    if not known(combat, 'boolean') or combat.value ~= false then notify('Capture requires known out-of-combat state.'); return end
    if type(GetBuildInfo) ~= 'function' then notify('Build API unavailable.'); return end
    local ok, version, build, _, interface = pcall(GetBuildInfo)
    if not ok then notify('Build call failed.'); return end
    version, build, interface = scalar(version), scalar(build), scalar(interface)
    if not known(version, 'string') or version.value ~= '1.60.1'
        or not known(build, 'string') or build.value ~= '70959'
        or not known(interface, 'number') or interface.value ~= 16001 then
        notify('Client differs from the reviewed Forever build; capture refused.'); return
    end
    if type(C_QuestLog) ~= 'table' then notify('Quest API unavailable.'); return end
    local count = call(C_QuestLog.GetNumQuestLogEntries)
    if not known(count, 'number') or count.value < 0 or count.value > 200 or count.value % 1 ~= 0 then
        notify('Quest log count unavailable or exceeds probe limit.'); return
    end
    local map = call(C_Map and C_Map.GetBestMapForUnit, 'player')
    if not known(map, 'number') or map.value <= 0 then notify('Current player map unavailable.'); return end
    local quests = array({})
    local unresolved = 0
    local capturedAt = call(GetServerTime)
    local player = { guid = call(UnitGUID, 'player'), name = call(UnitName, 'player'), level = call(UnitLevel, 'player') }
    local selectionAtCapture = call(C_QuestLog.GetSelectedQuest)
    if selectionAtCapture.status == 'observed' and (not known(selectionAtCapture, 'number')
        or selectionAtCapture.value < 0 or selectionAtCapture.value % 1 ~= 0) then selectionAtCapture = { status = 'invalid' } end
    for index = 1, count.value do
        local info = objectCall(C_QuestLog.GetInfo, index)
        if info then
            local header = scalar(info.isHeader)
            local id = scalar(info.questID)
            if known(header, 'boolean') and header.value == false and known(id, 'number') and id.value > 0 then
                local onMap = call(C_QuestLog.IsOnMap, id.value)
                if known(onMap, 'boolean') and onMap.value == true then
                    if #quests >= 50 then notify('More than 50 candidates; no truncated report exported.'); return end
                    local xp, xpContext, xpRead = selectedRewardXP(id.value, player, capturedAt, selectionAtCapture)
                    quests[#quests + 1] = {
                        questId = id,
                        title = questTitle(info, id.value),
                        onMap = onMap,
                        onQuest = call(C_QuestLog.IsOnQuest, id.value),
                        turnedIn = call(C_QuestLog.IsQuestFlaggedCompleted, id.value),
                        objectivesComplete = call(C_QuestLog.IsComplete, id.value),
                        displayLevel = scalar(info.level),
                        -- Display level is NOT a verified minimum-level requirement.
                        rewardXP = xp,
                        rewardXPContext = xpContext,
                        rewardXPRead = xpRead,
                        timing = { status = 'unavailable' },
                    }
                elseif not known(onMap, 'boolean') then unresolved = unresolved + 1 end
            elseif not known(header, 'boolean') or header.value == false then unresolved = unresolved + 1 end
        else unresolved = unresolved + 1 end
    end
    serial = serial + 1
    local report = {
        schema = 'alfador.wow.forever.quest-pilot.capture.draft4',
        game = 'wow-forever', source = 'wow-addon-api', freshness = 'historical',
        localCaptureSerial = serial, capturedAtUnix = capturedAt,
        build = { version = version, number = build, interface = interface },
        player = player,
        selectedQuestAtCapture = selectionAtCapture,
        zone = { mapId = map, name = call(GetZoneText) },
        candidateBasis = 'quest-log-IsOnMap-at-capture-not-verified-zone-membership',
        unresolvedLogEntries = unresolved,
        quests = quests,
        limitations = array({
            'Local historical evidence; no verified session or Core delivery.',
            'IsOnMap candidates require Core-side zone and eligibility verification.',
            'XP is read only for the selected quest; verify against UI. Prerequisites and remaining times are unavailable.',
            'No objective payloads, combat state, gear or talents collected.',
        }),
    }
    local success, text = pcall(encode, report, 0)
    if not success or #text > 262144 then notify('Export failed or exceeds limit.'); return end
    showExport(text, report)
    if not automatic then notify('Quest view ready. Show report opens copyable details; inspect your character identity before sharing.') end
end

SLASH_ALFADORWOW1 = '/alfadorwow'
SlashCmdList.ALFADORWOW = function(command)
    if command == '' or command == 'capture' then capture()
    else notify('Use /alfadorwow to capture local quest evidence outside combat.') end
end
