# Alfador-wow manual tests

On 0.0.22, choose **Portrait + Arrow** with a quest tracked. Confirm the
arrow starts below the portrait. Drag the arrow and check that the distance
moves with it while the portrait stays put. Switch modes and return, then
reload and verify the arrow stays where you put it.

## 0.0.21 WoW AddOns settings

After reloading, open **Esc → Options → AddOns → Alfador-wow**.
Choose Portrait + Arrow and verify the navigator updates. Toggle Follow
tracked quests and Always show. Right-click the navigator and verify that
it opens the same native settings page. Reload and check the saved values.

## 0.0.18 navigator settings acceptance

On build 71037, reload and check that Alfador appears before selecting a
quest. Track Return to Bellowfiz through WoW's quest tracker. In Card, Portrait,
and Arrow modes, check that the same distance remains visible and updates as
you move. Switch to another tracked quest and check that the display follows
the new target. Untrack and verify the idle label. With a target in another
map, check that no direction or distance from the previous target survives.
Reload and check that the display and follow preferences persist.

## 0.0.17 next pickup acceptance

Finish a local routed quest on build 71037 and leave the route card open.
Check that it says Route complete and names a quest and pickup if a lead is
available. Check the listed XP, distance and catalog rationale. If the NPC
offers that quest, open the dialogue and confirm the wording becomes Pick up.
Click Guide me there and verify it starts a new route. Check that Janus is
visible alongside Alfador.

## 0.0.16 completion and combat acceptance

On the character that completed Operation Recombobulation, run
`/alfadorwowguide route 412`. Expect WoW's turned-in status and no new pickup
route. Use a different active quest for the objective-to-turn-in check. With
a route selected, rotate in ordinary outdoor combat and check that the
arrow tracks you if the game exposes the required data. An unavailable
position or facing should hide the arrow. The route should advance only
after combat ends. Check the portrait crop and action labels in-game.

## 0.0.15 local route acceptance

On build 71037 in Dun Morogh, run `/alfadorwowguide route 412` with
Operation Recombobulation available or already in your journal. Verify
Razzle's pickup, the catalog lead for the remaining parts, and the Razzle
turn-in after both objectives complete. Verify the button can place each pin
and that a manually chosen waypoint survives automatic step advancement.
Check quest completion against the live journal. The same case covers two
objectives from the same source rather than grouping unrelated pickups.
Use `/alfadorwowguide voice on` to test local TTS, and `tips on` to verify an
outdoor approach emits one tip. Use `route story` to test curated lore and
story follow-up. Check the fallback when an objective cannot be mapped.

On 0.0.14, pin a known pickup outdoors on build 71037. Confirm Alfador's
portrait renders and the arrow turns toward the same map pin when you rotate.
Drag the card, change its scale with the mouse wheel, and close it. Reopen
it by pinning again. Walk toward the pickup and check that the distance falls.
Check that the arrow pauses during combat or a zone change and stops when
the quest is accepted. Desktop voice has its own existing path.

On 0.0.13, open `/alfadorwowguide nearby` and click **Pin first pickup**.
Confirm the waypoint matches the first displayed pickup. Repeat after changing
maps and check that the guide refreshes or refuses the old pickup.

## Local quest guidance candidate 0.0.12

Use Forever 1.60.1 build 71037 and interface 16001, outside combat.

1. In Ironforge near Gnoarn, run `/alfadorwowguide nearby` and compare the
   displayed pickup coordinates for a known NPC with its actual position on
   the same game map. Move farther away and rerun to check the ordering.
2. Run `/alfadorwowguide xp` and `/alfadorwowguide chains`. Verify the XP list
   uses listed XP. On a character below level 20, `The Day After` should not
   be a pickup lead. On a qualifying character, `/alfadorwowguide 2927` should
   mark `Gnogaine` as a Gnomeregan breadcrumb with no dungeon unlock claim.
3. For a shown pickup, run `/alfadorwowguide pin <quest ID>` and verify the
   game map or installed TomTom places it at the same NPC. Try a quest on
   another map and check that the existing waypoint stays in place.
4. Run `/alfadorwowguide lore` in Dun Morogh and Elwynn Forest. Check the
   story descriptions separately from the listed XP. Verify quest 218's
   item choices against the game rewards if it is offered.
5. On unsupported maps or whenever position cannot be read, check that the
   guide reports it unavailable and `/alfadorwowguide zone` still works where
   catalog leads exist. No export, external app or combat logging is needed.

## Historical capture manual test (0.0.6)

Target: Forever 1.60.1, build 70959, interface 16001. Internal test source only.
The archive does not install itself. No game folder, production package or
running WoW session was changed by the build. Keep the test separate from
normal addon releases and installers. Runtime acceptance remains pending.

## What this build does

The single `/alfadorwow` command reads your own player level/current map
and up to 50 quest-log candidates reported by IsOnMap. It opens a readable quest
summary with game-observed names; **Show report** opens the local JSON copy
view. There is no automatic upload, SavedVariables export, gameplay action, Core
connection or recommendation UI. Version 0.0.3 can read reward XP for the selected
log quest only, if reward display is available and selection/character/level
checks hold. Other XP and all timing remain unavailable. This is an API amount,
not accepted UI verification or proof of actual XP gained.
It refuses capture in combat, without the required secret-value checker, or on
a different build. A refused refresh hides the previous report.

