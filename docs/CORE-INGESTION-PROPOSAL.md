# Core ingestion proposal: first Forever snapshot

Later November 18 scope revision: the next server target is a current-zone quest
read under a verified WoW-only session; see LEVELING-PILOT.md. This broad
character/talent/equipment proposal is deferred background.

Prepared 2026-11-18 for review in the owning Core/Desktop projects. Local proposal
only: not delivered, registered, approved or implemented on a server. This file
does not request service installation/restart or worker privilege changes.

## Current implementation

- Draft `contracts/character-context.schema.json` defines historical JSON input.
- `tools/observation_import.py` implements bounded offline import and selected
  semantic checks; 29 synthetic tests pass. Authentication is not established.
- No addon manifest/exporter is installed. Forever interface/API acceptance is
  pending. No game data has been captured in this phase.
- Desktop's `src/core-client.ts` and `src/ffxiv-remote-observations.ts` demonstrate
  authorization, capability advertisement and expiring game-specific sharing.
  Inspection found no WoW-specific ingestion implementation there. FFXIV schemas
  and transport cannot be repurposed to claim WoW support.

## Required owning-Core decisions

1. Advertise a distinct versioned WoW observation capability. Supply exact event
   schemas and transport byte limits; do not presume the local 256 KiB ceiling
   matches the server. The adapter must send nothing when support is absent.
2. Bind authenticated account/device permission and explicit sharing state to
   permitted Forever character identity, independently of client-supplied fields.
   Do not infer a Retail realm-based identity or authority from profile lookup.
3. Reject plans and incompatible game/character/build inputs, conflicting slot
   or talent observations, unsupported fields, replayed revisions and invalid
   timestamps. Bind receipt IDs to the exact accepted content hash and revision.
4. Distinguish a historical imported report, a historical API profile and any
   future separately approved live source. Never infer current equipment from
   a partial or old report. Preserve prior observations as history rather than
   filling gaps with suggested equipment or saved builds.
5. Return explicit accepted/rejected/duplicate results; define duplicate hash
   behavior, reconnect/replay policy, source expiry and permission revocation.
   Existing assistant dialogue and voice do not become transport for raw reports.
6. Keep talent/gear mechanics, scenario preferences, lore interpretation and
   advice in Core. Initial scenarios: Druid/Paladin, PvE tanking and DPS; other
   roles are deferred. Item/talent IDs need game/build-matched knowledge.

## End-to-end acceptance still required

Capture one deliberate player's safe out-of-combat zone, character summary,
talents and equipment; visually compare against the Forever UI and retain exact
build/interface and capture time. Export explicit JSON via user action. Validate
locally, share only via an approved authenticated adapter, obtain a Core receipt
bound to the same revision/hash, and verify Core describes known versus unknown
slots and selected talents correctly. Negative acceptance includes no permission,
unsupported capability, replay, cross-game/character input and incomplete gear.

No passing local test or prepared proposal counts as this end-to-end acceptance.
