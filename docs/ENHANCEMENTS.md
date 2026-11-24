# Later enhancements

Governing dialogue design: `Forever/docs/CONVERSATION-DESIGN.md` (project-root
relative). Core owns semantic admission and follow-ups; no required game/zone
phrase or client trigger routing. User-stated area is public retrieval context,
not observed location. Private/public evidence guards stay independent. Nine design
acceptance cases are recorded, not yet executed as runtime semantic tests.

**Resumed by owner on2026-11-19.** Area/reference/lore source work is active.
First Core source module and93-quest Dun Morogh pack are prepared and delivered;
this is not installed/full-zone/eligibility/route/lore-ranking acceptance. See root
research/2026-11-19-area-quests-distance-lore-resumed.md and area_source/RUNBOOK.md.
The older recorded-only wording below describes the initial roadmap.

Recorded 2026-11-18. Owner-requested roadmap, not implemented functionality.
Keep current Core lookup, accepted-quest evidence and timing work first.

## Zone quests not yet accepted and “what next?” guidance

Owner goal: Alfador considers quests the player has NOT picked up in the current
zone, explains the best next leveling action by quest name, and delivers a private
in-game whisper-style message plus speech when voice is enabled.

### Evidence and ranking

- Combine the observed quest log/progress with a versioned Forever quest catalog
  and verified pickup/turn-in locations. The current addon only reads accepted
  on-map candidates; it does not discover all unaccepted quests in a zone.
- Confirm availability for the same character: level, faction/class/race where
  relevant, prerequisites/chains, completion history, repeatable/seasonal rules
  and any required unlocks. Absent from the quest log is not proof of availability
  or completion. Distinguish catalog candidate, eligibility unknown and verified
  available-to-accept; do not promote a database entry to an observation.
- Compare accepted quests and verified unaccepted options using reward XP
  qualified by player level/build/ruleset. Include travel to pickup, objectives,
  turn-in, transport/waits and detours. Rank estimated XP/min only when all
  applicable time segments are supported; identify uncertainty and budget fit.
- Straight-line distance is not route time. Validate supported navigation/ETA
  interfaces separately and keep missing route data unknown. Shared objectives,
  nearby pickups/turn-ins and efficient quest bundles are later optimization
  candidates, not permission to claim an exhaustive best route.
- If timing is incomplete, compare verified rewards and explain that speed is
  unknown. If quest eligibility is incomplete, label the quest as a possible
  option to check, not a definitely available pickup. Recompute after meaningful
  progress/level/zone changes with correct freshness and input revisions.

### Presentation and Core ownership

- Core's game-specific logic belongs in `alphador_core/gaming_modules/wowf/`.
  Core alone chooses/interprets the recommendation, notification timing and
  assistant policy. Shared authentication/dialogue/tool admission stay in Core.
- Present a short, private Alfador whisper-style line in local in-game chat (or
  a dedicated personal chat surface), using quest/NPC/location names, the next
  action and a brief reason. Do not require a bot/player account named Alfador,
  impersonate another player, or broadcast recommendations to public/group chat.
  Actual native whisper routing is not assumed supported or needed for privacy.
- Example of intended wording only: “Pick up [quest name] from [NPC]; it fits
  your time budget and shares objectives with [accepted quest].” Fill only from
  verified evidence. No real quest/location/reward is asserted by this example.
- When the existing Core-owned voice setting/mode permits speech, read the same
  recommendation aloud. Respect mute/voice-off and Core's interruption/admission
  rules; do not add addon wake aliases or local intent parsing. Desktop audio
  playback is the established fallback candidate; custom voice inside native WoW
  remains unverified. Text should still be available when voice is off.
- The addon presents output and permitted observations only. No automatic quest
  pickup, movement, targeting, turn-in or synthetic input is included.

### Dependencies and acceptance

1. Verified, authorized Forever catalog coverage, locations and eligibility/XP
   mechanics, including data terms/build provenance; do not borrow Retail facts.
2. Actual WoW-only Core/QuestLog lookup and historical observation intake contract
   with authenticated session/revocation/audit acceptance. Current request was
   delivered to both maintainers; it has not established a working connection.
3. Permitted Core-to-client reply delivery. Native addon inbound transport is
   unresolved; local UI refresh does not solve it. Use an explicitly supported
   channel or label a Desktop overlay fallback accurately.
4. Independently accepted route/objective/turn-in timing, then character-specific
   ranking tests. Verify unavailable prerequisites and no-time-data fallbacks.
5. Manual acceptance: a genuinely unaccepted/eligible quest is suggested by NAME,
   wrong-level/completed/ineligible quests are excluded, the reason reflects
   verified data, output is private, and voice-on/off behaves correctly. Check
   stale observations, changed zones, revoked sessions and unavailable transport.

This is a later enhancement only. No catalog integration, ranking expansion,
whisper, voice routing, network connection, game update or server change was made
when recording it. Do not hold up the current accepted-quest/Core milestone.
