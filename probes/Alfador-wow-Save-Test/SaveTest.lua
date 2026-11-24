-- Isolated source-only experiment. Never forces saves or reloads.
-- Setting a global in memory does NOT mean the client wrote it to disk.
local sequence, boundary, world = 0, nil, false
local function say(text) DEFAULT_CHAT_FRAME:AddMessage('Alfador-wow save test: ' .. text) end
local function safe(fn, ...)
    if type(fn) ~= 'function' or type(issecretvalue) ~= 'function' then return nil end
    local ok, value = pcall(fn, ...)
    if not ok then return nil end
    local checked, secret = pcall(issecretvalue, value)
    if not checked or secret then return nil end
    return value
end
local function exactBuild()
    if type(GetBuildInfo) ~= 'function' then return false end
    local ok, version, build, _, interface = pcall(GetBuildInfo)
    if not ok then return false end
    return safe(function() return version end) == '1.60.1'
        and safe(function() return build end) == '71037'
        and safe(function() return interface end) == 16001
end
local frame = CreateFrame('Frame','AlfadorWowSaveTestBoundary')
for _, event in ipairs({'PLAYER_ENTERING_WORLD','PLAYER_LEAVING_WORLD','PLAYER_LOGOUT'}) do frame:RegisterEvent(event) end
frame:SetScript('OnEvent',function(_,event)
    if event == 'PLAYER_ENTERING_WORLD' then
        world = true; sequence = 0; boundary = nil
    else world = false; sequence = 0; boundary = nil end
    -- Do not mutate saved data on lifecycle events. Inspect the marker actually set.
end)
local function mark()
    if not world or not exactBuild() or safe(IsLoggedIn) ~= true or safe(UnitExists,'player') ~= true then say('world/build/player unavailable; marker unchanged'); return end
    if safe(InCombatLockdown) ~= false then say('combat/safety unavailable; marker unchanged'); return end
    local stamp = safe(GetServerTime)
    if type(stamp) ~= 'number' or stamp ~= stamp or stamp % 1 ~= 0 or stamp < 1 or stamp > 9999999999 then say('timestamp unavailable; marker unchanged'); return end
    if sequence >= 1000 then say('marker limit reached'); return end
    if not boundary then
        local bits = {}
        for i=1,32 do bits[i] = string.format('%x', math.random(0,15)) end
        boundary = table.concat(bits) -- experiment label, not actor identity/authority
    end
    sequence = sequence + 1
    local json = string.format('{"schema":"alfador.wowf.save-test.v1","version":"1.60.1","build":"71037","interface":16001,"boundary":"%s","sequence":%d,"capturedAtUnix":%.0f,"freshness":"historical","payloadKind":"synthetic-save-marker"}',boundary,sequence,stamp)
    AlfadorWowSaveTestEvidence = (json:gsub('.',function(c) return string.format('%02x',string.byte(c)) end))
    say('MARKED in memory only; sequence=' .. sequence .. ' boundary=' .. boundary .. ' capturedAtUnix=' .. string.format('%.0f',stamp) .. '; disk save unverified')
end
SLASH_ALFADORSAVETEST1 = '/alfadorsavetest'
SlashCmdList.ALFADORSAVETEST = function(command)
    if command == 'mark' then mark()
    else say('mark only; no automatic logging, save, reload or network') end
end
