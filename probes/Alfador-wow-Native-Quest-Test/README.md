# Shadowglen native quest-data test

Target is WoW Forever `1.60.1`, build `71037`, interface `16001`. The owner
confirmed these values and player UI map `1438` while in Shadowglen on
November 23, 2026. The owner reported no accepted quests at the start.
With the full offer open before acceptance, the owner captured quest `456`,
**The Balance of Nature**, `170` from `GetRewardXP()`, and `0` from
`GetNumQuestRewards()`. A second native read confirmed two reward choices
and a nonempty description (`#GetQuestText()` returned 499 bytes).
`C_Map.GetPlayerMapPosition(1438, "player")` returned approximately
`0.58685076236725, 0.44352900981903`, or **58.69, 44.35** in map percentages.
The offer's choice rows returned **Archery Training Gloves** (`5394`) and
**Stemleaf Bracers** (`11187`), one of each as separate choices. The API's
usability field was true for both. `C_QuestLog.GetNextWaypoint(456)` returned
empty before acceptance and on the follow-up dump. A subsequent combined
dump returned `true` from `C_QuestLog.IsOnQuest(456)` and no values from
`C_QuestLog.GetNextWaypointForMap(456, 1438)`. This directly establishes an
accepted quest with no readable map-specific waypoint in that observation.
Filtering `C_QuestLog.GetQuestsOnMap(1438)` for accepted quest `456` returned
`0.58479541540146, 0.43616944551468`, or **58.48, 43.62**. This is a native
quest map pin; the screenshot does not identify its objective or turn-in role.
Neither waypoint API was required for that pin. Coverage before acceptance
and coverage across multiple objectives and distinct quests remain open.

After the owner reported finishing both kill objectives (7 Nightsabers and
4 Young Thistle Boars), and before turning in, the same quest-ID filter returned
`0.58695578575134, 0.44265192747116`, or **58.70, 44.27**. This confirms a native
pin change between the two observed stages. Objective completion was
owner-reported. After turn-in, the owner captured `IsOnQuest(456) = false`
and `IsQuestFlaggedCompleted(456) = true`. This confirms the native offer,
accepted quest, pin change and completed quest lifecycle on build 71037,
without a catalog in the experiment. The NPC's identity, precise pin-to-NPC
alignment and pin removal after turn-in were not separately measured.

The owner reported a separate, unaccepted quest marker near **60.9, 42.0**.
The full map-POI dump screenshot showed only quest `456` at **58.70, 44.27**,
with `isQuestStart=false` and `inProgress=true`. No row for the reported
pickup was visible. The source of that marker was not observed, so this is a
coverage result for the API read rather than a general claim about all native
quest starts. A permitted follow-up is opening the nearby giver's dialogue
without accepting its quests, and comparing the available offers and map pins.

The game can be tested through manual chat commands. The Lua source is an
isolated local experiment for mocked APIs. It is outside the game install and
production package. It has no catalog, background capture, network, or login.

1. With the journal empty and quest dialogue closed, inspect the player's
   map position and the current map's readable quest pins.

   ```text
   /dump C_Map.GetPlayerMapPosition(1438,"player")
   /dump #(C_QuestLog.GetQuestsOnMap(1438) or {})
   ```

2. Open a quest giver's list. If it uses the gossip window, inspect the
   available quests. Then open a single full quest offer before accepting.

   ```text
   /dump C_GossipInfo.GetAvailableQuests()
   /dump GetQuestID(), GetTitleText(), GetRewardXP(), GetNumQuestRewards(), GetNumQuestChoices()
   /dump GetQuestText() and #GetQuestText(), GetObjectiveText() and #GetObjectiveText()
   /dump GetRewardMoney()
   /dump C_QuestLog.GetNextWaypoint(GetQuestID())
   ```

   Check a positive item count against the relevant first reward row with
   `/dump GetQuestItemInfo("reward",1)` or `/dump GetQuestItemInfo("choice",1)`.
   If the API returns zero XP or no data, record that separately from the
   amount shown in the quest UI. Readable descriptions need only be reported
   as available or unavailable for the experiment.

3. Manually accept the same quest when ready. Select it in the quest log and
   compare the description, XP, reward counts, objectives and coordinates.

   ```text
   /dump C_QuestLog.GetSelectedQuest(), GetQuestLogRewardXP(), GetNumQuestLogRewards(), GetNumQuestLogChoices()
   /dump C_QuestLog.GetNextWaypoint(C_QuestLog.GetSelectedQuest())
   /dump C_QuestLog.GetQuestObjectives(C_QuestLog.GetSelectedQuest())
   ```

An offered quest is scoped to the NPC and dialogue. Waypoints and map pins
are observed navigation points, with no assumption that they identify every
pickup, objective spawn, or turn-in. Empty results are not zone-wide proof.
The current probe measures native UI and API coverage. It does not read
client archives or establish a way to reconstruct Polestar's whole catalog.

API sources: [Forever quest log documentation](https://raw.githubusercontent.com/Gethe/wow-ui-source/forever/Interface/AddOns/Blizzard_APIDocumentationGenerated/QuestLogDocumentation.lua)
and [Forever quest reward frame](https://raw.githubusercontent.com/Gethe/wow-ui-source/forever/Interface/AddOns/Blizzard_UIPanels_Game/Vanilla/QuestInfo.lua).
