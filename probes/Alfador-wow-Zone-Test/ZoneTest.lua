-- Isolated source-only probe. No networking, GUID/name or gameplay reads.
-- Optional client-written SavedVariables contains bounded hex JSON; historical only.
-- 1 Hz local sampler does NOT establish live delivery to Desktop/Core.
local sequence, world, elapsed = 0, false, 0
local persist
local samples, boundary = {}, nil
local function newBoundary()
    local bits = {}
    for i = 1, 32 do bits[i] = string.format('%x', math.random(0, 15)) end
    boundary = table.concat(bits) -- Ephemeral label, NOT identity/authorization.
end
newBoundary()
local function missing() return { status = 'unavailable' } end
local function fact(fn, ...)
    if type(fn) ~= 'function' or type(issecretvalue) ~= 'function' then return missing() end
    local ok, value = pcall(fn, ...)
    if not ok then return missing() end
    local checked, secret = pcall(issecretvalue, value)
    if not checked or secret then return missing() end
    local kind = type(value)
    if kind == 'string' then
        if #value == 0 or #value > 128 then return missing() end
    elseif kind == 'number' then
        if value ~= value or value == math.huge or value == -math.huge then return missing() end
    elseif kind ~= 'boolean' then return missing() end
    return { status = 'observed', value = value }
end
local function is(f, kind) return f.status == 'observed' and type(f.value) == kind end
local function integer(f, low, high)
    return is(f, 'number') and f.value % 1 == 0 and f.value >= low and f.value <= high
end
local function timestamp()
    local f = fact(GetServerTime)
    return integer(f, 1, 9999999999) and f or missing()
end
local function same(a, b)
    return a.status == 'observed' and b.status == 'observed' and a.value == b.value
end
local function build()
    local fields = { version = missing(), build = missing(), interface = missing() }
    if type(GetBuildInfo) ~= 'function' or type(issecretvalue) ~= 'function' then return false, fields end
    local ok, version, number, _, interface = pcall(GetBuildInfo)
    if not ok then return false, fields end
    fields.version = fact(function() return version end)
    fields.build = fact(function() return number end)
    fields.interface = fact(function() return interface end)
    if not is(fields.version, 'string') then fields.version = missing() end
    if not is(fields.build, 'string') then fields.build = missing() end
    if not integer(fields.interface, 1, 999999) then fields.interface = missing() end
    return is(fields.version, 'string') and fields.version.value == '1.60.1'
        and is(fields.build, 'string') and fields.build.value == '70959'
        and integer(fields.interface, 16001, 16001), fields
end
local function publish(reason, start, finish, fields)
    local matched, observedBuild = build()
    if reason == 'sampled' and not matched then reason = 'build-unavailable-or-mismatch'; fields = nil end
    sequence = sequence + 1
    samples[#samples + 1] = {
        schema = 'alfador.wowf.zone-probe.sample.draft1', game = 'wow-forever',
        expectedClient = { version = '1.60.1', build = '70959', interface = 16001 },
        observedClient = observedBuild,
        buildCheck = matched and 'matched-at-sample' or 'unavailable-or-mismatch',
        boundary = boundary, sequence = sequence,
        state = reason == 'sampled' and 'in_world' or 'unavailable', reason = reason,
        capturedAtUnix = start, sampleEndUnix = finish,
        sampling = 'sequential-nonatomic-before-after-guards',
        fields = fields or { inWorld = missing(), mapId = missing(), zoneName = missing(), level = missing() },
        transport = 'local-copy-only-not-live-desktop',
    }
    if #samples > 12 then table.remove(samples, 1) end
    if persist then persist() end
end
local function unavailable(reason)
    local stamp = timestamp()
    publish(reason, stamp, stamp)
end
local function sample()
    local stamp = timestamp()
    if not build() then publish('build-unavailable-or-mismatch', stamp, stamp); return end
    if not world then publish('not-in-world', stamp, stamp); return end
    local combat = fact(InCombatLockdown)
    if not is(combat, 'boolean') or combat.value then publish('combat-or-safety-unavailable', stamp, stamp); return end
    local logged = fact(IsLoggedIn)
    local exists = fact(UnitExists, 'player')
    if not is(logged, 'boolean') or not logged.value or not is(exists, 'boolean') or not exists.value then
        world = false -- Require another entering-world boundary after player loss.
        publish('player-unavailable', stamp, stamp); return
    end
    local map = fact(C_Map and C_Map.GetBestMapForUnit, 'player')
    local name = fact(GetZoneText)
    local level = fact(UnitLevel, 'player')
    if not integer(level, 1, 60) then level = missing() end
    local mapAfter = fact(C_Map and C_Map.GetBestMapForUnit, 'player')
    local nameAfter = fact(GetZoneText)
    local loggedAfter = fact(IsLoggedIn)
    local existsAfter = fact(UnitExists, 'player')
    local combatAfter = fact(InCombatLockdown)
    local finish = timestamp()
    if not integer(stamp, 1, 9999999999) or not integer(finish, 1, 9999999999)
        or finish.value < stamp.value or finish.value - stamp.value > 1 then
        publish('sample-time-unavailable-or-changed', stamp, finish); return
    end
    if not integer(map, 1, 10000000) or not is(name, 'string') or not same(map, mapAfter)
        or not same(name, nameAfter) or not same(logged, loggedAfter)
        or not same(exists, existsAfter) or not is(combatAfter, 'boolean') or combatAfter.value then
        publish('sample-unavailable-or-changed', stamp, finish); return
    end
    publish('sampled', stamp, finish, { inWorld = {status = 'observed', value = true},
        mapId = map, zoneName = name, level = level })
