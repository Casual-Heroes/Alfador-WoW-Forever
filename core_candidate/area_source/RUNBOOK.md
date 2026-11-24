# Forever area guidance source candidate 01

Governing dialogue design: `Forever/docs/CONVERSATION-DESIGN.md` (project-root
relative). Core owns semantic admission and follow-ups; no required game/zone
phrase or client trigger routing. User-stated area is public retrieval context,
not observed location. Private/public evidence guards stay independent. Nine design
acceptance cases are recorded, not yet executed as runtime semantic tests.

2026-11-19. Owner explicitly resumed public quest data, nearby/unaccepted quests,
distance and lore. Core remains sole brain; this is a source-only module overlay,
not a release or live API. Do not replace shared Core/r92 files with older copies.

## Built

`alphador_core/gaming_modules/wowf/area_guidance.py` implements a pinned offline
catalog reader and bounded paginated current-map queries. It has no network,
authentication, model, voice or gameplay surface. Caller must use existing Core
actor/observation policy and exact source release; this is not an admission route.
Query filtering works with any map supplied in a compatible reference pack.

The first pack is partial Dun Morogh: 93 quests, 83 with bounded pickup/turn-in
points, including The Stolen Journal and The Boar Hunter. It is normalized from
Forever Database's index, zone mapping and21 quest shards. Raw snapshots and all
24 fetch pins accompany the review ZIP. Compiler is offline, verifies each pin,
and byte-reproduces the normalized pack SHA256. Keep attribution and upstream
license with redistributed data. A code-commit pin does not pin mutable hosted data.

All records are ambiguous for exact70959. Missing journal membership never proves
availability; supplied completion filters require Core-validated same-character
observations. Faction/class/race/chain conditions are source data, not an eligibility
engine. Minimum-level hints do not make an unaccepted quest available. Source XP
is separate from observed/effective character reward XP.

Lore excerpts and chain membership are untrusted source context. Every story
importance label is unreviewed; chain size is not lore importance or canon order.
Core may explain qualified source context after guarded integration, but a sourced
importance/rationale layer is still required for 'which quests matter most?'.

Coordinates are percentages in area-ID map space. Calculate a straight-line
percentage-point distance only when input and source coordinates share that exact
space. C_Map UI-map fractions are not interchangeable without verified conversion.
No position is fabricated if the addon has not captured one. At most32 source
pickup/turn-in points per record are retained; distance is only to those points.
No objective path, meters, travel ETA, transports or best/XP-per-minute route.

## Contracts and tests

Proposed closed shapes: contracts/area-guidance-source-v1/area-query.schema.json
and area-context.schema.json. These describe internal source integration, not a
registered HTTP endpoint or operation. The kwargs API allows omitted optional
values; a serialized query expands the documented defaults. Pin pagination to the
same source digest. Max50 results/page, up to5000 source records. Full coverage is
not inferred; truncation/next_offset are explicit.

16 focused tests pass; both schemas checked by Draft202012Validator and3 real
query/result cases validate. Tests cover pin mutation, area changes, every page,
wrong game/build, coordinates, unknown eligibility, inert story text and malformed
input. Offline compiler reproduces pack digest96456ccfa09bb6a6fce66eb101f49a21e2c58dd864f18a3810b2861e94f64116.

From extracted Forever root: python -B tests/test_area_guidance.py -q.
Reproduce: python -B tools/build_area_reference.py source_snapshot new-output.json.
No installed Core, Server A, Desktop or addon change was made. Core's live r92
historical import/reply behavior is separate; Windows manual acceptance is pending.

## Team ownership and remaining build

Server A: resume optional Forever data source work under existing fixed broker
transport/auth. Review this pack, fix existing runtime source-pin/result-schema gaps,
and propose a reviewed audit migration/registration candidate. Define build-qualified
unknowns/eligibility, area query pagination, source/release authority and denial/
revocation tests. Expand source packs by observed map rather than fixed player zone.
Supply source-backed story importance, rationale, questline/spoiler references;
never label important from chain length alone. Return exact machine contracts and
source candidate, not activation. Preserve original source pins/license attribution.

Core: integrate this pure source adapter into wowf on CURRENT matched source, bind
private overlays to actor/snapshot and newly reviewed public results to source
release. Distinguish public catalog candidates from observed journal and verified
availability. Guard text/audio against sharing-off/replacement/revocation. Propose
closed position/progress input contract before addon changes; draft4 has no player
position/class/faction/prerequisite completion coverage. Distance needs verified
same-space map transform or a supported navigation interface. No model/tool authority
from quest text. Keep unrelated FFXIV/streaming functions intact and run merged tests.

WoW developer: retains canonical addon ownership. After contract agreement, extend
supported self-character/location facts in a new source schema with exact build/API
checks and owner in-game acceptance. Automatic SavedVariables export plus safe
Desktop parser/watch/consent and reload ordering is a separate transport milestone;
it is not a live connection. Do not change installed addon from this source packet.
Desktop changes are coordinated by Core through its existing team workflow.

Return CORE-WOWF-AREA-20261119-RESPONSE01.md and
SERVER-A-WOWF-AREA-20261119-RESPONSE01.md in established outboxes with reviewed
contracts/source/tests. No new endpoint/provider URL, grant expansion, DB migration,
service activation/restart or installation is authorized by arrival of this packet.
