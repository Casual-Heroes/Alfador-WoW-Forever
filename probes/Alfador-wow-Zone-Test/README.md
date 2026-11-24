# Alfador-wow zone test - isolated source review

Date:2026-11-20. Expected Forever client1.60.1 / build70959 / interface16001.
This is not the canonical installed addon and is not an installer. No installation,
activation, feature change or production restart was requested or performed.
Actual in-game samples and bounded-delay Desktop delivery are NOT established.
Only the Lua source tests below were executed. Do not relabel mock examples as game
acceptance. Original addon0.0.6 and installed Core/Desktop remain unchanged.

## Observation contract

Proposed producer schema:alfador.wowf.zone-probe.sample.draft1, within the fixed
alfador.wowf.zone-probe.evidence.draft1 evidence envelope. The closed schema is
contracts/zone-probe-sample.draft1.schema.json. Not a registered Core/HTTP event.

World presence requires a prior PLAYER_ENTERING_WORLD event plus explicit true
IsLoggedIn() and UnitExists('player') checks. It does not infer world presence from
an executable badge. Startup waits for that event; loading/unavailable states
publish no old map/name/level. PLAYER_LEAVING_WORLD/PLAYER_LOGOUT immediately
invalidate. ZONE_CHANGED, ZONE_CHANGED_INDOORS and ZONE_CHANGED_NEW_AREA invalidate
before a later fresh sample. Loss of the player requires a new entering-world
boundary before resuming. These lifecycle events require actual client acceptance.

Each locally generated record has an increasing sequence within this Lua lifetime
and a32hex random boundary label. Entering world rotates the boundary; reload
resets Lua sequence. The label is not a GUID, persistent character ID, secure token,
proof of identity or globally guaranteed unique across reloads. Desktop/Core must
bind any reviewed future transport to their verified actor/device and explicitly
established context; do not silently reconnect/rebind to accept a reset sequence.
No UnitGUID(), UnitName(), account, realm, raw file path or token is collected.

GetBuildInfo() is checked against1.60.1/70959/16001 and sanitized actual values are
reported separately from expected values. A different/missing/restricted build
stays unavailable; expected metadata is never a claim of actual in-game acceptance.

Fields sampled in one sequential, non-atomic guarded window:
GetServerTime(start), IsLoggedIn, UnitExists(player), C_Map.GetBestMapForUnit(player),
GetZoneText, optional UnitLevel(player), then map/name/login/unit/safety/time checks
again. Map/name must match before/after, start/end times must be observed and within
0..1 seconds, and character/world gates must hold. Optional level is sampled once
inside that window, not separately attested. Timestamp is original server Unix
seconds, not disk-read/upload time. It is client-reported, not trusted wall-clock
attestation. Every unavailable sample clears every field value. No atomicity claim.

Available facts: UI-map ID, zone text, inWorld derived true signal, optional level.
Coarse position is intentionally absent pending the separately reviewed API and
coordinate contract. Level beyond1..60, map<=0, missing/restricted/error/unstable
reads, missing clock, combat or unknown safety all stay unavailable. Secret checks
are honored; there is no alternate read to reconstruct restricted state.

Local polling is at most1Hz, without catch-up loops, to bound probe overhead. Event
invalidations are immediate locally. The last12 sanitized samples are retained.
This is a sampling cadence, not a proven delivery latency or performance benchmark.

## Evidence views and persistence

After a separately authorized actual-client test deployment, the owner can use
/alfadorzonetest to view/copy the frozen last12 sample records. The command only
opens a local evidence box; it never uploads or triggers gameplay. It does not
force a sample or update the frozen box while copying. All samples are untrusted
local evidence, not a live Core feed.

The probe also assigns only a hex-encoded bounded JSON string to the single
SavedVariables field AlfadorZoneTestEvidence. A client-written save may preserve
the terminal logout/unavailable marker. Normal SavedVariables persistence is a
historical transport, not an in-world live pipe. Actual write/load/flush behavior
on70959 and the full lifecycle still need measurement. No external app executes
or imports the SavedVariables as Lua. Fixed developer decoder accepts only one
whole-file assignment to that exact field with a quoted hex string; additional
Lua, escaped strings, other fields, malformed data and oversize files fail closed.
No product watcher or arbitrary file/HTTP/command importer is implemented.

Developer validation commands, from the extracted Forever source root:
python -B tests/test_zone_probe.py -q
python -B tools/zone_probe_validate.py <local-JSON-evidence-file>
python -B tools/zone_probe_validate.py <local-fixed-saved-file> --saved-hex
Keep actual paths local. Validator emits content-free historical receipt, never a
live delivery claim. JSON ceiling64KiB, saved text ceiling140000 bytes,12 samples,
32hex boundary, closed fields and sequence checks. It never executes captured Lua.

38 Lua5.1/5.4 mock checks pass (19 scenarios per runtime), covering stable reads,
transition/startup/player loss/logout, unavailable/restricted/build mismatch,
sample consistency, clock regression, rate/retention, copy freezing, decode safety,
reset boundaries and invalid fields/sequences. Every mocked sample is validated
against the closed contract. Examples are SYNTHETIC-NOT-GAME only, not raw captures.
API reference: generated Blizzard Map documentation mirrored by Gethe, separately
pinned in API-SOURCE-REFERENCE.json; it documents nullable GetBestMapForUnit and
player/party applicability. A mirrored branch/commit is not exact70959 evidence.
Other API presence/secret/event behavior remains a probe hypothesis until native
acceptance; GetZoneText/map/level historical captures are prior user evidence only.

## Native-client evidence still required

Do not install this source packet as part of the handoff. For an approved isolated
actual-client test, the owner/test operator must obtain three sanitized producer
cases: in-world stable zone; transition invalidation then new zone read; character
unavailable/terminal logout marker. Also verify exact GetBuildInfo output, interface,
reload/reset and denied/unavailable APIs. Do not collect GUIDs or raw account paths.
Return normalized summaries and fixed-field samples only; private raw evidence
stays local. Tests must distinguish world transition from a successful fresh read.

Desktop jointly reviews transport: demonstrate actual observations arriving while
the game runs, source/destination clocks, maximum delay, drop/duplicate/reorder,
logout/zoning/disconnect/sharing-off/character changes. File flush/read timestamps
cannot prove current state. This probe demonstrates NO bounded live connection.
Until a permitted bounded live transport is demonstrated, Core must answer from
historical time-qualified snapshots or say current zone unknown. Do not improvise
screen/pixel/clipboard side channels, process-memory reads or protected-state export.

Core owns the eventual actor-bound expiring reader and natural zone-question
admission, plus independent public catalog/private snapshot authority through text
and audio. Treat boundary as client data only, honor sharing/cancellation, expire
without fresh readings and clear on identity/lifecycle changes. Preserve game
identity, public descriptions, quest answers, FFXIV and voice regressions.

Server A's later coordinate/eligibility/mob spawn/XP/drop/lore evidence is independent.
Player telemetry does not prove grinding rankings. Public catalog remains available
with sharing off. Source-only probe/test handoff; no rollout permission is implied.
