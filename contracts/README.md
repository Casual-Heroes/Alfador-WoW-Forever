# Draft observation contract

`character-context.schema.json` is a local JSON Schema draft-07 proposal, not a
registered Core message. `examples/unavailable.json` is synthetic structure only.
No real character was captured and no data was sent to Core.

The owner scope is Druid/Paladin, PvE tanking/DPS. This source contract remains
class-neutral; scope and desired roles are recommendation inputs owned by Core.

Transport and semantic validation must additionally enforce:

- At most 256 KiB UTF-8 before parsing; no executing imported Lua.
- Trusted producer, authenticated user and explicit character binding.
- A verified game/build/source identity and bounded strings and collections.
- Unique slot numbers and unique selected talent IDs, including conflicting
  ranks. JSON Schema uniqueItems only rejects identical duplicate objects.
- An observed equipment section requires all expected slots and verified slot
  states; partial coverage must use partial. Missing item ID is not an empty slot.
  This initial schema has no confirmed-empty slot representation; empty slots
  remain unavailable until that observation contract is verified.
- Talents, gear and zone must share a coherent capture revision or be marked
  partial. Neither receipt time nor retrieval time makes an old snapshot current.
- Dates must parse, capture time cannot exceed retrieval time, and future times
  require rejection under the receiving service's clock-skew rules.
- Per-slot modified item context must be resolved before mechanical ranking.
- Planned equipment and planned talents are not accepted as observations.

Run structural checks using an existing Ajv 6 installation (no dependency install):

```text
node contracts/check-contract.cjs <path-to-ajv-module>
```

These checks validate the draft's structure, not observation truth, in-game
compatibility, full semantic acceptance or a server connection.