## When loaded for a deliberate manual addon test

1. Confirm AddOns shows **Alfador-wow**. Record actual
   GetBuildInfo output and test date; test Totem Ale first.
2. Outside combat, with the world map closed, run `/alfadorwow`.
   Confirm names/progress are shown and no Lua error. Check names against your
   quest log; unavailable names must not become guessed names or raw IDs.
3. Click **Show report**, press Ctrl+C in the selected text, paste into a UTF-8 text file such as
   `totem-ale-quest-capture.json`, and close the panel. Inspect your identity
   before sharing. Never run the exported content as a program.
4. Compare player/level/map and several quest IDs against the game UI. Record
   whether the quest is accepted, objectives complete, or already turned in.
   The build does not establish exact minimum levels or prerequisites.
5. Open the world map to a DIFFERENT zone and capture again. Record whether
   IsOnMap changes with the displayed map. This checks a known ambiguity; do
   not treat candidates as verified current-zone quests without resolving it.
6. Change zones and capture again. Confirm the player map changes and the local
   serial increments. This serial is not authentication or replay protection.
7. During ordinary combat, if you choose to try the command, it should refuse
   capture and hide the earlier report. No combat payload should be exported.
8. Check several quests, not just one matching entry. Empty candidates with
   unresolved entries mean unavailable coverage, not “nothing to do.” Record
   game API errors, missing APIs and unexpected completion semantics.

## Selected-quest XP check (0.0.6)

1. Open your quest log, select one accepted quest and note the reward XP shown.
   Do not assume the quest's displayed level is its minimum required level.
2. Run `/alfadorwow` outside combat. Refer to quests by their displayed names.
   Under **Show report**, the capture should use schema draft4 and include titles.
   At most the selected on-map candidate may have observed rewardXP. Its
   rewardXPContext must name the same quest ID, player level and capture time.
3. Compare the number with the UI. If it is zero, hidden, different or unavailable,
   report that exact result; do not substitute a guessed or Classic XP value.
4. Select a different quest and repeat. XP must not be copied to every quest;
   selection changes do not reuse an old quest amount. No automatic selection or
   background scanning of reward panels is performed by Alfador-wow.

   With the readable window still open, switching the selected quest should now
   update the selected marker/reward without another slash command. Press
   **Refresh** if needed. Check The Boar Hunter against 250 displayed XP and The
   Stolen Journal against 550 displayed XP as shown in the owner's screenshots;
   recheck the game UI if the player's level or reward changes.
5. Keep each capture's time and level; do not merge XP across a level-up as though
   it were one current snapshot. These are displayed reward observations, not
   earned-XP measurements or a fastest-quest recommendation.

If XP stays unavailable, report `selectedQuestAtCapture` and each candidate's
`rewardXPRead`. These are fixed diagnostic values, not commands or assistant
policy. `rewards-not-shown` differs from a missing API; `not-selected-quest` may
mean the selected quest is outside the current candidates. Do not remove the
selection/visibility checks or infer that unavailable means zero XP.

Ask/answer by the selected quest's NAME and visible reward amount; numeric IDs
are supporting technical diagnostics only. Check **Back to quests** returns to
the readable summary. The new view has not yet received in-game visual acceptance.

## Refresh regression checks

- Keep the readable window open and switch quests; confirm the selected name and
  XP follow the game quest log. These are new captures, not relabeled old data.
- Click Refresh to request a new capture. Change zone/level during normal play
  and confirm the view reflects new context when safe.
- In Show report, select another quest: the report must stay unchanged while
  copying, and Refresh is disabled. Back to quests resumes updates.
- In combat/unknown combat state, automatic refresh pauses and the header says
  refresh paused. Manual capture still refuses combat. Do not provoke combat
  only for this test if it interferes with play.
- Close the window; no background capture or chat spam should continue.

The earlier screenshots verify names and displayed rewards but show the 0.0.5
snapshot-refresh mismatch. Version 0.0.6's new refresh behavior still requires
in-game acceptance; local mocked tests do not establish it.

## Local file validation

From `G:\Projects\Alfador-WoW`:

```powershell
python Forever/tools/quest_capture_import.py C:/path/to/totem-ale-quest-capture.json
```

This prints a local receipt/hash. Success means structural validation only;
character/session authenticity, quest eligibility and Core delivery remain
unestablished. Paste the JSON or provide the file for review only after inspecting
it. Do not replace missing XP/times with values from a different game/build.

## Evidence to retain

Record date, exact build/interface, character label, region, zone, player level,
candidate count, unresolved count, checked quest IDs, world-map-open behavior,
copy/paste/parser outcome and any Lua error. Mark each result observed, failed,
restricted or unavailable. Do not mark this checklist passed from mocked tests.

Real Core/QuestLog connection, verified quest XP, timing measurements and a
WoW-only authenticated lookup are subsequent acceptance steps.
