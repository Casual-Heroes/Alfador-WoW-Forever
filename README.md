# Alfador WoW Forever

Build from this checkout with `python tools/build_addon.py` after installing the
pinned test dependencies in `.builddeps`. Historical handoff packets, delivery
receipts and archived deployment candidates are local workspace references.

## Native quest-data coverage test (2026-11-23)

Shadowglen build 71037 and UI map 1438 have been confirmed in-game. An
[isolated API-only experiment](probes/Alfador-wow-Native-Quest-Test/README.md)
compares the empty journal, NPC offer and selected journal quest without
Polestar. The native offer for The Balance of Nature (456) returned 170 XP,
zero guaranteed items, two named reward choices with item IDs, and readable
description text. Native character coordinates were 58.69, 44.35. The direct
and map-specific waypoint calls were empty, but the native map POI API gave
accepted quest 456 a pin at 58.48, 43.62. It moved to 58.70, 44.27 after
both objectives were completed, as reported by the owner. The post-turn-in
dump confirmed quest 456 left the journal and was flagged complete. The nearby
unaccepted marker at 60.9, 42.0 was absent from the visible map-POI dump.

## Independently movable direction display (2026-11-22)

Version 0.0.22 anchors the arrow below the portrait by default in combined
mode. The arrow and distance share a draggable frame and saved placement.

## WoW AddOns settings (2026-11-22)

Version 0.0.21 puts the four navigator display modes and two display
preferences under WoW's **Options → AddOns → Alfador-wow**.

## Portrait + Arrow mode (2026-11-22)

Version 0.0.20 adds a compact mode combining the corrected portrait, direction
arrow and tracked-quest distance. Native visual acceptance is pending.

## Alfador portrait correction (2026-11-22)

Version 0.0.19 keeps the card title **Alfador** and uses the Desktop overlay's
original transparent Janus familiar on Alfador's arm. The owner confirmed
native tracked distance in 0.0.18. The corrected portrait needs a client check.

## Always-on navigator settings (2026-11-22)

Version 0.0.18 adds resizable Card, Portrait and Arrow modes with local
display preferences and optional native quest tracking on build 71037.
Core remains responsible for deeper analysis. The navigator uses only
in-game observations and changes no live transfer or model settings.

## Post-route recommendations and Janus (2026-11-22)

The owner confirmed the 0.0.16 A Favor for Evershine route changed to
Route complete after the real turn-in. Version 0.0.17 adds the next pickup
and Janus to the card. See the [in-game check](docs/ALFADOR-WOW-MANUAL-TEST.md).

## Completion checks and combat direction (2026-11-22)

On build 71037 the owner confirmed the 0.0.15 portrait, card and first pin
appeared. WoW's quest check confirmed quest 412 was already turned in.
Version 0.0.16 suppresses that pickup, refines the card and permits read-only
direction during combat when position and facing remain available.

## Local quest routes (2026-11-22)

The 0.0.15 candidate adds pickup, objective and turn-in stages on the three
build-71037 pilot maps. It includes opt-in travel tips, optional local WoW
speech, and separate XP, chain and story route selections. See
[the commands](addons/Alfador-wow/README.md) and [acceptance checks](docs/ALFADOR-WOW-MANUAL-TEST.md).

## In-game Alfador navigator candidate (2026-11-22)

Version 0.0.14 adds the existing Alfador Desktop portrait as an in-game
texture and a themed direction arrow for a selected pickup. The frame is
movable and scalable. Local navigation reuses build 71037 position checks.
The [native test](docs/ALFADOR-WOW-MANUAL-TEST.md) is pending.

## One-click pickup waypoint candidate (2026-11-21)

Version 0.0.13 adds **Pin first pickup** to the in-game guide. The button
uses the same checked waypoint placement as the `pin` command. See the
[route data review](../docs/research/2026-11-21-wowf-local-quest-routes.md).

## Local quest guidance candidate (2026-11-21)

Alfador-wow 0.0.12 adds local `nearby`, `xp`, `chains`, `lore` and `pin`
commands. Build 71037 is the distance pilot. Pickup coordinates come from
the pinned Polestar tables and are used only when live map corners agree.
Installed 0.0.12 in Forever's AddOns directory and verified all six files.
Native position, starter alignment and waypoint acceptance are pending.
See [the commands](addons/Alfador-wow/README.md) and [in-game checks](docs/ALFADOR-WOW-MANUAL-TEST.md).

## Live quest guidance acceptance (2026-11-21)

Core r106 was reported to format guidance for a supplied zone. The Windows
zone-change producer remains unverified on Forever 71037. See the [live quest guidance acceptance response](../docs/research/2026-11-21-wowf-live-quest-guidance-acceptance-response.md).

## Leveling release and live-zone work (2026-11-21)

Core leveling Review02 passed release preflight against r104. Native zone
delivery on Forever 71037 remains unverified. See the [Leveling release and live-zone handoff](../docs/research/2026-11-21-wowf-leveling-release-live-zone-next.md).

## Native 0.0.11 Ironforge scan observed (2026-11-21)

The owner shared the zone view for Ironforge (map 1455) on Forever 71037 at
level 9. The guide screened 310 mapped catalog pickups. It showed Data
Hoarders in the active journal, 24 leads matching the available catalog
checks and 19 leads needing more evidence. It excluded 266 by catalog
checks. The view did not verify any NPC offers.