end
local sampler = CreateFrame('Frame', 'AlfadorWowZoneTestSampler')
for _, name in ipairs({'PLAYER_ENTERING_WORLD', 'PLAYER_LEAVING_WORLD', 'PLAYER_LOGOUT',
    'ZONE_CHANGED', 'ZONE_CHANGED_INDOORS', 'ZONE_CHANGED_NEW_AREA'}) do sampler:RegisterEvent(name) end
sampler:SetScript('OnEvent', function(_, event)
    elapsed = 0
    if event == 'PLAYER_ENTERING_WORLD' then
        newBoundary(); world = true; unavailable('entering-world-awaiting-read')
    elseif event == 'PLAYER_LEAVING_WORLD' or event == 'PLAYER_LOGOUT' then
        world = false; unavailable(event == 'PLAYER_LOGOUT' and 'logout' or 'leaving-world')
    else
        unavailable('zone-transition-awaiting-read')
    end
end)
sampler:SetScript('OnUpdate', function(_, dt)
    if type(dt) ~= 'number' or dt ~= dt or dt < 0 then return end
    elapsed = elapsed + dt
    if elapsed < 1 then return end
    elapsed = 0 -- No catch-up loop, max one sample per frame and 1 Hz.
    if world then sample() end
end)
local function quote(s)
    return '"' .. s:gsub('[%z\1-\31\\"]', function(c)
        if c == '"' then return '\\"' end
        if c == '\\' then return '\\\\' end
        return string.format('\\u%04x', string.byte(c))
    end) .. '"'
end
local function encode(v, depth)
    if depth > 16 then error('depth') end
    if type(v) == 'string' then return quote(v) end
    if type(v) == 'number' then return tostring(v) end
    if type(v) == 'boolean' then return v and 'true' or 'false' end
    if type(v) ~= 'table' then error('unsupported') end
    local parts = {}
    for k, value in pairs(v) do parts[#parts + 1] = quote(k) .. ':' .. encode(value, depth + 1) end
    return '{' .. table.concat(parts, ',') .. '}'
end
local function snapshot()
    local rows = {}
    for _, row in ipairs(samples) do rows[#rows + 1] = encode(row, 0) end
    local text = '{"schema":"alfador.wowf.zone-probe.evidence.draft1","evidenceClass":"local-only-not-core-delivered","samples":['
        .. table.concat(rows, ',') .. ']}'
    if #text > 65536 then return nil end
    return text
end
persist = function()
    local text = snapshot()
    if text then
        AlfadorZoneTestEvidence = (text:gsub('.', function(c) return string.format('%02x', string.byte(c)) end))
    else AlfadorZoneTestEvidence = nil end
end
unavailable('startup-awaiting-world-event')
local panel
local function export()
    local text = snapshot()
    if not text then return end
    if not panel then
        panel = CreateFrame('Frame', 'AlfadorWowZoneTestExport', UIParent)
        panel:SetSize(640, 400); panel:SetPoint('CENTER'); panel:SetFrameStrata('DIALOG')
        local title = panel:CreateFontString(nil, 'OVERLAY', 'GameFontNormal')
        title:SetPoint('TOP', 0, -10); title:SetText('Alfador-wow - local zone test (not a live connection)')
        local scroll = CreateFrame('ScrollFrame', nil, panel, 'UIPanelScrollFrameTemplate')
        scroll:SetPoint('TOPLEFT', 12, -35); scroll:SetPoint('BOTTOMRIGHT', -35, 42)
        local edit = CreateFrame('EditBox', nil, scroll)
        edit:SetMultiLine(true); edit:SetAutoFocus(false); edit:SetFontObject(ChatFontNormal)
        edit:SetWidth(585); edit:SetMaxLetters(65536); scroll:SetScrollChild(edit)
        edit:SetScript('OnEscapePressed', function() panel:Hide() end); panel.edit = edit
        local close = CreateFrame('Button', nil, panel, 'UIPanelButtonTemplate')
        close:SetSize(100, 24); close:SetPoint('BOTTOMRIGHT', -12, 10); close:SetText('Close')
        close:SetScript('OnClick', function() panel:Hide() end)
    end
    panel.edit:SetText(text); panel:Show(); panel.edit:SetFocus(); panel.edit:HighlightText()
end
SLASH_ALFADORZONETEST1 = '/alfadorzonetest'
SlashCmdList.ALFADORZONETEST = function(command)
    if command == '' then export() end -- UI shows frozen last 12 samples; no arbitrary commands.
end
