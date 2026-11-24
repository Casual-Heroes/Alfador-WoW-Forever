
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