Seasonal-looking, event and battleground entries dominate the output.
Sampled Polestar records share type 0 with ordinary quests, so the type
field alone cannot distinguish them. Separate event leads using sourced
category or schedule evidence and prioritize confirmed offers when
available. Desktop/Core replay with the copied zone view is pending.


## Alfador-wow 0.0.11 installed (2026-11-21)

The screenshot showed 0.0.10 command help. All six installed files now
match the 0.0.11 build manifest. The prior version is saved under Forever's
Interface directory as Alfador-wow-backup-0.0.10-2940aefb. Native zone view
and Core chat replay remain pending. Reload and run /alfadorwowguide zone.


## Alfador-wow 0.0.11 zone quest checks (2026-11-21)

`/alfadorwowguide zone` selects the player's observed UI map and ranks
mapped catalog pickup leads by listed XP. The generated index uses Polestar
2026.11.1 starter spawns and map envelopes from build 70532. Locations may
overlap and unmapped starts are omitted. On supported guide builds 70959
and 71037, the view checks the journal, completion, level, faction, race,
class, and known mandatory prerequisites. Only explicitly one-time quests
with a positive turn-in flag are removed as completed. Incomplete or
alternative prerequisites remain uncertain. Matched checks cannot confirm
an offer. The separate NPC offers view provides direct game evidence.

Copy for Alfador prepares the filtered results for a manual paste into
Desktop chat. Installed Core r103 already has semantic instructions to
answer planning questions using pasted quest context and the user's
constraints. This uses normal conversation and makes no trusted import or
automatic observation. Live model replay of this zone format is pending.

`Forever/builds/Alfador-wow-0.0.11-16001.zip` passed 299 existing tests
and packaged Lua 5.1/5.4 checks. Release data contains 495 starter-map leads
for Elwynn and 531 for Dun Morogh before filtering. Native acceptance and
installation of this candidate are pending.


## Alfador-wow 0.0.10 installed (2026-11-21)

The owner's screenshot showed 0.0.9 help. All six installed files now match
the verified 0.0.10 package. The 0.0.9 backup is in Forever's Interface
directory as Alfador-wow-backup-0.0.9-64d9d883. Reload and compare
`/alfadorwowguide offers` with the visible quest choices in an open NPC
dialogue. Native acceptance remains pending.


## Alfador-wow 0.0.10 quest offer check (2026-11-21)

The `/alfadorwowguide offers` command reads the documented gossip quest
list while a quest giver dialogue is open. It reports positive offers
for the player and refreshes on gossip events. It verifies one dialogue,
with no zone-wide inference or Core synchronization. Source API:
https://raw.githubusercontent.com/Gethe/wow-ui-source/3d8abb1da73acd38e412e24fb3f99454a6392346/Interface/AddOns/Blizzard_APIDocumentationGenerated/GossipInfoDocumentation.lua

Candidate `Forever/builds/Alfador-wow-0.0.10-16001.zip` passed 299 existing
checks plus packaged offer and completion checks in Lua 5.1 and 5.4.
Installation and native verification on Forever 71037 are pending.


## Native quest completion check passed for quest 311 (2026-11-21)

The owner's Alfador-wow 0.0.9 screenshot on Forever build 71037 shows Return
to Marleth (311) absent from the active journal, with the per-quest turn-in
flag set and the ID present in the completed quest list. This verifies both
completion reads for one known turned-in quest on this client. An active or
uncompleted comparison, list coverage, and delivery to Core remain unverified.


## Alfador-wow 0.0.9 installed (2026-11-21)

The owner's screenshot showed 0.0.7 command help. The verified 0.0.9 package
now matches all six installed files in Forever. Backup in the game's Interface
directory: Alfador-wow-backup-0.0.7-e6ff0e7c. Reload and run
`/alfadorwowguide check 311` to verify native completion reads on 71037.


## Alfador-wow 0.0.9 quest completion check (2026-11-21)

Guide lookup reports journal membership, the per-quest turn-in flag, and
objective completion where applicable. The explicit check command adds a
bounded GetAllCompletedQuestIDs membership check for one requested ID.
A missing list entry or unknown flag does not make a quest available.
No completion history is persisted or sent to Core.

Candidate: `Forever/builds/Alfador-wow-0.0.9-16001.zip`. All 299 existing
checks and packaged Lua 5.1/5.4 mocked checks passed. Native 71037 acceptance
is pending. Compare one known turned-in quest and one active quest with
`/alfadorwowguide check <id>`. Candidate IDs are 311 (Return to Marleth),
95041 (Data Hoarders), and 346 (Return to Kristoff). The 70532 catalog only
provides reference names. Core integration still needs a character-bound
observation contract and a verified transfer path.


## Alfador-wow 0.0.8 next-step and manual chat sharing (2026-11-21)

The standalone guide adds a zone label and suggests the first ready turn-in
in journal order. It has no distance or XP-per-minute ranking. Copy for
Alfador prepares conversation text with observed quest statuses and available
catalog turn-in names. The player copies and pastes it into Desktop chat.
No new Core transport or automatic journal sharing is available.

The 0.0.8 archive passed 299 automated checks, and the packaged guide passed
mocked refresh and copying checks on Lua 5.1 and 5.4. Version 0.0.7 remains
the most recent verified install. The owner confirmed the native 0.0.7
journal displayed Return to Marleth and Data Hoarders as ready to turn in,
along with the catalog NPC names. Native 0.0.8 acceptance is pending.


