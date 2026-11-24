# Isolated SavedVariables write test for Forever71037

Source review only. Nothing installed or activated. Exact native target:
1.60.1/build71037/interface16001. Test has2 runtime files only. No chat logging,
network, character name/GUID, quest/zone/gear/combat payload or automatic reload.
A synthetic marker is held in a declared SavedVariable as fixed hex JSON. Only
manual /alfadorsavetest mark changes it. Lifecycle handlers do not overwrite the
last marker. The opaque label changes at reentry and is not character authority.

## What is already known from source

Canonical quest addon addons/Alfador-wow has no SavedVariables declaration and
accepts only70959. Its JSON panel is not a saved quest journal file. Local quest
JSON importer likewise accepts70959. On2026-11-20 a read-only SSH source check of
Core current/gaming_modules/wowf/capture.py confirmed its decode_request tuple
still requires1.60.1/70959/16001. No Core service/configuration changed. Owner
reports r98 deployed; this source check does not independently attest a release
label or endpoint enablement. Game badge71037 support does not widen import.

## Native procedure proposed for separate review

Stage only Alfador-wow-Save-Test.toc and SaveTest.lua in their own isolated
AddOns/Alfador-wow-Save-Test directory after exact pins/absent-target checks.
Keep production Alfador-wow unchanged. Preserve any pre-existing same-name saved
file; never overwrite/delete an unexpected test installation or saved evidence.
Game discovers/enables through normal owner-operated UI. No automated input.

1. Record actual GetBuildInfo if it changed. Owner starts in-world outside combat.
   Operator establishes which local WTF/.../SavedVariables/Alfador-wow-Save-Test.lua
   file the exact test writes. Keep account/path local. First baseline may be
   absent/empty; record unavailable instead of making up a timestamp.
2. Owner /alfadorsavetest mark. Record printed boundary,sequence,capture time.
   Operator checks the exact file with the bounded safe decoder immediately and
   after60seconds of ordinary in-world play. Record local read times, byte size,
   input hash and decoded original capture time. No zone/quest triggers assumed.
3. Owner manually /reload once. Inspect that same file and compare marker identity
   and original capture time. A changed disk mtime is not the capture time.
4. Owner marks again (new loaded-UI boundary). Repeat during-play observation,
   then a manual logout to character selection and inspect again. If needed,
   a separate normal-exit case can distinguish logout and process exit behavior.
   These are separate owner actions/cases; never initiate them automatically.
5. Report per-case unavailable/old/new marker, exact timing/build and unexpected
   behavior. A file that changes only on reload/logout supports saved snapshots,
   not live delivery. Do not use crash/forced termination as a save test.

Decoder, from canonical project root (read only, no Lua execution/network):
py -3.12 -B Forever/tools/save_test_validate.py <exact-local-test-SavedVariables-file>
It accepts only a single fixed variable assignment containing bounded hex JSON,
rejects extra Lua/code/keys/duplicates, and emits sanitized metadata. A different
serializer format is unavailable pending source review, never executed as Lua.
The decoder is a developer evidence reader, not Desktop's production watcher or
Core historical import. Synthetic markers must never be submitted as quest data.

Rollback: disable/unload test via normal UI; verify exact2 runtime names, hashes
and absolute target, remove only those files and empty folder. Preserve the
client-written test saved file locally as evidence; no raw paths/account names
or source files need forwarding. Existing chat logging state is untouched.

## What comes after evidence

Addon: prepare separately reviewed journal SavedVariables capture for71037; verify
quest API behavior on that exact build and preserve original sample times.
Desktop: bounded file watch, stable file read, safe data-only decode/JSON schema,
private local path, original capture time, actor/account boundary, duplicate/order
handling, existing explicit sharing and connection authority. No silent reconnect,
new permissions or assistant-policy logic. No reading game process memory.
Core: reviewed exact-build historical import compatibility plus positive71037 and
wrong-build rejection tests; preserve70959 compatibility, historical semantics,
withdrawal/actor replacement/expiry and normal text/voice delivery. Badge support
is insufficient evidence. Core remains the sole authority under gaming_modules/wowf.
A successful synthetic save test proves persistence behavior, not quest API accuracy
or permission/eligibility/live game identity. No server deployment requested.
