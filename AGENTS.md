# Alfador WoW repository instructions

## Project ownership and layout

Use `G:\Projects\Alfador-WoW` as the canonical WoW project. Forever comes first,
Retail second. Keep game-specific source under `Forever/` and `Retail/`.
Do not assume shared-client API presence proves a feature is supported in both.
Keep dated evidence, exact client builds, sources, unknowns and next steps in
`docs/STATUS.md` and the game READMEs. Keep investigation history under docs.
Do not create parallel canonical addon copies in Alfador Desktop.

## Mandatory architecture

Read `docs/adr/0001-server-authoritative-brain.md` before changing architecture,
protocol handling, voice commands, wake behavior or device integrations.
Alfador Core is the only brain and policy authority. Clients capture input,
present output and execute narrowly typed capabilities. Submit transcripts
without interpreting assistant intent. Wake aliases, command phrases, mode rules,
authorization and command settings belong exclusively to Core.

Core game-specific work belongs in each game's own folder under
`alphador_core/gaming_modules/`. Forever uses `wowf/`, alongside `ffxiv/`;
do not put WoW behavior into FFXIV. Shared Core authorization/routing/dialogue
remain shared infrastructure, not duplicated game brains. Retail support must
be scoped independently when introduced.

Device-local adapters execute only explicit allowlisted typed Core actions.
Never add generic voice-to-command, model-to-command, shell, HTTP or Meld API
execution surfaces. Meld loopback remains behind MELD_RECORD_CLIP unless a
superseding ADR approves another typed action. Changing this boundary requires
Ryven's explicit approval, a superseding ADR, server protocol/policy tests and
updated client architecture checks.

## Observed equipment versus plans

Website and app edits are plans, never equipped-gear evidence. Saving, restoring,
copying presets, linking a Journey, collecting an item or selecting a build must
not overwrite game observations. Keep source, game, character, revision and
freshness distinct. Only validated same-game, same-character game observations
may confirm slots. Partial, stale or unavailable data stays partial, historical
or unknown. Never fill missing slots from plans. A matching subset does not
confirm the entire build or unobserved effects. Core distinguishes plan advice
from observed-equipment advice; Desktop must not invent assistant policy.
Default equipment views to observations and label local/site edits and receipts
planned.

## WoW integration boundaries

Use supported addon interfaces and authorized data sources. Verify policy and
client restrictions before extending capabilities. No gameplay automation,
protected-action bypasses, injection, process-memory reading, synthetic input,
or reconstruction/export of restricted combat state through side channels.
Limit performance work to the player and verified owned combat pets/summons;
do not collect or analyze other players' damage. Preserve unavailable states.
Never execute SavedVariables or imported Lua as a Desktop data-import mechanism.
An external live connection is unverified; do not claim SavedVariables provide it.

Keep probes isolated from production, installers and game installations. Record
what was actually tested; static checks do not count as in-game acceptance.