## Alfador-wow 0.0.7 installed (2026-11-21)

Installed the verified 0.0.7 package in Forever at the owner's request. All six
installed files matched the build manifest. Version 0.0.6 is backed up in the
Forever Interface directory as Alfador-wow-backup-0.0.6-5ffd21ce. Reload the
WoW UI and run /alfadorwowguide to verify the native command and journal view.
In-game acceptance is pending.


## Alfador-wow 0.0.7 standalone guide candidate (2026-11-21)

The archive at `Forever/builds/Alfador-wow-0.0.7-16001.zip` bundles an
Alfador-generated index of all 5,287 published Polestar quest IDs. The original
published data, generator, licenses and credits accompany the build. Only
Alfador's own Lua and generated data index are loaded in-game.

`/alfadorwowguide` shows the live journal and puts ready turn-ins first.
`/alfadorwowguide 218` shows pickup and turn-in references for that quest.
The guide targets builds 70959 and 71037. Catalog facts come from the Polestar
70532 snapshot. The build passed 299 existing checks and packaged smoke checks
on Lua 5.1 and 5.4. Game installation and native acceptance are pending.


## Alfador quest additions (2026-11-21)

Keep the pinned Polestar database as the upstream reference. Add missing Forever quests and corrections to Alfador's own database by quest ID. Record the source, client build, and verification status with each entry. Keep uncertainty visible when a quest or field cannot be verified.


## QuestieDB coverage comparison (2026-11-21)

QuestieDB v1.1.4 (933ec77a8151441c31a6356816feadaf145af73d) is a candidate
reference for polishing Forever quest coverage. All 4,244 IDs in its raw
Forever quest table already occur in the pinned 5,287-row Polestar catalog.
A text-only scan of the generated delta provider found 726 additional
comment-labelled IDs absent from Polestar. These are leads, including NYI
placeholders, and the count does not apply authored corrections or establish
build 71037 availability. No QuestieDB payload was merged or installed.

Inspect individual gaps and conflicting fields with recorded provenance.
Review upstream data permissions before redistribution. A second catalog
does not supply live quest progress or the Windows transport.


## Polestar quest database imported (2026-11-21)

The official database-only release, `data-v2026.11.1`, is stored in
`Forever/reference_data/polestar-forever-db-2026.11.1/` with its schemas,
licenses, credits, and `ALFADOR-SOURCE.json`. The release archive SHA-256,
all 15 table hashes and row counts, and all 5,287 unique quest IDs were
checked. The source reports 5,287 out of 5,408 quest records published for
build 1.60.1.70532. Availability and gaps on build 71037 remain unverified.

Alfador will use its own presentation and guidance logic. Ideas for the
in-game guide include grouping nearby objectives, offering optional tasks
along the route, and advancing when WoW confirms quest progress. The
catalog is local reference data. Live journal reads determine progress.
Desktop and Core transport remains a separate dependency for spoken
answers about current progress.


## In-game guide example (2026-11-21)

The Dun Morogh guide draft in reference_data/dun-morogh-stolen-journal.guide.draft1.json
defines three steps for quest 218. Quest ID and title match the local catalog.
The draft uses the game's quest log for the objective. Import, progress tracking,
and in-game acceptance are pending.


## Native zone-log candidate identified (2026-11-21)

Desktop's add-on writer finding stands. ForeverDB documents reading zone data
from WoW's own combat-log file during play (https://foreverdb.net/uploader).
That identifies a separate game-written source. Local install metadata lists
Forever 1.60.1.71037 and the Logs directory had no matching file at inspection.
No native timing or open-world boundary behavior is verified on this client.

An isolated tools/native_zone_log_probe.py reads only new ZONE_CHANGE and
MAP_CHANGE metadata from one native file. Synthetic filtering passed. For native
validation, manually enable combat logging, arm the observer before crossing a
known open-world boundary without fighting, and compare the result with the in-game
zone. Restore the prior setting afterward. Keep data local. The log's timestamp
and reader arrival are distinct, and zone and UI-map IDs must be checked before
use. A successful transition alone would leave ongoing freshness and in-world
status unverified. No production integration or journal transport is implied.


## Desktop response reviewed: live bridge blocked at producer - 2026-11-21

Received Desktop RESPONSE01 and evidence; canonical request document/archive
hashes independently match. Desktop reports1.0.70, Core r98, existing badge/import/
FFXIV regressions passed; these version/test claims were not rerun here. No
supported71037 in-game writer to Windows is established. Live bridge remains
blocked/unimplemented, not replaced by snapshot syncing. No new native test is
ready; retired chat-file and completed save experiments must not be repeated.
Acknowledgement is receipt-only, no duplicate review loop or owner actions.
Evidence: Forever/handoffs/desktop-wowf-live-bridge-20261121-response01-received/.
Ack: Forever/handoffs/wowf-desktop-live-bridge-20261121-ack01/.


## Desktop live-bridge task delivered for review - 2026-11-20

