# External WoW data uploaders: source research - 2026-11-20

Scope: owner asks how Wowhead and comparable clients extract and upload data.
Read-only public-source research. No application downloaded/installed/executed,
no game input, no logging enabled and no production behavior changed.

## Wowhead: add-on collector plus desktop uploader

Wowhead's own Client page says Wowhead Looter collects data while the player
plays. The desktop client uploads collected data and supports automatic upload
after WoW closes. Its FAQ explicitly lists a running WoW process as a reason
uploads are disabled. Therefore data collection during play must not be confused
with continuous upload of the latest player state during play.
https://www.wowhead.com/client
https://www.wowhead.com/faq

The FAQ also describes viewing collected NPC/object/page/quest data before upload
and account login to attribute uploads. We did not inspect the current proprietary
client binary, collector implementation, wire schema, upload endpoint or token
storage. Do not claim a verified exact current SavedVariables name or parser based
only on these product pages. Public descriptions support collection -> saved data
-> external client -> server, not process-memory access as a requirement.

The current Client changelog includes version2.0.9771.6501, Forever Beta support
and updated Forever combat-log support. This is evidence Wowhead considers Forever,
not exact-build71037 acceptance or a guarantee of live quest/zone file export.
The FAQ contains older material elsewhere, so its explicit upload policy should
be attributed as published documentation rather than a native behavior test.
Its one-minute upload throttle does not establish a one-minute game save cadence.

## Warcraft Logs: a different game-produced file

Warcraft Logs' own getting-started guide describes both whole-file uploads and
live logging: desktop client monitors new events appended by the game to the
combat log and uploads them. It warns that outside raids the file may wait for
a quantity of events before writing, so sparse solo activity can be delayed.
https://www.warcraftlogs.com/help/start

This explains a real documented external live-uploader architecture without
proving arbitrary add-on data can be inserted into that file. It does not show
quest acceptance/progress/current-zone snapshots have the required fields or
bounded delay. No exact Forever71037 log format or native acceptance was tested.
No combat logging/collection is authorized by this research. Project boundaries
still prohibit reconstructing restricted combat state and analyzing other players'
damage; an existing uploader is not a license to copy its entire collection scope.

## TradeSkillMaster: separate inbound desktop data

TSM's official AppData.lua troubleshooting guide says its desktop application
distributes pricing data into the AppHelper addon. That is an example of app-to-
addon file distribution, not proof of a continuous addon-to-app channel.
https://support.tradeskillmaster.com/how-do-i-fix-an-error-about-appdatalua-being-empty

TSM's setup guide describes separate TradeSkillMaster and TSM_AppHelper addons:
https://support.tradeskillmaster.com/tsm-desktop-application/how-do-i-set-up-the-tsm-desktop-application

We encountered an explicitly unofficial TSM desktop repository. Do not attribute
that implementation to the official client. No code from it was used.

## Application to Alfador

A supported next milestone is automatic saved-snapshot delivery: permitted addon
API observations -> game-written SavedVariables -> Desktop file watcher -> safe
bounded decode/JSON validation -> authenticated Core historical intake. Preserve
original capture time, source, actor boundary, sequence and original unavailable
fields. Never execute imported Lua. Desktop forwarding must use existing explicit
observation sharing and verified connection authority; it must not infer intent
or promote a historical file to current state. Core remains the only brain.

This is an architectural proposal, not an implemented or accepted watcher.
Forever's actual save behavior and exact existing add-on schema need source/native
review before build integration. No automatic /reload, synthetic input or game
memory access is proposed. Manual /reload or logout saves are snapshots; file
watch frequency cannot make the underlying observations live.

The native logged-self-whisper experiment is retired. Its all8 API successes,
zero receipts and empty file do not establish a generic streaming log. Future
continuous quest/zone transport still needs a supported game writer with required
fields and verified during-play delivery. Wowhead's batch uploader documentation
does not remove that unresolved requirement.
