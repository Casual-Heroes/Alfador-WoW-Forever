# Forever data foundation

Later owner revision November 18: this broad milestone is deferred. Active work
is [current-zone leveling](LEVELING-PILOT.md), multiple eligible quests and a
twenty-minute question. Keep this document as future context, not current scope.

Started 2026-11-18. Owner-requested scope, not implemented Core functionality.
Installed executable: 1.60.1.70959. In-game interface and data acceptance pending.
Core remains the only brain under ADR-0001. Avatar work is deferred.

Initial character scope confirmed by owner: Druid and Paladin; PvE tanking and
DPS. PvP and healing optimization are deferred. Do not assume specific talent
trees or role eligibility from class alone; establish Forever's selected talents
and verified abilities. Keep tank and DPS comparisons as separate scenarios.
For Druid, distinguish damage playstyles/forms when supported by the observed
build. Record content type, target level, mitigation/survival requirements and
damage objective; do not reduce tank advice to a single damage score. User role
preferences are scenario inputs, never observations of equipped gear/talents.

## First five capabilities

| Capability | Input | Core output |
| --- | --- | --- |
| World and zone knowledge | Forever zone identity, curated sources; optional observed quest IDs/progress | Zone story, factions/conflicts, why quest chains matter, important unlocks/locations and relevant activities; spoilers default to minimal |
| Character and talents | Verified character identity, level/class, observed selected talent IDs/ranks/configuration | Explain the actual build, key interactions and gaps; label alternative builds as plans |
| Equipped gear | Same-character per-slot item instances and observation time | Explain what is equipped and what remains unknown |
| Gear versus talents | Equipped item stats/effects plus observed talent ranks and versioned mechanics | Explain which bonuses help selected abilities and where gear does not support the intended role |
| Equipment calculations | Baseline loadout, candidate item instances, goal, constraints and validated rules | Compare legal complete loadouts; explain tradeoffs and assumptions; recommend the best evaluated option within stated coverage |

## Two separate input streams

World knowledge is sourced content, not a character observation. Store game,
locale, zone/quest/item/spell IDs, source URL, source build/revision, retrieved
time, coverage and license/terms review. Lore interpretation must link back to
supporting material. Preserve differences from Retail/Classic and distinguish
source-backed facts from interpretation. Do not import whole copyrighted guides.
Never infer quest completion from lore, level or possession of a reward.

Character state is a dated observation. Preserve game, region and a verified
opaque character identity; do not require a Retail realm model for Forever.
Record original capture/source-update time separately from retrieval/receipt
time. A recently fetched profile may still describe an earlier logout. Imported
snapshots and public profiles are historical until their observation freshness
is established. Importing or fetching again does not renew capture time.

Missing fields have explicit unavailable/partial/restricted states. Plans,
website edits and calculated loadouts cannot overwrite observed gear or talents.
Talent and equipment observations from different captures cannot silently become
one coherent current build. Bind a recommendation to exact input revisions.

## Observation contract proposal

`contracts/character-context.schema.json` is a LOCAL draft for bounded JSON
snapshots, not an approved Core event or transport. No executable Lua import.
The first report covers identity, build, zone, character summary, talents and
per-slot equipment. A producer must validate safe values before serialization;
schema validation cannot establish authenticity, permission or runtime secrecy.

For each datum, retain status, evidence revision, capture time and source. An
equipment instance needs its full item link/bonus/modifier context when available;
item ID alone cannot establish rolls, enchants, sockets, upgrades or set effects.
The initial contract intentionally allows incomplete sections and refuses to
represent an incomplete loadout as complete. IDs must be confirmed against the
Forever data revision before resolving them to names or mechanics.

Authentication and account-to-character binding belong to the Core integration.
No client-supplied ID grants account authority. Do not put API secrets in the
addon. Validate byte/count limits before parsing and before forwarding. Draft
transport ceiling: 256 KiB UTF-8, no network activation in this project yet.

## Equipment evaluation in Core