Owner explicitly requested Desktop involvement. Published source-only request
and sanitized native chat-file/save evidence to established shared Windows
Desktop exchange and Core inbox; local pins and remote archive hash verified.
Desktop must assess supported game writer/local reader, return exact evidence or
unknowns, and coordinate typed zone/in-world contract with Core before a native
test. Historical watcher is not completion of live goal; retired chat-file route
must not be repeated. Existing Desktop import/reader packets referenced, not
reimplemented. Owning Desktop OneDrive worktree differs from G:Projects checkout.
No app/source edit outside WoW repo, installer, test, worker activation or restart.
File delivery does not wake a chat; developer acknowledgement/work start unknown.
Packet: Forever/handoffs/wowf-desktop-live-bridge-20261120-request01/.


## Live context remains the owner goal; snapshots are limited - 2026-11-20

Owner clarified reload/logout snapshots do not meet the desired FFXIV-like live
zone/activity experience. Do not substitute automatic historical imports for that
goal or require repeated reloads as a live solution. Save Test only established
persistence behavior. No further owner test or production watcher build requested
by this clarification.

Read-only Core source review: gaming_modules/ffxiv/RUNBOOK.md describes Dalamud
observations; docs/ffxiv/CORE-CONTRACT.md describes local producer pipe -> Desktop
bridge -> authenticated AI WebSocket -> Core with fresh expiring evidence. This
is a different producer/transport from a WoW Lua addon's saved file. The existing
Core brain/voice is not the missing WoW component: supported fresh WoW egress is.
No equivalent supported WoW live bridge has been verified. No claim that FFXIV's
plugin method is an official WoW API or may be transplanted into WoW. Preserve
no-memory-reading/injection/protected-state-bypass boundaries. No runtime change.


## Native71037 saved-file test passed for reload/logout - 2026-11-20

Owner marked synthetic data in memory. No test file in60s during-play window.
Manual /reload wrote517bytes matching original marker/time. A second memory
marker left the first disk marker intact; owner logout to character selection
then wrote the second marker/time exactly. Bounded decoder never executes Lua.
This validates minimal historical save behavior, not real71037 quest API/Core
import, Desktop watcher or continuous feed. Exactly2 pinned test files/folder
removed; saved test evidence retained locally. No logging/production/Desktop/Core
change. Packet: Forever/handoffs/wowf-saved-file-20261120-result01/.


## Saved-file test installed with owner approval - 2026-11-20

Owner authorized install/save test. Exactly2 pinned isolated Save Test files
installed under Forever AddOns after absent-target/path/hash checks. Production
addon unchanged. Owner loading/enabling and first manual marker pending; no
native persistence result yet. No chat logging, Desktop install or Core restart.
Local evidence: Forever/local-evidence/2026-11-20-save-test/.


## Saved-file probe prepared; production journal has no save file yet - 2026-11-20

Canonical quest addon lacks SavedVariables and gates70959; local raw importer
also gates70959. Read-only Core current codec confirms same exact build tuple.
Owner-reported r98 deployment/badge71037 does not prove historical71037 admission.
Prepared isolated71037 manual save-marker probe and bounded non-executing decoder;
16 synthetic source/extraction checks pass;7 pins. No names/GUID/gameplay facts,
network, chat logging, automatic reload or lifecycle overwrite of last marker.
Native before/during/reload/logout file cases proposed only, not installed/run.
Desktop watcher and real journal persistence/build update remain separate work.
Packet: Forever/handoffs/wowf-saved-file-20261120-source01/.


## Wowhead and external-uploader research - 2026-11-20

Wowhead documents addon collection during play and automatic upload after WoW
closes; its FAQ says uploads are disabled while WoW runs. Current changelog also
mentions Forever combat-log support; this does not verify live quest/zone export
on71037. Warcraft Logs documents tailing a game-written combat file, with possible
sparse solo-write delays; TSM AppHelper distributes desktop pricing data inward.
No binary/install/native test or generic live transport discovered. Recommended
next milestone remains automatic historical saved-snapshot intake with sharing,
source/capture time/actor guards and safe non-executing decode. Source research:
Forever/docs/research/2026-11-20-wowhead-and-external-uploaders.md.


## Logged-addon chat-file experiment retired - 2026-11-20

Stop this native transport route. Blizzard's historical announcement concerns
abuse-reportable addon messages; generated docs expose an in-game receive event,
not a guarantee of local WoWChatLog.txt output. Source04 all8 native API successes
with45.016s/zero receipts/empty native log did not establish a Windows live feed.
Isolated test folder confirmed absent. Latest logging restoration/window closure
await owner confirmation; no new test, install or restart. Source-backed decision:
Forever/docs/research/2026-11-20-logged-addon-route-retired.md.


## Local READY result confirmed: no live log delivery demonstrated - 2026-11-20

Owner confirms all8 native acknowledgements during this countdown; screenshot
shows seq7/8 and completion with restriction_flag=true. Local reader ran45.016s,
0/8 receipts, no terminal error; native log metadata0bytes at test end. No precise
latency/common-clock recording or matching game echo verified. Native API return
success did not demonstrate live disk delivery. Avoid identical retries; require
source evidence before another transport proposal. Exactly2 pinned files/folder
removed; this run's logging restoration and window closure await confirmation.
Packet: Forever/handoffs/wowf-native-transfer-20261120-result03/.


## Local READY run ended with zero receipts - 2026-11-20

