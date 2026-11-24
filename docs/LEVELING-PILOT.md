# Current-zone leveling pilot

Later enhancement recorded separately in [ENHANCEMENTS.md](ENHANCEMENTS.md):
unaccepted zone quests, eligibility/route-aware recommendations, private in-game
text and voice when enabled. This does not expand the current pilot's acceptance
or imply an inbound Core connection is already supported.

Latest November 18: installed 0.0.3 adds selected-quest reward-XP observations,
not yet UI-verified. 119 local checks pass. A real deployed Core inspection
found no WoW research entry; the owner authorized and both maintainers received
the implementation request, requiring gaming_modules/wowf. Real lookup remains
pending. See parent selected-quest-xp-and-core-boundary research for exact hashes.

Build update November 18: an isolated manual-test ZIP is available under
`builds/Alfador-wow-0.0.1-16001-70959.zip`. It passed 94 local checks,
including 32 mocked Lua runtime checks. No in-game test or game installation
change occurred. See [manual-test checklist](ALFADOR-WOW-MANUAL-TEST.md).

Active owner direction, 2026-11-18. Supersedes the earlier broad first milestone
and initial two-quest limit. Character: owner-named Totem Ale, Paladin. Region,
current level, current zone and quest IDs have not yet been captured/verified.
Keep Reforged work separate and unchanged.

Question: “I've got twenty minutes. What should I do next to level?”

Use multiple eligible quests in the character's observed current zone, bounded
to 50 evaluated candidates. A zone change follows a new observation, not an
arbitrary request parameter. Missing zone coverage remains unknown. This does
not promise a complete quest database, all available unaccepted quests, a
transport model for every zone, or a jointly optimized route across quests.
Lore, gear, talents, PvP and avatar presentation are deferred.

## Evidence and calculation

Core must bind the snapshot to a verified session/character/build and resolve
minimum level, on-quest/progress/completion, prerequisites and zone membership.
The initial source probe only nominates quest-log candidates; it does not prove
all quest availability. Missing eligibility evidence excludes a candidate.

For each eligible quest, use reward XP verified for this character's level and
Forever ruleset/build. Calculate estimated XP/min = XP * 60 / (remaining travel
seconds + remaining objective seconds + remaining turn-in seconds). All three
segments need evidence. Include delivery legs, NPC travel and expected waits;
do not use objective time alone. Use a fresh revision after progress changes.

When any eligible candidate lacks a complete estimate, show verified XP values
and say “I can't yet tell which is faster.” Do not rank unknown times as zero,
declare a faster winner from XP alone, or claim it fits twenty minutes. Missing
XP is unknown, not zero. With complete estimates, compare individual quests that
fit the budget; show a tie rather than an arbitrary winner. State coverage and
uncertainty. Kill/travel XP, rested bonuses and shared-route efficiencies are
not modeled by this first reward-XP-only comparison.

`core_candidate/quest_pilot.py` is an offline candidate for owning-Core review,
not client advice logic or a deployed server feature. `core_candidate/access_demo.py`
is a synthetic server-session harness, not a replacement for real authorization.

## Measurements while playing

For a few objectives, record quest ID, character/level, map, build, capture/progress
revision, start/end UTC, active duration, completed objective amount and notes
about interruptions/grouping. Time travel and turn-in separately. A completed
sample is history; deriving a remaining-time estimate for a new state is a
separate Core calculation. Never blindly reuse an old full-objective duration
as current remaining time. Pause or annotate AFK, queues, detours and deaths.

Use `measurements/objective-samples.csv` as a blank manual record. Do not put
tokens or other players' details there. No automated combat capture is required.

## Navigation source review

Checked November 18 against the authors' project pages:

- [TomTom release](https://www.curseforge.com/wow/addons/tomtom/files/9493883/additional-files)
  lists Forever/1.60.1 support.
- [QuestGPS](https://www.curseforge.com/wow/addons/questgps) documents distance and
  ETA as straight-line estimates. That is not road/transport-aware route time.
- [Forever GPS](https://www.curseforge.com/wow/addons/forever-gps) advertises routes
  using roads, flights, boats and zeppelins.

No supported cross-addon ETA interface was established by this review. No addon
was installed, downloaded, or scraped internally. A rendered ETA is not proof
of an API. Keep travel time unavailable unless a documented interface is tested
on this exact Forever build, or use labeled manual timing. A measured travel
sample likewise applies only to its route/context.

## Security demonstration and real acceptance

The project folder organizes source, not permissions. Real Core/QuestLog must
verify the session, grant WoW-only read access, bind the current-zone/character
scope, check it before EVERY downstream call, and re-check revocation before
delivering results. Upstream credentials stay on the server; quest text, addon
payloads and model output cannot create scopes or choose arbitrary URLs/tools.

The local synthetic demo proves only behavior of the candidate harness: scoped
lookup success, malicious quest text does not expand scope, out-of-scope requests
stop before the callback, and revoked/expired sessions stop later delivery.
Its audit shows decision/reason, whether downstream work started, and whether a
response was delivered. It is in-memory test evidence, not a production audit.
Denial after in-flight revocation can withhold a response but cannot undo a
downstream read that already started. Real audit needs correlation/session ID,
verified actor, scope/version, data source/revision, timestamps and receipt.
Do not log raw tokens, credentials or quest-text payloads.

Real verified-session lookup and revocation against Core/QuestLog remain pending.
No server credentials or approved WoW endpoint/session contract is available in
this project. Do not send raw quest reports as dialogue or another game's event.
The old broad Core proposal is background; this scoped lookup is the next server
acceptance target. The existing read-only dispatcher is not granted new powers.

## Run and stream

```powershell
python -m unittest discover -s Forever/core_candidate -p 'test_*.py' -v
python Forever/core_candidate/demo.py
```

The demo prints clearly labeled INVENTED quest IDs/XP/times and synthetic-session
audit output. It does not connect to any game/service or authenticate a user.
29 pilot tests pass locally. Earlier importer tests remain separate.

Stream sequence: explain the reduced scope; show measured versus missing data;
show why travel/objective/turn-in all matter; compare complete timing with the
XP-only fallback; show synthetic denials with callback counts; then later repeat
against a real verified server session. Keep an explicit record of AI suggestions
accepted/rejected and the evidence for each decision. Do not present this mock
session demo or staged probe as an operational integration.

## Decision record for the stream

| Suggestion or constraint | Decision | Evidence or reason |
| --- | --- | --- |
| Start with lore, equipment and talent optimization | Deferred by owner | First value is a twenty-minute leveling decision |
| Fix the pilot to one named zone | Revised by owner | Use observed current zone, with missing coverage explicit |
| Limit to two quests | Revised by owner | Multiple eligible candidates, bounded to 50 |
| Derive a fastest quest from XP alone | Rejected | Full remaining travel/objective/turn-in estimates required |
| Treat GPS features as a ready integration | Rejected pending evidence | Project pages do not establish supported ETA access |
| Present local security tests as Core enforcement | Rejected | Sessions/lookups are synthetic; real server acceptance pending |