1. Establish the objective: leveling/solo, dungeon damage, raid damage, tanking,
   healing or PvP; include character level, encounter assumptions and preferences.
   Role is not established merely by where most talent points were spent.
2. Verify the baseline's talent and gear revisions, game/build and character.
   If partial, explain known stat changes but withhold a complete best-loadout
   claim. Current selected talents and a proposed respec are separate scenarios.
3. Resolve exact item instances and applicable restrictions: class, level,
   proficiency, unique-equipped rules, weapon pairing and set membership. Separate
   equipped, owned, obtainable and hypothetical candidates. Ownership is not equip.
4. Compute deterministic deltas only for implemented, version-tested mechanics.
   Account for diminishing returns/caps where verified, talent scaling, weapon
   effects, set thresholds, enchants, sockets and on-use/proc behavior. Unsupported
   mechanics remain unknown; do not invent a damage or healing contribution.
5. Evaluate loadouts together where items interact. Choosing the highest-scoring
   item independently in every slot can miss set or weapon-pair interactions.
   A weighted-stat score is an explicitly labeled approximation, not proof of DPS.
6. Return the best evaluated legal candidate under the specified goal and search
   coverage, with alternatives, tradeoffs, data/model revision and confidence.
   Without a validated Forever simulation/model, do not claim simulated DPS or
   universal best-in-slot. Recompute after relevant talent/gear/rules changes.

No gameplay execution, automatic equipping or analysis of other players' damage
is included. Core may explain and recommend; the player makes game actions.

## Source discovery: November 18

- Blizzard [Forever overview](https://worldofwarcraft.blizzard.com/en-us/forever/)
  and [launch article](https://news.blizzard.com/en-us/article/24315820/world-of-warcraft-forever-now-live):
  authoritative narrative starting points; not a complete zone/quest database.
- Blizzard developer documentation entry points for game-data/profile APIs
  redirected or failed in this browsing session. No authenticated API response,
  credentials, endpoint contract or Forever coverage was validated.
- [First-hand community API investigation](https://us.forums.blizzard.com/en/blizzard/t/wow-forever-api-what-works-so-far-plus-a-ts-client/60334)
  reports Forever namespaces, profile/equipment/specialization routes and distinct
  character identity. This is the author's experiment, not Blizzard documentation
  or our acceptance evidence. It motivates checking a server-side profile path,
  which could supply historical snapshots independently of addon live transport.
- [TheWoWDB developer documentation](https://thewowdb.com/developers/) advertises
  versioned JSON for items, spells, quests and zones. Its displayed Forever build
  was 1.60.1.70532, older than installed 70959. Candidate only: permissions,
  freshness, completeness and endpoint behavior are not accepted.
- [ForeverDB developer page](https://foreverdb.net/developers) appeared in search
  but timed out on direct open. Search snippets are not an accepted API contract.

## Delivery order and acceptance

1. Confirm in-game interface and supported APIs; establish one deliberate test
   character. Prepare a safe local Forever snapshot collector only after that.
2. Validate the JSON proposal locally, then agree the authenticated ingestion
   contract with Core in its owning project. Either an authorized API profile
   or user-mediated report is a candidate; distinguish both from a live feed.
3. Demonstrate one real character/talent/equipment snapshot accepted by Core and
   returned in a receipt bound to the same revision. Confirm observed values
   against the game UI. No fabricated fixture counts as this acceptance.
4. Add sourced zone/quest context; test a zone and quest chain end to end before
   claiming all-zone coverage. Confirm current-zone provenance and spoiler handling.
5. Add mechanical item deltas and talent-aware explanation; test missing slots,
   stale/mismatched characters/builds, modified item variants and a set threshold.
6. Enable rankings only as the mechanics model is validated. Test objective
   changes, incompatible items, unsupported procs and conditional recommendations.

Core implementation, live transport, full world coverage, validated mechanics and
in-game acceptance are outstanding. No service or game installation was changed.
