# Native transfer interpretation correction - 2026-11-20

Supersedes the transport-blocked interpretation in WOWF-NATIVE-TRANSFER-20261120-RESULT01, not its recorded observations or rollback.

## What actually happened

On owner-observed Forever 1.60.1/build 71037/interface 16001, the getter existed and returned true. Source03's local eligibility gate rejected prepare. No SendAddonMessageLogged call, self-whisper, reader run or transport-latency measurement occurred. A local preflight rejection is not evidence of a native WHISPER rejection. Earlier statements calling this route unavailable were too strong.

## Primary source comparison

Campkeeper author's v0.2.1-forever changelog reports build 70334 tests on 2026-10-10: the getter remained true despite working guild/channel messages and a self-whisper. This is older-build developer evidence, not acceptance on 71037, a policy authorization, or proof of live disk flushing.
https://www.curseforge.com/wow/addons/campkeeper/files/9129067

Consequently, neither blanket message prohibition nor universal CHANNEL-only semantics are established. The getter has no channel argument. Specific destinations, API variants, realm/session rules and builds require separate evidence. The owner's proposed battleground prohibition and anti-cheating explanation remain unverified here.

## Next source review

Review a destination-specific, bounded native test of the same logged SELF-WHISPER API. Keep the getter result as an explicit diagnostic; do not falsify it or claim it proves permission. Review applicable client/policy documentation before changing the runtime gate. Keep chat/combat/world/build guards, fixed self target, eight-marker ceiling, manual logging and reader-ready handshake. Native return status, matching self echo, and timely local log receipt are separate outcomes. No alternate channels, other-player targets, gameplay payloads or bypasses are proposed.

Current outcome: live transport UNTESTED, not demonstrated unavailable. SavedVariables remain historical. Runtime files remain removed and logging restored OFF. No code change, installation, new native attempt, Desktop install or Core restart is authorized by this clarification. A concrete revised artifact needs review and approval before staging.
