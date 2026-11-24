# Alfador-wow

Version 0.0.22 puts the arrow and distance below the portrait in **Portrait + Arrow** mode.
Drag the arrow or distance to move the pair independently.
Alfador remembers the placement when you switch display modes or reload.

Version 0.0.21 adds **Alfador-wow** under WoW's **Options → AddOns**.
The panel has a Display mode dropdown and checkboxes for Always show and
Follow tracked quests. Right-clicking Alfador or using
`/alfadorwowguide settings` opens the same panel.

Version 0.0.20 adds **Portrait + Arrow** to the navigator settings. It shows
Alfador, Janus on his arm, direction and distance in one compact display.

Version 0.0.19 restores the card title **Alfador**. Janus is rendered from
the Desktop overlay's `cloak-familiar-cat` artwork and sits on Alfador's
arm in the Card and Portrait displays.

Version 0.0.18 adds **Card**, **Portrait**, and **Arrow** modes. Right-click
Alfador or run `/alfadorwowguide settings` to change the mode. All three show
straight-line distance when the current quest stop is comparable. The
always-show toggle keeps Alfador on-screen between quests. Follow tracked
quests observes the quest selected in WoW's tracker. Manual pins and routes
use the same display. The saved preferences contain display settings only.
Native quest waypoints and game-provided map dimensions take precedence when
available. A missing or different-map stop leaves distance unavailable.

Version 0.0.17 adds a recommendation to the completed-route card. It ranks
readable catalog leads by listed XP, pickup distance, mapped travel legs,
follow-up links and authored story notes. It names the quest and pickup and
offers **Guide me there**. Open NPC dialogue can confirm an offer. Otherwise
the card says to check with the quest giver. Travel is a straight-line
estimate. Quest duration and XP per minute are unknown. Janus appears beside
Alfador using the existing Desktop Janus artwork converted to a WoW texture.

Version 0.0.16 enlarges Alfador's portrait and separates the destination
from the quest title. Pickup recommendations suppress quests positively
marked turned in when repeatability is unknown. The active arrow continues
in combat while the client exposes readable outdoor position and facing.
Quest-state advancement, voice, and map-pin changes resume after combat.

Version 0.0.15 follows a local quest route from a pickup through remaining
objectives and turn-in. Click **Plan route** in the nearby, XP, chains or
lore view, or use `/alfadorwowguide route 412` for Operation Recombobulation.
Use `route xp`, `route chains` or `route story` to choose a focus. The route
can group up to three nearby pickups with close catalog objective points.
Objective guidance uses the live journal and mapped catalog sources. If
an objective or turn-in cannot be located with that evidence, use the journal.
An unrelated map pin is preserved. Use **Pin stop** to place the current pin
explicitly, or **Skip quest** to continue with the other route entries.

`/alfadorwowguide tips on` enables occasional local chat tips on approach to
an eligible lead. `/alfadorwowguide voice on` enables local WoW text-to-speech
for route changes and tips where a voice is available. Both are off by default
and can be turned off with the corresponding `off` command. Desktop's voice
continues to serve its own conversation. The in-game route uses no live transfer.

Version 0.0.14 shows Alfador's portrait and a purple navigation arrow after
you pin a pickup. Drag the card to move it. Scroll over it to resize it.
The arrow uses your own readable outdoor position and facing. When you reach
the pickup, the card asks you to check the NPC. Once the quest appears in
your journal, pickup navigation stops. The card has no Desktop connection.

Version 0.0.13 adds **Pin first pickup** to the local guide. Click it to
place the first displayed pickup on the map. The guide checks your map and
the quest's current pickup status again before setting the pin.

Version 0.0.12 adds local quest guidance. On Forever build 71037, try:

- `/alfadorwowguide nearby` for the closest catalog pickup leads.
- `/alfadorwowguide xp` for nearby leads ordered by listed XP.
- `/alfadorwowguide chains` for nearby quests with direct catalog follow-ups.
- `/alfadorwowguide lore` for curated story quests in Dun Morogh and Elwynn Forest.
- `/alfadorwowguide pin <quest ID>` to set a waypoint for a displayed pickup.
  The command uses the game waypoint when accepted and can use TomTom if present.

The distance pilot covers Dun Morogh, Elwynn Forest and Ironforge. It uses
outdoor player position and checks the live map frame against the catalog
frame before comparing points. Results use straight-line proximity. The
catalog may be incomplete and offers need confirmation at the quest giver.
Run `/alfadorwowguide zone` for zone-wide leads when position is unavailable.
These views are local to WoW and use no Desktop or Core connection.

Version 0.0.10 adds `/alfadorwowguide offers`. Open a quest giver's list
of quests first. The command reads offers that WoW exposes in that dialogue.
Zone-wide eligibility and Core sharing remain outside this check.

Version 0.0.9 adds game-reported quest status to quest ID lookup.
`/alfadorwowguide check 218` compares the per-quest flag, journal status,
and whether that ID appears in the completed quest list. This diagnostic
runs once when requested and displays only the requested quest. An absent
list entry does not establish completion status or eligibility.

