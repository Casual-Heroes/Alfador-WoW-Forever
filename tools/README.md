# Offline Forever observation importer

## Build the isolated manual-test probe

```powershell
python -m pip install --only-binary=:all: --no-deps --target Forever/.builddeps -r Forever/tests/requirements-build.txt
python Forever/tools/build_addon.py
```

The builder requires all importer, pilot and mocked Lua runtime tests to pass
without skips. It verifies source hashes and archive contents, then writes the
ZIP, manifest and SHA-256 file under ignored `Forever/builds/`. Differing existing
builds cannot be overwritten. No game files or global Python packages are changed.
Lupa is a build/test dependency only; exported JSON and SavedVariables are never
executed by these tests. The test harness executes trusted repository Lua only.

The manual-test checklist is `Forever/docs/ALFADOR-WOW-MANUAL-TEST.md`.

Current quest pilot uses a separate raw capture contract. Validate a copied
probe report with `python Forever/tools/quest_capture_import.py report.json` from
the canonical root. It reports candidate counts and a content hash only; no
eligibility, verified session, XP, timing or Core delivery is established.
The character importer described below remains earlier deferred groundwork.

Implemented November 18, 2026. Python 3.10+ standard library only. This is source
in the WoW repository, not a Desktop installation or a running Core bridge.

Run from the canonical project root:

```powershell
python Forever/tools/observation_import.py C:/path/to/report.json --subject YOUR_VERIFIED_CHARACTER_ID --region us --build 1.60.1
python -m unittest discover -s Forever/tools -p 'test_*.py' -v
```

The input must be explicit JSON matching the bundled draft contract. Existing
`AlfadorProbeReport` SavedVariables are Lua and are intentionally rejected; no
Lua execution or automatic conversion is provided. No JSON exporter is installed
yet. Do not rename SavedVariables to JSON or treat a synthetic fixture as a real
report. The version argument is the `GetBuildInfo()` version field, distinct from
the numeric build field (for example, 70959).

The importer reads at most 256 KiB plus one overflow byte, validates structure
and selected semantics, checks caller-supplied character/region/version, and
prints a local receipt with source/canonical SHA-256 hashes. It writes no files,
opens no sockets, executes no imports, and does not log character payloads.
Rejected input exits with code 1. Successful local validation exits with code 0.

Every accepted document stays historical. Null capture time stays unknown;
retrieval time never becomes capture time. Equipment completeness and conflicting
slot/talent identities are checked. Unknown slot contents never become empty.
The tool does not establish coherent in-game capture, authenticated ownership,
item mechanics, full talent support or recommendation readiness. The bundled
schema evaluator supports only the fixed contract's keywords; it is not an
imported-schema or general JSON Schema execution feature.

29 synthetic tests passed on November 18 with Python 3.12. They cover malformed
and oversized input, Lua rejection, conflicting talent/slot entries, identity,
game/build mismatches, dates, partial coverage and preservation of unknowns.
No game client was exercised; no actual snapshot or Core receipt was produced.

Next: obtain Forever's `GetBuildInfo()` output, verify the safe APIs on that
client, then implement an isolated manual JSON exporter. Only an approved
authenticated WoW Core contract can enable eventual transmission; this importer
does not send documents using another game's protocol.