Owner screenshot and sanitized receipt confirm local READY reader completed
45.016s with0/8 matching markers and no terminal error. Native chat-log metadata
shows0bytes at test end; raw contents were not opened for post-test inspection.
Owner confirmation of all8 SEND acknowledgements during this specific countdown
is still required before judging send/reader overlap or live flush. No supported
continuous delivery demonstrated. Exactly2 pinned test files and empty folder
removed; owner logging restoration pending. No automatic retry or game input.
Evidence: Forever/local-evidence/2026-11-20-source04-local-ready-retest/.


## Local READY retest staged; owner-run window idle - 2026-11-20

Same exact Source04 two-file native pair staged for owner local-READY retest.
New development-only window pins the unchanged reader, starts idle, and displays
READY/countdown/receipt count for45s only after owner supplies a prepared session
and clicks. 53 existing checks pass; synthetic window integration confirms ready,
receipt, unrelated-text omission and close/deadline cleanup. Native UI acceptance
and live transfer pending. Logging untouched; no game input/reader auto-start,
Desktop install or Core restart. Owner must restore prior logging and operator
must remove only exact2 pinned test files after this run. Packet:
Forever/handoffs/wowf-local-ready-20261120-source01/.


## Marker test closed; rollback confirmed - 2026-11-20

Owner confirms all8 Source04 native send acknowledgements and native logging
restored OFF. Exactly2 pinned test files and empty folder removed. Reader was
ready for45.109s with zero markers; actual send/window overlap remains unknown.
Native self-WHISPER API success is observed; live disk delivery is inconclusive.
No Desktop/Core deployment, raw log export/deletion or production feed claim.
Sanitized outcome: Forever/handoffs/wowf-native-transfer-20261120-result02/.


## Native self-whisper success observed; delivery unresolved - 2026-11-20

Owner screenshots show Source04 STARTED and native-success SEND acknowledgements
for sequences1-4 with restriction_flag=true; owner explicitly confirms all8 sends.
This is native API return success, not matching echo or disk-flush proof. The
45-second reader received zero matching markers. Common-clock evidence does not
establish that sends occurred inside its window; no transport-failure conclusion.
All8 native acknowledgements are confirmed; logging restoration confirmed OFF by owner. Two pinned
test files and empty folder removed after the reader ended; raw log untouched.
No production addon/Desktop/Core change or live-feed claim. Sanitized local
receipts: Forever/local-evidence/2026-11-20-source04-native-test/.


## Revised self-whisper test staged - 2026-11-20

Owner authorized proceeding with the revised bounded experiment. Source04 records
restriction flag diagnostically; native send result and chat lockdown still stop
failures. Open-world-only guard added. 53 synthetic source checks and the same 53
from the pinned extracted archive pass; reader unchanged from Source03. Exactly
two hash-pinned isolated test files staged after absent-target/path checks. Logging
unchanged; owner prepare and reader-ready/start handshake still pending. No native
marker, reader, Desktop install or Core restart yet. No live delivery claim.
Packet: Forever/handoffs/wowf-continuous-transfer-20261120-source04/.


## Native transfer verdict corrected: self-whisper untested - 2026-11-20

Source03 stopped at its local restriction-flag gate; it never attempted a native
send. The owner's true getter result does not establish a WHISPER rejection.
An older-build Campkeeper author report describes working messages with that
same flag true. Exact build 71037 behavior and live log delivery remain untested.
This supersedes the blocked/unavailable interpretation below; original evidence
and completed cleanup remain valid. No runtime code or installation changed.
See Forever/docs/research/2026-11-20-native-transfer-interpretation-correction.md.


## Native transfer candidate blocked; rollback complete - 2026-11-20

Owner actual71037 client reports C_ChatInfo.AreOutgoingAddonChatMessagesRestricted()
==true (function exists). Source03 prepare correctly stopped before any marker;
reader never started and latency not tested. Logged-addon-message candidate is
unavailable under this native restriction. No bypass/alternate message channel.
Both staged test files and empty folder removed after exact pin/path checks;
owner screenshot confirms logging restoredOFF. Raw log never read/shared/deleted.
Core received/hash-verified sanitized native receipt. No supported continuous
Forever->Desktop route demonstrated; saved snapshots remain historical and public
catalog remains independent. Not a universal claim about every future realm/API.
Packet:Forever/handoffs/wowf-native-transfer-20261120-result01/.

## Native build mismatch diagnosed; Source03 prepared - 2026-11-20

Owner in-game GetBuildInfo screenshot after reload shows1.60.1/build71037/
interface16001 (Nov18,2026). Source02 test expected70959; prepare correctly failed
world/build gate and no native marker/reader ran. Minimal Source03 changes only
Lua expected-build literal and TOC source version; reader byte-identical to Source02.
45 synthetic source/extraction checks pass. Source03 replacement hashes await
approval because installed pair was exact-pinned Source02. Existing native-test
approval otherwise persists; prior logging state still unknown for restoration.
No installed files/logging/Core/Desktop changed by this correction. New build does
not independently validate API, source catalog, live transport or zone freshness.
Packet:Forever/handoffs/wowf-continuous-transfer-20261120-source03/.

## Transfer source02 fixes startup race - 2026-11-20

