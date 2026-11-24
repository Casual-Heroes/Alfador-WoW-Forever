# Logged-addon native chat-file transport retired - 2026-11-20

Decision: stop testing SendAddonMessageLogged as a native WoWChatLog.txt live
transport. Owner supplied Core's recommendation; source review supports stopping.
No new installation, activation, logging toggle or native test is proposed.

## Verified source meaning

Blizzard community-manager posts (May30 and June12,2018), preserved by BlueTracker,
introduce the then-named SendLoggedAddonMessage for reporting addon communication
abuse and announce CHAT_MSG_ADDON_LOGGED. This is historical author documentation,
not exact Forever71037 acceptance or a promise of local file output:
https://www.bluetracker.gg/wow/topic/us-en/20762318007-battle-for-azeroth-addon-changes/#45

Pinned generated ChatInfoDocumentation.lua names today's SendAddonMessageLogged,
describes plain-text client-to-client messaging with logging/throttling, and
provides CHAT_MSG_ADDON_LOGGED. It does not guarantee output to WoWChatLog.txt.
Function name, native success and an in-game receive event do not establish an
external Windows feed. The probe did not verify a matching receive event.
https://raw.githubusercontent.com/Gethe/wow-ui-source/3d8abb1da73acd38e412e24fb3f99454a6392346/Interface/AddOns/Blizzard_APIDocumentationGenerated/ChatInfoDocumentation.lua

## Actual Forever result and cleanup

Build71037: owner confirms all8 native success acknowledgements during the local
READY countdown. Reader45.016s,0/8 receipts, no terminal error; local file0bytes
at end. No per-marker common-clock recording reviewed and no latency claim.
Evidence: Forever/handoffs/wowf-native-transfer-20261120-result03/.
The isolated test folder is confirmed absent. Logging OFF/window closure for this
latest run still require owner confirmation; the prior run's cleanup is distinct.
Raw logs were not exported or deleted. No Core restart, Desktop install or
production addon update occurred.

## Scope of retirement

Retire this experiment's local-chat-file transport hypothesis, not addon
client-to-client messaging generally. Preserve immutable source packets and
sanitized evidence. Do not restart identical tests, change chat destinations or
turn ordinary chat into a telemetry stream. Future live proposals need supported
source/policy/build evidence and a reviewed transport before a native run.
Historical snapshot import and public catalog work retain their existing source,
authority and freshness limits. SavedVariables are not a continuous live feed.
