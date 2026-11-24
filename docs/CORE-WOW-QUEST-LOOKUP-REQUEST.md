# Request: Forever-only quest lookup and historical observation intake

Date: 2026-11-18. Sender: Alfador-wow development workspace.
Intended recipients: Alfador Core maintainer (Server B) and QuestLog research
broker maintainer (Server A). Action: implement/review a narrow source candidate
and return exact versioned contracts/tests. This is NOT an install, activation,
restart, permission migration or request to change existing research sessions.
Owner explicitly authorized sending this request on November 18. Delivery is
tracked in a separate receipt; this document does not itself prove receipt.

## Mandatory Core source layout (owner instruction)

Each game has its OWN folder under `alphador_core/gaming_modules/`:

```text
alphador_core/gaming_modules/
  ffxiv/
  wowf/
```

Implement Forever observations, names/quest resolution, XP evidence, leveling
comparison and game-specific adapters in `wowf/`, with its own runbook and tests.
Do not place WoW code in FFXIV or scatter it through generic game files. Keep
shared routing, session verification, authorization, tool admission, dialogue and
delivery in Core's shared infrastructure. This is separation by game, not a
second brain or duplicated authorization. Retail requires its own game module
when introduced; no inferred compatibility or shared private state.
Return the exact module source map with the candidate. Do not move or modify
FFXIV/Reforged functionality as part of this scoped request.

## Concrete prerequisite finding

Read-only inspection through the existing host-key-verified `alfador` SSH alias
found current Core release `20261118-r91-speech-name-reliability-candidate01`.
`contracts/ai-research-v1/research-operation-matrix.json` SHA-256:
`d659ab5d26597fc0dcba643f7e0d137196d5344f2fc69e8e300b0e40de2f59cb`.
Enabled targets were crimson_desert, elden_ring and err; no WoW matrix entry.
The inspected ai_research.py, public_research.py and questlog_gateway.py had no
WoW/Warcraft reference. This is source/contract evidence, not a verified product
session or proof of the broker's present runtime. No token, secret, grant,
environment or live session was accessed/changed; no real quest lookup attempted.

## Owner's narrow acceptance target

Totem Ale (owner-described Paladin) plays Forever. User-supplied reports identify
UnitName Totem, level 3 then 4, Dun Morogh player map 1426, build 1.60.1/70959,
interface 16001. Multiple current-zone quest candidates, bounded to 50, inform:
“I've got twenty minutes. What should I do next to level?” Lore/gear/talents and
avatar work are deferred. Private raw GUID/captures remain local, not attached.
IDs 170/182/183/233 occurred in the pilot; their names, chains, minimum levels and
XP have not been independently verified. IsOnMap does not prove exact membership.

## Existing local source candidate

- `addons/Alfador-wow`: manual, local JSON capture only; no network or tokens.
- Draft1 raw snapshots preserve unavailable XP/times. New draft2 adds at most one
  reward-XP observation bound to the selected quest, capture time, player level
  and claimed identity, with before/after selection checks. It calls Blizzard UI's
  no-argument GetQuestLogRewardXP; no client quest selection or gameplay action.
- `contracts/quest-pilot-capture-v2.schema.json` and `tools/quest_capture_import.py`
  enforce structure/context but never establish authenticated observation truth.
- `core_candidate/quest_pilot.py` and `access_demo.py` are synthetic offline
  references, not deployed policy. Do not copy the fake session registry into
  production or accept a source/provenance string as authentication.

## Requested server contract

1. Use existing authenticated AI connection/session approval and introspection;
   define an explicit Forever-only read operation and game identifier. Return the
   exact capability advertisement, request, response, receipt, revoke/expiry and
   audit schemas. An unsupported capability must produce a safe unavailable state
   before any downstream call. Do not silently widen existing scopes or accounts.
2. Quest-read inputs are bounded IDs and a validated game/build/locale context,
   not arbitrary URLs, tools, query languages, downstream credentials or model
   instructions. Verify candidate/zone membership on the server; a request's map
   cannot expand scope. A new current-zone observation requires validated rebinding.
3. Separate public quest records from private character authority. A user-approved
   session grants only the requested data read; it does not authenticate a pasted
   GUID, make an API profile live, or authorize private account data. Define the
   accepted observation trust level and do not relabel claimed identity as verified.
4. Resolve Forever-specific quest identity, level requirements, prerequisites,
   zone/source/build revision and reward XP. XP must be qualified by player level,
   ruleset and source, with scaling/bonus assumptions explicit. Missing data stays
   unknown; no Retail/Classic substitution. An observed UI amount needs independent
   acceptance before it is treated as verified resolver evidence.
5. Historical report intake must retain original capture time/revision/hash and
   explicit opt-in. Return a receipt bound to the exact content. Accepting an old
   report does not renew it. No raw JSON-as-dialogue workaround or another game's
   observation event. Draft contracts are proposals, not an instruction to accept.
6. Authorize immediately before downstream work and re-check revocation/expiry
   before delivery. Keep upstream credentials exclusively on the server. Log a
   correlation ID, verified actor, scoped operation, source revision, decision,
   whether downstream began and whether data was delivered, without raw tokens,
   quest text, credentials or private character payloads.

## Required source tests and later real acceptance

Source tests: verified scoped session succeeds; forged/expired/revoked session,
other game, writes, other zone/quest scope and malicious quest-text instructions
stop correctly; forbidden calls do not reach downstream; in-flight revocation
withholds delivery; duplicate/stale/cross-character reports cannot become current.
Existing dialogue/voice/session-renewal invariants and release checks still apply.

Return full reviewable candidate identity, exact contracts, tests, limitations,
setup/preflight and rollback without installing. Then obtain a real owner-approved
WoW-only product session, perform one authorized quest lookup and the actual
revocation test, and retain correlated sanitized audits/receipts. SSH access,
source tests and fake sessions do not satisfy this acceptance. Do not create a
grant, end an existing owner session or promote/restart services from this request.

Expected replies: Core publishes `CORE-WOWF-QUEST-LOOKUP-20261118-RESPONSE01.md`
and matching machine-readable evidence; Server A publishes
`SERVER-A-WOWF-QUEST-LOOKUP-20261118-RESPONSE01.md` and exact broker contracts.
Use each recipient's existing `/home/<service-owner>/ServerHandoffs/outbox`
route to MYTHIC, explicitly addressed to the WoW developer. Completion means
verified delivery of a reviewable candidate/contract or a precise missing-input
request, not an unreviewed rollout or a fabricated live result.