Core's reader-start race reproduced/design accepted. Revised isolated probe now
prepares idle label -> reader opensEOF/prints ready -> owner manually starts same
prepared run. Source/exact extraction43 synthetic checks pass;10 pins verified.
Windows synthetic shared-read/write/delete and actual readerCLI readiness cases
pass; all8 synthetic markers preserved. Native game delivery still unverified.
Closed source2 receipts include monotonic times, exact sequences, dup/order/batch
counts. Concrete2-file staging/no-overwrite/manual logging/rollback proposal is
in probe WINDOWS-TEST.md. Matched packet sent/hash-verified to Core. No actual
chat log opened, installation, native logging toggle or real message. Separate
owner native-test approval not yet granted. Source02 supersedes first experiment
for testing. Packet:Forever/handoffs/wowf-continuous-transfer-20261120-source02/.

## Continuous transfer required; native transport unproven - 2026-11-20

Owner requires automatic in-play updates; historical save watching/manual imports
are not the live goal. Built an isolated native logged-addon SELF-message marker
experiment plus bounded local reader:25 synthetic checks pass in source/extraction.
No gameplay payload, no auto logging, no actual native messages/install, no Core
upload. API documents logging/throttling but not live flush; exact-client/realm/
policy/delay remain unverified. Core received/hash-verified the feasibility packet
for joint Desktop review and native test procedure. Existing1Hz local sampling
is not transfer. Actual continuous feed remains unimplemented/unverified pending
supported in-play transport proof. Root evidence:
`docs/research/2026-11-20-continuous-transfer-feasibility.md`.

## r97 historical character source reviewed - 2026-11-20

Received/verified r97 candidate:533 content pins, independent exact-extraction
suite1,416 tests passed in20.985s. Recorded name/level/zone with original capture
time uses existing shared draft4 snapshot; no addon/schema/Desktop wire update
needed. No live location/class/gear inferred. Service readback remains r96
(20261119-r96-wowf-quest-followup-candidate02); no promotion/restart occurred.
Source review delivered/hash-verified to Core. Existing isolated zone probe source
and38 mocked checks are separate: actual client samples and bounded Desktop
receipt remain unverified; saved evidence stays historical. Windows r97 character/
zone text, spoken and withdrawal acceptance not performed. Review/evidence packet:
`Forever/handoffs/core-wowf-r97-20261120-received01/`.

## Current-zone source probe - 2026-11-20

Owner-reported r96 overview/quest/grinding improvements are separate from a live
zone feed. Isolated zone probe/schema/safe historical decoder prepared;38 mocked
Lua5.1/5.4 checks pass in source and exact extraction. No actual client build,
in-world/zoning/unavailable sample or bounded Desktop delivery verified. First
native deliverable remains partial.1Hz local sampling is not transport latency;
SavedVariables remains historical. Explicit unavailable markers, ephemeral opaque
boundaries and increasing sequences included; no GUID/name/raw captures collected.
Source packet delivered/hash-verified to Core for Desktop joint review. No install,
activation, service/config change. Root research:
`docs/research/2026-11-20-zone-probe-source-and-transport-limits.md`.

## Owner ON/OFF feedback and grinding relevance - 2026-11-19

Owner reports public Dun Morogh discussion/catalog available with observation
sharing ON and OFF. This confirms owner-reported public continuity, not imported
journal withdrawal or audible voice acceptance. Both sharing states FAIL semantic
relevance for a best-grind-spot question: it returns the generic quest list. Missing
position response avoids invented closeness but provides limited nearby context.
Core final catalog fallback inspected read-only; runtime classifier choice was not
captured. Concrete source correction request delivered/hash-verified to Core:
answer the actual grinding goal or explain missing evidence/ask one short useful
question; no phrase regex, client routing, guessed best spot or private fact reuse.
Two ON/OFF design cases added (11 total), not executed runtime regressions.
Packet:Forever/handoffs/wowf-grinding-relevance-20261119-review01/.
No installed code/config/sharing setting changed.

## Native Windows r95 typed checks - 2026-11-19

Installed release readback:20261119-r95-wowf-natural-guidance-candidate02. Five
native Alfador Chat typed checks pass: area follow-up, named-quest successor,
missing compatible position without proximity claim, FFXIV override, non-game
switch. Sharing visibly on. Exact Desktop version was not independently checked.
One quality limitation: tell-me-about a named quest repeated the general list;
subsequent successor question resolved correctly. Outcome summaries delivered to
Core/hash-verified without snapshots or unrelated chat. Real journal overlap,
spoken follow-up/audibility and sharing-off separation remain unverified/pending
user action. No privacy settings, installed services or feature gates changed.
Evidence: Forever/handoffs/wowf-r95-20261119-typed-acceptance01/.
This supersedes older statements that no native typed area acceptance exists;
it is not complete voice/private end-to-end acceptance.

## Governing conversation design - 2026-11-19

Adopted verified Core natural-dialogue response02, superseding response01's
explicit-query recommendation only. Core uses existing semantic admission and
conversation context, with no required repeated game/zone phrase or trigger regex.
Stated area scopes public retrieval without proving location; historical journals
remain capture-time evidence. Public/private guards and text/audio lifetimes are
independent; missing optional evidence does not block other valid conversation.
Nine design acceptance cases recorded (not executed regressions). Source/evidence
limits unchanged; installed r92 narrow journal trigger is not claimed replaced.
See `Forever/docs/CONVERSATION-DESIGN.md` and
`Forever/contracts/conversation-acceptance.source.json`. Correction/adoption sent
and hash-verified to Core/Server A; Desktop coordination remains Core-owned.