Version 0.0.8 suggests one ready turn-in in journal order and adds
**Copy for Alfador**. Click it, press Ctrl+C, and paste into Desktop chat.
This shares a manually selected journal snapshot as conversation text.
It includes the zone and quest statuses available to the guide without
adding character or account identifiers. The selection stays stable
while you copy it. Automatic journal delivery to Core remains unavailable.

Version 0.0.7 adds a local guide. Use `/alfadorwowguide` to see your journal
with ready turn-ins first. Use `/alfadorwowguide 218` to look up a quest's
pickup and turn-in references. Build the archive with `tools/build_addon.py`
to generate the full 5,287-entry catalog. The guide targets 70959 and 71037.
The original capture command retains its 70959 build constraint.


Version 0.0.6. Forever target: 1.60.1, build 70959, interface 16001.
The owner supplied GetBuildInfo on November 18, 2026. The name, folder and
command are Alfador-wow, `Alfador-wow`, and `/alfadorwow` respectively.

## Current function

Local read-only capture of your own character level, current player map and up to
50 on-map quest-log candidates. The default window shows actual game-sourced
quest names, objective progress and XP availability. Use **Show report** to see
the copyable technical JSON, and **Back to quests** to return to names. IDs stay
in diagnostics; missing names stay unknown. Titles come from GetInfo.title or
GetTitleForQuestID, with no restricted-title fallback, guessed mapping or network.
Untrusted quest names are displayed literally and grant no authority.

While the readable window is open, local selection/level/character/map checks
run at most twice per second; quest-log updates also request a bounded refresh.
This updates the displayed selection and its XP without rerunning the command.
Use **Refresh** for an immediate new capture. Refresh pauses during combat or
unknown safety state, and the window unregisters its quest event when closed.
Show report freezes the report and disables Refresh while you copy; Back to
quests resumes the readable view's updates. No upload, gameplay action or Core
connection is introduced by local UI refresh. Automatic updates do not post chat
notifications. Every exported report remains a dated historical observation.

Open the quest log and select a quest to capture
its displayed reward-XP API amount, when supported. The amount is read only for
that selected quest using GetQuestLogRewardXP with no arguments. Selection,
character and level are checked before/after; unavailable, failed and restricted
values stay explicit. No quest is selected or completed by the addon.

XP context records quest ID, player level, API and capture time. It must be
compared against the game's reward UI before being treated as verified evidence.
It is not earned XP. There is no reward cache across quests or levels. Missing
quest XP and all remaining travel/objective/turn-in times stay unknown.

Draft4 reports use `alfador.wow.forever.quest-pilot.capture.draft4`, adding observed
quest titles. The earlier draft3 fields retain the
selected quest ID at capture and a bounded rewardXPRead reason for each candidate
so missing XP can be diagnosed: missing selection, another selected quest, hidden
rewards, unavailable API, failed call, restricted/invalid value or binding change.
The local quest importer still accepts draft1/draft2/draft3 history. It never automatically repairs JSON
or treats imported identifiers/provenance as authentication. Local serial numbers
can reset on reload and are not replay protection. The current copy box is local
only: no network, SavedVariables transport, gameplay actions, tokens, combat
telemetry, gear, talents or other-player data. No GPS dependency is required.

## Limits and acceptance

IsOnMap is only candidate evidence; it does not establish exact player-zone
membership or all eligible quests. Display level is not minimum required level.
Missing API behavior remains unknown. Capture refuses combat, a missing secrecy
checker, another client build, more than 50 candidates or more than 200 log rows.
A refused capture hides the prior report. Inspect your own character identity
before sharing a copied export.

Earlier user reports demonstrated level and objective/candidate changes in Dun
Morogh. New XP behavior needs in-game acceptance; standard Lua mock tests do not
establish WoW secrecy/permission behavior or UI correctness. Reward XP API use was
reviewed against Blizzard source mirrored on the moving Forever branch:
https://raw.githubusercontent.com/Gethe/wow-ui-source/forever/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/QuestInfo.lua

The deployed Core research matrix inspected November 18 had no WoW entry. No
Core connection, authenticated WoW lookup or actual server revocation acceptance
is implemented by this addon. All interpretation/authorization remains in Core.

## Build and manual test

Build from the canonical project root: `python Forever/tools/build_addon.py`.
The builder checks importer, Core-candidate and Lua 5.1/5.4 mocked tests, packages
only the TOC, Alfador.lua, this README, a manual checklist and a hash manifest.
No test runtime or installer ships. See archive `MANUAL-TEST.md` for the exact
selected-quest XP acceptance steps. Canonical source stays in the WoW repository;
only verified addon files are copied into the owner-authorized game directory.

## Exact serial lifetime (Core review01 clarification)

`localCaptureSerial` starts at 1 for the first assembled report after Lua loads.
Manual capture, Refresh and automatic captures use the same file-local counter.
Closing the panel does not reset it. Reload/relog/client restart reload the code
and reset the counter; it is not persisted. Early refused captures do not increment
it; later encoding failure may leave gaps. Copying a snapshot retains its metadata.
Equal/backwards server seconds do not reset or correct the counter. Draft4 has no
exporter-session identifier; serial/time must not be used for cross-reload ordering
or identity/replay guarantees. Core restart binding is pending. 104 Lua mock tests
pass; these are not in-game reload acceptance. No runtime addon change required
for this clarification. See root research/core-review-serial-followup record.
