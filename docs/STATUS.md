# WoW project handoff

Updated 2026-11-15. Canonical project: `G:\Projects\Alfador-WoW`.

## Direction

Rich natural conversation, banter and permitted awareness across exploration,
quests, collections, travel, grouping, economy and personal improvement.
Forever first; Retail second. Core remains the only brain.

## Completed

- Initial scope and FFXIV-to-WoW intent mapping recorded in the dated research.
- On 2026-11-13, discovered `E:\Program FIles\World of Warcraft`, containing
  Retail build `12.1.0.69299`; no Forever client in that inspected installation.
  This is historical evidence, not a new scan on November 15.
- Staged read-only AlfadorProbe, now under `Retail/addons/AlfadorProbe`.
- Desktop architecture boundary check passed on November 13. This did not
  execute or validate the Lua addon in game.
- On November 15, separated the WoW project from Desktop, preserved the research
  and ADR-0001, and established game-specific source folders and handoff files.

## Unverified / unimplemented

- Forever installation, exact build/interface, supported APIs and event behavior.
- All in-game probe behavior, including Retail.
- Own-player post-fight damage access and owned-pet attribution.
- Permitted low-latency delivery to Alfador, data-only import and Core ingestion.
- Queue/group actions, housing coverage and public API contracts by game.

## Next work

1. Locate or obtain the Forever client and establish its exact build/interface.
2. Review the existing probe against that client; add a Forever variant only when
   supported. Do not copy the Retail TOC and call it Forever-compatible.
3. Run isolated manual acceptance from the research notes. Record observed,
   restricted, absent and failed results with client identity and capture time.
4. Resolve permitted transport before promising live reactions. Keep manual
   snapshots distinct from live observations and preserve per-slot freshness.
5. Design any approved Core contract and Desktop adapter in their owning projects.

## Provenance

`docs/research/2026-11-13-capability-discovery.md` and Retail probe source were
migrated from `Alfador-Desktop/wow_addon`. The Desktop location retains a pointer
only after migration verification. No game installation or running app changed.