## Area quests, distance and lore resumed - 2026-11-19

Owner explicitly resumed Server A reference work. Built a source-only Core wowf
area module and pinned Dun Morogh reference pack:93 quests,83 with pickup/turn-in
points, story excerpts/chains;16 focused tests pass in source/exact extraction.
Two closed schemas validate; offline compiler reproduces all normalized bytes.
Source remains ambiguous for exact70959, availability unknown, lore importance
unreviewed; same-area percentage distance is not meters/route ETA. Code supports
other maps when source packs expand. Source packet delivered/hash-verified to
Core and Server A with concrete integration/curation/position-contract tasks.
Core r92 live install is reported by its receipt; Windows acceptance unverified.
No service/addon install or activation in this milestone. Root research record:
`docs/research/2026-11-19-area-quests-distance-lore-resumed.md`.
This supersedes older API deferral/current-work statements below.

## Corrected addon-only intake ? 2026-11-19

Corrected r92-based Core candidate received: all520 pins verified, independent
exact-extraction suite **1,404 tests passed** (25 WoW). Review01 intake corrections
are implemented in this source; no live acceptance or deployment claimed.
After addon reload/relog, importing requires an explicitly new AI connection;
no silent reconnect and no addon schema/reinstall needed. **Server A reference API
is deferred and no longer an intake prerequisite.** Desktop typed import bridge
and Core snapshot-bound journal-to-answer/voice remain unfinished. Checklist and
receipt delivered to Core/Server A with hashes verified. Root research:
`docs/research/2026-11-19-corrected-wowf-addon-only-intake.md`.
Earlier entries below are historical and may state superseded prerequisites.

## Server A contract received ? 2026-11-19

Verified Server A's three artifact hashes and seven source pins; independently
reran its five focused tests (all pass). Forwarded verified packet to Core and
returned two source-contract gaps: runtime source-pin enforcement and a closed
result schema. Temporary modified-data probe confirmed altered source XP is
returned, still ambiguous/advice-disabled. Exact70959 authority and audit migration
remain registration blockers. Four public source matches are ambiguous; Stolen
Journal remains outside this release. Core intake/r92 corrections still pending.
No rollout or addon runtime change. See root research record
`docs/research/2026-11-19-server-a-wowf-contract-review.md` and delivery evidence.
This supersedes earlier statements that no Server A contract had been received.

## Review correction ? 2026-11-18

Core candidate01 is **changes required, not rollout-ready** despite its passing
original suite: ordering, body admission/deadline, privacy-filtered audits and r92
rebase remain Core work. Addon serial resets with Lua reload/relog/restart; draft4
has no exporter epoch. Clarification and exact Server A request delivered to both
maintainers with hashes verified. 104 addon mock tests pass; runtime addon unchanged.
Server A quest contract and Core restart binding/corrected source still pending.
See root `docs/research/2026-11-18-core-review-serial-followup.md`. Earlier entries
below describe historical milestones, not current rollout approval.

## Current source milestone ? 2026-11-18

Core `wowf` historical report intake candidate is prepared, default off, using the
existing shared AI authority. **17 new tests pass; all 1,364 Core regression tests
pass in source and from the packaged archive.** Both maintainers received the
hash-verified source-only review packet. This is not deployed or enabled; no real
owner session, public quest lookup, dialogue/voice or live game connection is proven.
Next: maintainer contract review and separate rollout/real-session acceptance.
Evidence: `docs/research/2026-11-18-core-wowf-historical-intake-candidate.md` in the
project root; delivery receipt under `Forever/docs/evidence/`. Earlier entries below
are chronological investigation history and may describe superseded versions.

Primary development target. Addon source belongs in `addons/`.

Later owner-requested work: [unaccepted-zone-quest recommendations, private text
and optional voice](docs/ENHANCEMENTS.md). Current milestone remains the scoped
quest evidence/Core connection; this roadmap is not implemented capability.

## Current milestone: current-zone leveling pilot

Latest owner API capture: **The Stolen Journal ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â 550 reward XP at player level 5**,
matching its selection/level/capture context. The amount equals the earlier
native UI screenshot; same-level contemporaneous comparison and timing remain
pending. Core delivery is still unavailable. See parent refresh/reward research.

Latest installed: **0.0.6**. The readable view follows selected quest changes
while open and has **Refresh**; **Show report** freezes its snapshot for copying.
Refresh pauses in combat and stops on close. 168 local checks pass; actual new
refresh behavior needs owner acceptance. Screenshots verify native rewards of
250 XP for The Boar Hunter and 550 XP for The Stolen Journal; the latter still
needs a matching selected-quest API capture. No Core connection or speed ranking.

First positive named XP capture: the owner reports **The Boar Hunter ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â 250 XP**
at player level 4, with matching selected-quest context. **The Stolen Journal**
stays unknown while unselected. Readable summary supplied; independent reward-UI
comparison, timing and Core delivery remain pending. See capture-5 research.

Latest installed version: **0.0.5**, with game-observed quest names and a readable
default quest summary. **Show report** reveals technical JSON; **Back to quests**
returns to the names. Refer to quests by NAME when talking with the owner. Missing
names stay unknown; no ID mapping from other WoW editions. 152 local checks pass,
but the new view and title/XP accuracy still need in-game acceptance.

