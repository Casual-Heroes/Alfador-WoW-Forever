# WoW project handoff

## ForeverDB bulk import design review (2026-11-23)

The [ForeverDB developer API](https://foreverdb.net/developers) documents
fetching with a private plugin key and bundling credited data. The planned
import reads metadata, quests and zones in pages of up to 100, retains source
builds and point provenance, and fetches detail for explicit chain links.
The free tier allows 30 requests per minute and 5,000 daily per account.
Objective coordinates, descriptions, XP and complete rewards coverage still
need an authorized sample. No key was requested and no import was performed.

The [independent Forever dataset](https://github.com/danielalanbates/wow-completionist-data)
puts Dirania Silvershine (8583) at 60.8, 42.0 on UI map 1438 for quests 3521
and 3522. These wiki-sourced points are leads for the marker reported on
Forever 71037. The dataset's client membership pin is 70790. A native NPC
dialogue read is needed to identify the actual offer. See the
[Shadowglen native evidence](../README.md#native-quest-data-coverage-test-2026-11-23).

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

Updated 2026-11-18. Canonical project: `G:\Projects\Alfador-WoW`.

## Direction

LATER ENHANCEMENT: unaccepted current-zone quests plus verified prerequisites,
character-level XP and route/objective/turn-in estimates, with Core recommendations
by name in private whisper-style text and voice when enabled. See ENHANCEMENTS.md.
Recorded only; current accepted-quest/Core milestone unchanged. No full-zone
catalog/ETA/inbound transport or whisper/voice capability is claimed implemented.

LATEST CAPTURE-6: owner reports level 5, The Stolen Journal selected, 550 XP,
matching context, one candidate/zero unresolved. Amount matches earlier UI
screenshot but level changed from 4; no general scaling or refresh-mode proof.
Boar Hunter absence does not prove turn-in. Original retained, corrected schema
copy validates in ignored local-evidence. No new build, timing or Core delivery.

LATEST 0.0.6: owner screenshots confirm native reward UI Boar Hunter 250 XP and
Stolen Journal 550 XP. Boar Hunter matches prior API evidence; Journal API read
is still pending. Screenshots expose stale snapshot selection in 0.0.5. Added
Refresh plus safe 2 Hz maximum visible-view change checks/quest-log event refresh;
report copy freezes, combat pauses, close unregisters events. Built/installed,
168 local checks pass. No in-game new-refresh acceptance or Core connection.
Receipt: docs/evidence/2026-11-18-alfador-wow-0.0.6-installation.json. Next user
reload/select The Stolen Journal with readable window open and compare 550 XP.

FIRST NAMED XP CAPTURE: owner draft4 reports The Boar Hunter selected, 250 XP,
matching context at level 4; The Stolen Journal not selected/XP unknown. Readable
summary also supplied. Local validation accepts separately corrected schema
string; raw paste preserved under ignored local-evidence/2026-11-18-totem-capture-5.
Reward UI match and actual earned XP are not yet confirmed. Next: verify 250
against game reward UI, then select/capture The Stolen Journal. No Core delivery.

LATEST 0.0.5: owner requested human quest names instead of numeric IDs. Names
read from the game log/title API, shown by default with progress/XP availability;
Show report/Back to quests separates technical data. Missing/restricted titles
are preserved, WoW markup displayed literally. Draft4 adds title observations,
older captures supported. Built/installed with 152 local checks passing;
in-game name/UI/XP acceptance pending. Receipt:
docs/evidence/2026-11-18-alfador-wow-0.0.5-installation.json. No Core changes.

LATEST 0.0.4: owner draft2 capture-4 reports 183/218 but no XP; cause unknown.
Added draft3 selected quest and bounded XP-read reasons, retaining prior schemas
and selection/visibility/identity guards. Built/installed with 135 local checks
(42 importer, 29 Core candidate, 64 mocked Lua). Exact receipt:
docs/evidence/2026-11-18-alfador-wow-0.0.4-installation.json. User reload and XP
diagnostic capture pending; no in-game acceptance. No WOWF response in either
maintainer outbox at the check. No actual product session or Core delivery.

LATEST XP BUILD November 18: 0.0.3 installed, 119 local checks (40 importer,
29 Core candidate, 50 mocked Lua) pass. Draft2 reads selected log quest XP only
with before/after selection and character/level guards. XP UI verification and
timing remain pending; draft1 history supported. No game reload by agent.

Actual Core r91 inspected read-only: no WoW research operation exists. Owner
requires Core gaming_modules/wowf alongside ffxiv and explicitly authorized
sending the implementation request to Core/Server A. Six files delivered and
remote hashes verified in each inbox; no raw captures or credentials included.
No server source/service/grant changed and no real product lookup succeeded.
Receipts: docs/evidence/2026-11-18-alfador-wow-0.0.3-installation.json and
docs/evidence/2026-11-18-wowf-lookup-request-delivery.json. Await exact contracts
and reviewable server candidate; client XP acceptance is next manual action.

THIRD USER CAPTURE November 18: Totem now level 4, candidate 233 absent and 183
new/incomplete; 170/182 remain objectives complete. Same claimed build/zone and
identity; zero unresolved entries, serial 2. Candidate-set change does not prove
a turn-in/chain or XP amount. Separate corrected JSON validates; original
preserved in ignored local-evidence/2026-11-18-totem-capture-3. Basic progress
updates recorded; reward XP, timing, authenticated Core lookup remain pending.

SECOND USER CAPTURE November 18: quest 182 objectivesComplete false -> true;
170/233 remain true, all three still on quest/not turned in. Identity/build
claims match; interval 266 seconds does not measure objective time. Both serials
are 1. Original retains invalid schema escape; corrected copy validates and is
stored under ignored local-evidence/2026-11-18-totem-capture-2. No Core delivery.
Next: ordinary turn-in followed by fresh capture and quest-log comparison.

FIRST USER CAPTURE November 18: owner supplied Totem level 3 in Dun Morogh,
map 1426, build 1.60.1/70959/interface 16001; quest IDs 170/233 objectives complete,
182 incomplete, all on quest/not turned in; zero unresolved entries. Raw paste
rejected for invalid schema escape; separately corrected copy passed validation.
Original/normalized/receipt retained in ignored local-evidence. See parent
`docs/research/2026-11-18-first-user-quest-capture.md` for hashes and limits.
This establishes partial user-reported game evidence, not full manual acceptance
or a verified Core session. No XP/timing or Core delivery is available yet.

LATEST NAME November 18: owner requested **Alfador-wow**. Renamed source to
`addons/Alfador-wow`, TOC to `Alfador-wow.toc`, Lua to `Alfador.lua`, command to
`/alfadorwow`, and installed folder to `_forever_/Interface/AddOns/Alfador-wow`.
Version 0.0.2 passed 94 build checks; installed bytes match the rebuilt archive
SHA-256 `c5c60ebe65b711ece4a175adfe0bd79fafea0ffd474202c9aadc2f9c20a94bfd`.
Old installed folder is absent; no duplicate addon, restart or in-game execution.
Receipt: `docs/evidence/2026-11-18-alfador-wow-rename.json`. Build tool now
`tools/build_addon.py`; manual checklist `docs/ALFADOR-WOW-MANUAL-TEST.md`.
All older names and paths below are retained historical evidence.

LATEST INSTALLATION UPDATE November 18: owner requested the manual-test addon in
the actual game AddOns folder. This explicitly overrides isolation for this
specific test deployment only. Installed/verified TOC, Lua and README at
`E:\Program FIles\World of Warcraft\_forever_\Interface\AddOns\AlfadorQuestProbe`.
No existing addon overwritten, no game launched/restarted or operated. Receipt:
`docs/evidence/2026-11-18-quest-probe-installation.json`. No in-game acceptance or
Core connection yet. Earlier ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã¢â‚¬Å“not installedÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â statements are historical.

Latest build evidence November 18: manual-test archive
`builds/AlfadorQuestProbe-0.0.1-16001-70959.zip` produced and member/hash verified.
SHA-256 `b450aeec59e3a6289c6c9fbbe7a6c7fa025db383b8859d78406d09f3a76b1080`.
94 checks passed: 33 importer, 29 pilot, 32 mocked Lua runtime tests (5.1/5.4).
Pinned test-only Lupa 2.6 installed under ignored `.builddeps/`; no global
Python changes and no build dependencies shipped in the ZIP. Fixed stale export
display after refused capture. Build tool never writes to the game installation.
No in-game execution, UI visual acceptance, real API/secret-value validation,
Core delivery or server deployment occurred. See QUEST-PROBE-MANUAL-TEST.md.

LATEST OWNER SCOPE: Totem Ale, Paladin; multiple eligible quests in the observed
current zone (up to 50), twenty-minute leveling advice. This supersedes the
earlier broad first milestone/two-quest limit. Lore, equipment/talents and avatar
are deferred. Reforged remains unchanged. See LEVELING-PILOT.md.

Owner GetBuildInfo report: 1.60.1, 70959, Nov 13 2026, interface 16001, followed
by blank strings. Staged isolated quest probe uses that interface/build guard;
not installed or in-game tested. Raw pilot JSON importer and offline Core-side
comparison/security candidates implemented. 62 Python tests pass; no Lua runtime
was available for execution. Real session, verified quest XP, supported GPS ETA
interface, Core/QuestLog enforcement and end-to-end delivery remain pending.
Earlier scope/unknown-interface notes below are retained history.

First implementation November 18: `tools/observation_import.py` provides offline,
bounded JSON validation and historical snapshot receipts. 29 Python 3.12 tests
passed; no dependencies installed, Lua executed or network connection opened.
See `tools/README.md` and `docs/CORE-INGESTION-PROPOSAL.md` from this edition root.
No Core protocol is approved and no report has been transmitted. Awaiting actual
in-game build/interface evidence before an installable Forever export probe.

November 18 active scope: character/talents, equipped gear, gear/talent comparison,
objective-specific equipment calculations and zone/quest knowledge. Owner's
initial classes are Druid and Paladin, PvE tanking and DPS. See DATA-FOUNDATION.md
and ../contracts/README.md. A local JSON Schema proposal compiled, accepted a
synthetic unavailable fixture and rejected eight invalid contexts using existing
Ajv 6. No real capture, Core ingestion, gear simulation or in-game test occurred.
Next: interface/API validation and a Core-approved ingestion contract. Earlier
November 15 status below is retained as historical context.

Rich natural conversation, banter and permitted awareness across exploration,
quests, collections, travel, grouping, economy and personal improvement.
Forever first; Retail second. Core remains the only brain.

## Completed

- Initial scope and FFXIV-to-WoW intent mapping recorded in the dated research.
- On 2026-11-13, discovered `E:\Program FIles\World of Warcraft`, containing
  Retail build `12.1.0.69299`; no Forever client in that inspected installation.
  This is historical evidence, not a new scan on November 15.
- Staged read-only AlfadorProbe, now under `Retail/addons/AlfadorProbe`.
- Desktop architecture boundary check passed on November 13. This did not
  execute or validate the Lua addon in game.
- On November 15, separated the WoW project from Desktop, preserved the research
  and ADR-0001, and established game-specific source folders and handoff files.

## Unverified / unimplemented

- Forever installation, exact build/interface, supported APIs and event behavior.
- All in-game probe behavior, including Retail.
- Own-player post-fight damage access and owned-pet attribution.
- Permitted low-latency delivery to Alfador, data-only import and Core ingestion.
- Queue/group actions, housing coverage and public API contracts by game.

## Next work

1. Locate or obtain the Forever client and establish its exact build/interface.
2. Review the existing probe against that client; add a Forever variant only when
   supported. Do not copy the Retail TOC and call it Forever-compatible.
3. Run isolated manual acceptance from the research notes. Record observed,
   restricted, absent and failed results with client identity and capture time.
4. Resolve permitted transport before promising live reactions. Keep manual
   snapshots distinct from live observations and preserve per-slot freshness.
5. Design any approved Core contract and Desktop adapter in their owning projects.

## Provenance

`docs/research/2026-11-13-capability-discovery.md` and Retail probe source were
migrated from `Alfador-Desktop/wow_addon`. The Desktop location retains a pointer
only after migration verification. No game installation or running app changed.

## In-game companion review (2026-11-18)

Installed path: `E:\Program FIles\World of Warcraft\_forever_`; executable
`1.60.1.70959`, flavor `wowf`, matching root `.build.info`. This is filesystem
evidence; no addon or API was tested in game and the interface remains unknown.

Alfador's existing server Core remains the brain. Portrait/bubble UI is a
candidate; live permitted observations to Core, inbound replies and custom voice
inside a native addon remain unverified. Hidden Desktop networking or voice does
not by itself provide a native addon connection. Next: in-game build/interface,
isolated local UI acceptance, then supported transport verification.

See the canonical parent review:
`../docs/research/2026-11-18-in-game-companion-review.md`.
