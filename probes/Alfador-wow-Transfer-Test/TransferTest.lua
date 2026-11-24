-- Source-review experiment only. Not installed or proven on actual Forever.
-- Uses documented logged addon messaging; no data stream or raw chat is exported.
local PREFIX, MAX_SENDS, INTERVAL = 'AlfadorTest', 8, 3
local world, active, prepared, elapsed, sequence = false, false, false, 0, 0
local session, target, restrictionObserved
local function say(text) DEFAULT_CHAT_FRAME:AddMessage('Alfador-wow transfer test: ' .. text) end
local function safe(fn, ...)
    if type(fn) ~= 'function' or type(issecretvalue) ~= 'function' then return nil end
    local ok, value = pcall(fn, ...)
    if not ok then return nil end
    local checked, secret = pcall(issecretvalue, value)
    if not checked or secret then return nil end
    return value
end
local function stop(reason)
    active = false; prepared = false; target = nil; say(reason)
end
local function buildOK()
    if type(GetBuildInfo) ~= 'function' then return false end
    local ok, version, number, _, interface = pcall(GetBuildInfo)
    if not ok then return false end
    version = safe(function() return version end)
    number = safe(function() return number end)
    interface = safe(function() return interface end)
    return version == '1.60.1' and number == '71037' and interface == 16001
end
local function eligible()
    if not world or not buildOK() then return nil, 'world/build unavailable' end
    if safe(IsLoggedIn) ~= true or safe(UnitExists, 'player') ~= true then return nil, 'player unavailable' end
    if safe(InCombatLockdown) ~= false then return nil, 'combat/safety unavailable' end
    if type(C_ChatInfo) ~= 'table' or type(C_ChatInfo.SendAddonMessageLogged) ~= 'function' then return nil, 'logged API unavailable' end
    -- Source04 diagnostic: older Forever author tests report true even with working
    -- messages. This does not override native enforcement or establish permission.
    local restricted = safe(C_ChatInfo.AreOutgoingAddonChatMessagesRestricted)
    if type(restricted) ~= 'boolean' then return nil, 'restriction diagnostic unavailable' end
    restrictionObserved = restricted
    if safe(IsInInstance) ~= false then return nil, 'open-world test only; instance state unavailable/active' end
    if safe(C_ChatInfo.InChatMessagingLockdown) ~= false then return nil, 'chat lockdown/unavailable' end
    if safe(C_ChatInfo.IsLoggingChat) ~= true then return nil, 'chat logging is off/unavailable; this probe will not enable it' end
    local name = safe(UnitName, 'player') -- Local routing only. Never payload/export.
    if type(name) ~= 'string' or #name == 0 or #name > 64 or name:find('%c') then return nil, 'self target unavailable' end
    return name
end
local function prefixReady()
    if type(C_ChatInfo.RegisterAddonMessagePrefix) ~= 'function' then return false end
    local ok = pcall(C_ChatInfo.RegisterAddonMessagePrefix, PREFIX)
    return ok and safe(C_ChatInfo.IsAddonMessagePrefixRegistered, PREFIX) == true
        and Enum and Enum.SendAddonMessageResult and type(Enum.SendAddonMessageResult.Success) == 'number'
end
local function prepare()
    if active then say('stop active run before preparing another'); return end
    local name, reason = eligible()
    if not name then stop(reason); return end
    if not prefixReady() then stop('prefix/enum verification unavailable'); return end
    local bits = {}
    for i = 1, 32 do bits[i] = string.format('%x', math.random(0, 15)) end
    session = table.concat(bits); target = name; sequence = 0; elapsed = 0; prepared = true
    say('restriction_flag=' .. tostring(restrictionObserved) .. '; diagnostic only; self-WHISPER native outcome untested')
    say('PREPARED session=' .. session .. '; zero markers sent. Open reader and wait for ready before start.')
end
local function start()
    if active then say('already running; no second session started'); return end
    if not prepared then say('prepare first; no markers sent'); return end
    local name, reason = eligible()
    if not name or name ~= target then stop(reason or 'character target changed'); return end
    if not prefixReady() then stop('prefix/enum verification unavailable'); return end
    local clock = safe(GetTimePreciseSec)
    if type(clock) ~= 'number' or clock ~= clock or clock < 0 or clock == math.huge then stop('subsecond game clock unavailable'); return end
    prepared = false; elapsed = 0; active = true
    say('STARTED prepared session=' .. session .. '; eight attempts maximum, three-second cadence.')
end
local frame = CreateFrame('Frame', 'AlfadorWowTransferTestSampler')
for _, event in ipairs({'PLAYER_ENTERING_WORLD','PLAYER_LEAVING_WORLD','PLAYER_LOGOUT'}) do frame:RegisterEvent(event) end
frame:SetScript('OnEvent', function(_, event)
    if event == 'PLAYER_ENTERING_WORLD' then world = true
    else world = false; if active or prepared then stop('world left; prepare a new run; no silent resume') end end
end)
frame:SetScript('OnUpdate', function(_, dt)
    if not active or type(dt) ~= 'number' or dt ~= dt or dt < 0 then return end
    elapsed = elapsed + dt
    if elapsed < INTERVAL then return end
    elapsed = 0 -- No catch-up bursts.
    local name, reason = eligible()
    if not name or name ~= target then stop(reason or 'character target changed'); return end
    local stamp = safe(GetServerTime)
    if type(stamp) ~= 'number' or stamp ~= stamp or stamp % 1 ~= 0 or stamp < 1 or stamp > 9999999999 then stop('timestamp unavailable'); return end
    local before = safe(GetTimePreciseSec)
    if type(before) ~= 'number' or before ~= before or before < 0 or before == math.huge then stop('subsecond game clock unavailable'); return end
    sequence = sequence + 1
    local text = 'ALFADOR_XFER_V1 session=' .. session .. ' seq=' .. sequence .. ' sent=' .. string.format('%.0f', stamp) .. ' END'
    local result = safe(C_ChatInfo.SendAddonMessageLogged, PREFIX, text, 'WHISPER', target)
    if result ~= Enum.SendAddonMessageResult.Success then stop('send unsuccessful/unverified result=' .. tostring(result) .. '; no retry'); return end
    local after = safe(GetTimePreciseSec)
    if type(after) ~= 'number' or after ~= after or after < before or after == math.huge then stop('send clock unavailable; native attempt occurred'); return end
    say(string.format('SEND seq=%d game_before=%.6f game_after=%.6f native_success_only=true restriction_flag=%s', sequence, before, after, tostring(restrictionObserved)))
    -- A native success code is NOT proof of disk flush or Desktop receipt.
    if sequence >= MAX_SENDS then stop('eight marker attempts complete; disk delivery still unverified') end
end)
SLASH_ALFADORTRANSFERTEST1 = '/alfadortransfertest'
SlashCmdList.ALFADORTRANSFERTEST = function(command)
    if command == 'prepare' then prepare()
    elseif command == 'start' then start()
    elseif command == 'stop' then stop('stopped by user')
    else say(active and 'marker test active; not a live game-data feed' or (prepared and 'prepared; wait for reader ready before start' or 'idle; prepare/start/stop only in an approved test')) end
end