Latest installed version is **0.0.4** (135 local checks). A draft2 user capture
had unavailable XP for 183/218 without a reason. Draft3 now adds the selected
quest ID and bounded per-candidate XP-read diagnostics; XP guards remain intact.
Reload/select a quest/run `/alfadorwow` and compare against the reward UI. Older
draft1/draft2 reports remain supported. Core maintainer replies are pending.

Latest: **0.0.3 is installed**, with 119 local checks passing. Select a quest in
the quest log and run `/alfadorwow` to observe its reward-XP API amount when
available; compare against the UI before accepting it. Draft2 binds that amount
to the quest/level/capture context. No XP is copied across other quests or levels.

Core r91 has no WoW research entry. The owner-authorized implementation request
was delivered/hash-verified to Core and Server A, requiring Core's own
`alphador_core/gaming_modules/wowf/` folder. Real lookup and Core delivery await
the server contract; no server rollout or user session was performed here.

First owner-supplied capture received: Totem level 3 in Dun Morogh, three quest
candidates (170, 233, 182), build/interface matching the target. A separately
corrected JSON copy passed local validation; the raw paste contained an invalid
schema escape. This is partial in-game evidence reported by the user, not full
acceptance. Quest XP/timing and authenticated Core delivery remain unavailable.

Subsequent user captures report quest 182 objectives becoming complete, then
Totem reaching level 4 with candidate 233 replaced by 183. These demonstrate
reported state changes; turn-in history/quest-chain identity and XP values are
not established. See the parent first-user-quest-capture research for evidence.

Owner-authorized manual-test installation completed November 18:
`E:\Program FIles\World of Warcraft\_forever_\Interface\AddOns\Alfador-wow`.
TOC/Lua/README bytes were verified against the built archive; no existing addon
was overwritten. No game launch/restart or in-game execution was performed.
Earlier ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã¢â‚¬Å“not installedÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â notes below describe the build-stage state.

Active scope: Totem Ale (Paladin), multiple eligible quests in whichever zone the
character currently occupies, and ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã¢â‚¬Å“What should I do next to level in twenty
minutes?ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â Evaluate up to 50 candidates. Verified reward XP divided by remaining
travel + objective + turn-in time; missing times means XP-only comparison with
no fastest claim. Lore, gear/talents and avatar work are deferred. Reforged stays
separate. See [pilot scope and acceptance](docs/LEVELING-PILOT.md).

The [quest probe](addons/Alfador-wow/README.md) targets owner-reported
interface 16001 on 1.60.1/70959. It is installed for the owner-requested manual
test; in-game execution remains unverified.
The [raw JSON importer](tools/quest_capture_import.py) validates its separate
draft format offline. The Core-side candidate and synthetic access demo are in
`core_candidate/`; no real Core/QuestLog session or lookup has been verified.
The manual-test build passes 94 checks: 33 importer, 29 pilot and 32 mocked Lua
runtime checks across Lua 5.1/5.4. Actual WoW behavior remains unverified.
The [manual-test checklist](docs/ALFADOR-WOW-MANUAL-TEST.md) covers the next run.
ZIP and hash manifest are under ignored `builds/`; the subsequent manual-test
installation copied only the three verified addon files described above.

The [earlier broad foundation](docs/DATA-FOUNDATION.md) and
[character contract](contracts/README.md) remain deferred groundwork.

The first implementation is the [offline JSON importer](tools/README.md): 29
synthetic tests pass, with bounded input and identity/build/partial-data checks.
It sends nothing to Core. The [Core proposal](docs/CORE-INGESTION-PROPOSAL.md)
records the required handshake and acceptance; it is prepared locally only.

On November 18, read-only inspection confirmed the installed Forever executable
1.60.1.70959 (flavor wowf). The owner subsequently supplied GetBuildInfo(): version
1.60.1, build 70959, Nov 13 2026, interface 16001. A probe manifest is staged from
that report; supported APIs and in-game behavior remain unverified.

Resume with `../AGENTS.md`, `../docs/STATUS.md` and the dated capability research.
Keep Forever test evidence separate from Retail; shared APIs are not proof of
feature availability. Never substitute a Retail result for Forever acceptance.

## Dedicated repository (2026-11-15)

This edition is a separate private repository: Casual-Heroes/Alfador-WoW-Forever.
Read this repository's AGENTS.md and docs/STATUS.md. Shared instructions and docs
were preserved as a dated bootstrap snapshot from the parent project; the parent
files remain intact. Changes to either snapshot require explicit edition scope.
The one WoW dispatcher serializes Forever, Retail and Shared assignments. It has
review-only authority, with no privileged recipes or background installation.

## In-game companion review (2026-11-18)

Installed path: `E:\Program FIles\World of Warcraft\_forever_`; executable
`1.60.1.70959`, flavor `wowf`, matching root `.build.info`. This is filesystem
evidence; no addon or API was tested in game. The owner subsequently reported
interface 16001; see the current pilot above.

Alfador's existing server Core remains the brain. Portrait/bubble UI is a
candidate; live permitted observations to Core, inbound replies and custom voice
inside a native addon remain unverified. Hidden Desktop networking or voice does
not by itself provide a native addon connection. Next: in-game build/interface,
isolated local UI acceptance, then supported transport verification.

See the canonical parent review:
`../docs/research/2026-11-18-in-game-companion-review.md`.
