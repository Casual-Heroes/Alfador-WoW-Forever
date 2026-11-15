# WoW capability discovery

Internal research, 2026-11-13. Forever first; Retail second. Nothing in this
directory is installed, packaged with Desktop, or connected to Core.

## Local evidence

Battle.net's local installation record points to
`E:\Program FIles\World of Warcraft`. That root contains `_retail_`, no
`_forever_`. The local `.build.info` and `Wow.exe` agree on Retail
`12.1.0.69299`. No running WoW process was found during inspection.
These facts describe this installation, not all possible installations.

`AlfadorProbe` is staged source, not in-game-verified functionality. Its TOC
targets that observed Retail interface version, `120100`. Do not declare
Forever compatibility by guessing its interface number. Obtain Forever's
`GetBuildInfo()` output and test there before adding a Forever TOC.

## Probe behavior and manual acceptance

The probe never executes gameplay actions, reads damage, reads chat, inspects
other players, sends addon messages, opens sockets, or connects to Alfador.
There is no arbitrary API execution command. It does not alter game settings.

When deliberately loaded in an internal test client:

1. Run `/alfadorprobe` outside combat. Confirm no Lua error. It captures build,
   character identity, zone, pet presence, quest-log entry count and the player's
   equipment item IDs by slot. Nil, errors and restricted values remain explicit
   unavailable states. No saved plan is consulted.
2. Run `/alfadorprobe start`, play normally, then `/alfadorprobe stop`. Only
   selected event names are counted, with no payloads or exact event timestamps.
   Counts saturate at 10,000 per event. Event registration is not proof an event
   fires or carries useful data. Reloading resets the in-memory counters.
3. Run `/alfadorprobe` again outside combat. Verify build, map and changed gear
   against the UI. Capture while in combat must be deferred. Missing secret-value
   checking must also prevent capture.
4. Reload or log out normally. Inspect only the per-character
   `SavedVariables/AlfadorProbe.lua` report. It includes your character identity;
   review before sharing. Never execute imported SavedVariables as Lua in Desktop.
5. Repeat independently in Forever once available, recording the exact client
   build and interface, event results, and rejected/restricted APIs.

The report is a manual snapshot with a capture timestamp. SavedVariables are
persistence, not a demonstrated live transport. There is no background file
watcher, upload, model connection, or inbound command channel in this prototype.

## FFXIV intent mapped to WoW

These are product mappings and test candidates, not claims that every system is
available in Forever. In particular, a namespace in a shared client does not
establish that its content is enabled for the current game.

| Original intent | Forever discovery target | Retail discovery target |
| --- | --- | --- |
| Party Finder | Available manual group-finding/listing UI; test actual features | Premade Groups and applicable Dungeon/Raid/PvP queues |
| Market board | Auction House: verify market identity, available queries and public API coverage | Auction House, with realm/region and commodity distinctions |
| Relic progression | Long class/weapon/quest chains and their prerequisites; no assumed equivalent relic system | Legendary/artifact and other long quest or collection chains, expansion-specific |
| Treasure maps | Treasure/exploration quests and known discovery locations actually present | Treasure, secrets, exploration achievements and prerequisite chains |
| Collections | Mounts, pets, recipes, reputations and other verified collection systems | Mounts, pets, appearances, toys, achievements, recipes and decor |
| Housing | Unverified; do not infer support from shared housing APIs | Housing catalog, collection and layout capabilities, verified separately |
| Pet job | Own combat pet/summons with verified ownership attribution | Same; distinguish combat pets from collectible battle pets |

## Evidence and gates

- Blizzard's [Forever announcement](https://worldofwarcraft.blizzard.com/en-gb/news/24302093)
  establishes the separate experience. A complete Forever addon API contract was
  not established in this investigation. Do not inherit Retail capabilities as
  confirmed Forever capabilities.
- Blizzard's generated
  [quest API documentation](https://raw.githubusercontent.com/Gethe/wow-ui-source/live/Interface/AddOns/Blizzard_APIDocumentationGenerated/QuestLogDocumentation.lua)
  lists quest-log and objective queries. This is Blizzard source mirrored by
  Gethe on a moving Retail branch, not the installed Forever client.
- The generated
  [damage-meter documentation](https://raw.githubusercontent.com/Gethe/wow-ui-source/live/Interface/AddOns/Blizzard_APIDocumentationGenerated/DamageMeterDocumentation.lua)
  includes individual-source session queries and combat secrecy annotations.
  This makes post-fight self-review a candidate, not a verified integration.
  The probe checks function presence only. A future test must establish safe
  out-of-combat access, duration, spell coverage and own-pet attribution without
  querying group totals or other-player source data. Aggregate damage cannot
  establish cast order, missed opportunities, or a cause of death by itself.
- Blizzard's [housing API announcement](https://us.forums.blizzard.com/en/blizzard/t/new-housing-apis/56815)
  explicitly covers Retail and lists decor, fixture, room, collection and house
  endpoints. It does not establish Forever housing or complete layout fidelity.
- [Combat addon policy](https://worldofwarcraft.blizzard.com/en-us/news/24246290/combat-philosophy-and-addon-disarmament-in-midnight),
  [addon development policy](https://eu.forums.blizzard.com/en/wow/t/wow-user-interface-add-on-development-policy/1642),
  and [EULA](https://www.blizzard.com/en-us/legal/simple/2c72a35c-bf1b-4ae6-99ec-80624e1b429c/blizzard-end-user-license-agreement)
  constrain the design. API availability alone is not Blizzard approval of an
  external AI integration. Never reconstruct restricted combat state through
  pixels, screen interpretation, memory access or another side channel.

## Connection decision remains open

First demonstrate local observations. Next validate user-mediated report import
as a bounded data-only format, with exact game/build/character/freshness and
explicit opt-in before sharing with Core. No executing Lua files as imports.
Live banter needs a separately verified, permitted low-latency source; this
prototype does not solve it. Do not promise queues or deaths reach Alfador live
through SavedVariables. No pixel telemetry or synthetic key/mouse transport.

Core retains all interpretation, personality, memory, speech intent and assistant
policy under ADR-0001. Desktop remains a typed adapter. Future gameplay-facing
features need supported in-game user interaction and per-action review; spoken
requests never become a generic WoW command execution surface.

## Status

- Installation discovery: completed, read-only.
- Product mapping and initial source review: completed, with unknowns above.
- Probe source: staged; not installed or executed in WoW.
- In-game behavior, Forever coverage, personal combat review, live transport and
  Core ingestion: unverified/unimplemented.
