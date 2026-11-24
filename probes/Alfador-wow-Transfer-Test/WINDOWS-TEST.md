# Source04 isolated Windows self-whisper test - 2026-11-20

Owner requested proceeding with the revised bounded marker test. This supersedes
Source03 for a new isolated run, not its immutable evidence. No production addon,
Desktop installation, Core restart, game-data upload or game input automation.
The previous test files were removed and native logging restored OFF.

## Change and evidence

Exact client target: Forever 1.60.1/build71037/interface16001. Source04 records
AreOutgoingAddonChatMessagesRestricted as a diagnostic boolean. Missing/error/
secret/nonboolean results still stop. A true result is reported, not falsified.
The native logged self-WHISPER call determines its own result; any non-success
stops without retry or another destination. InChatMessagingLockdown, combat,
world, player, logging, prefix, clock and build checks remain. New outside-instance
requirement excludes dungeons, battlegrounds and arenas from this experiment.
This is an observation of documented native behavior, not evidence of approval
for a production external stream. No restricted gameplay information is collected.

Primary comparison: Campkeeper author reports build70334 worked despite true flag:
https://www.curseforge.com/wow/addons/campkeeper/files/9129067
Generated API docs at pinned commit3d8abb1da73acd38e412e24fb3f99454a6392346:
https://raw.githubusercontent.com/Gethe/wow-ui-source/3d8abb1da73acd38e412e24fb3f99454a6392346/Interface/AddOns/Blizzard_APIDocumentationGenerated/ChatInfoDocumentation.lua
Older-build author observations do not establish behavior on71037. Generated
docs describe the getter broadly; the discrepancy is what the native test measures.

## Exact two-file staging

Stage only these files to Interface/AddOns/Alfador-wow-Transfer-Test under the
locally verified _forever_ installation. Abort if that target already exists,
is linked, or unexpected contents appear. Do not replace Alfador-wow production.

- Alfador-wow-Transfer-Test.toc: `2d34af846a9f088905b7cd69e9e85cdd9a5966be73b59f437e3ae361af661ea4`
- TransferTest.lua: `9ef13b64be8b03d90491420fcf00681b2b41fff4d13da051e3639c601bc8c9ea`

## Owner and reader handshake

1. Load/enable only the isolated Transfer Test through normal game UI; restart
   if required to discover a new addon. Confirm build if the game has updated.
2. Outside instances and combat, note prior logging state. Original state was
   OFF after the preceding run; verify it has not changed. Manually use /chatlog
   only if needed to enable it. Native logging can record unrelated chat locally.
3. Run /alfadortransfertest prepare. It reports restriction_flag, then PREPARED
   session=<32hex>. No markers are sent by prepare. Provide label and prior logging
   state to the operator. Do not run start yet.
4. Operator opens reviewed tools/transfer_marker_tail.py with Python3.12:
   py -3.12 -B tools/transfer_marker_tail.py --forever-root <local-root> --session <label> --seconds 45
   Reader starts at EOF, prints ready and ignores unrelated chat. Paths stay local.
5. Only after operator announces READY, manually run /alfadortransfertest start.
   At most eight harmless markers, one every three seconds, target self WHISPER.
   SEND is only a native API success acknowledgement; no matching echo is tracked
   by this version, and success does not establish disk or Desktop delivery.
6. Keep playing safely without reload/logout/save during the 45-second window.
   Stop if the game shows a denial/error. Send failures stop automatically, but
   asynchronous game notices must also be reported. No alternative target/channel.
   Reader closes by deadline; no reconnect or Core forwarding.

## Interpretation and rollback

All eight receipts during play are useful feasibility evidence, not authenticated
current-zone data or product acceptance. Missing/late records do not prove a ban.
Game/Windows wall-clock differences are not latency: use a local common-clock
stopwatch/recording for latency claims, otherwise report arrival timing relative
only to reader ready. Reader polls every0.25s. Raw chat/recordings remain local.
Keep exact sanitized ready/marker/summary records and native error observations.

After the run, manually /alfadortransfertest stop. Restore the prior logging state
manually, then disable/unload via normal game UI. Operator verifies absolute target,
exactly these two files and both pins, removes only those files and then the empty
folder. Never delete or transmit native logs. Unexpected changes stop cleanup for
review. Source03 is not reinstalled. No Desktop/Core changes are made.

## Verification

53 synthetic checks pass in Lua5.1/5.4 and local Python reader, including true-flag
native success/denial, lockdown transitions, instance transitions, secret/missing
APIs, self-only routing, eight-attempt ceiling, ready/start and EOF delivery.
The matching local Lupa dependency is Python3.12. Synthetic acceptance does not
prove native delivery. Source03 reader bytes remain unchanged.
