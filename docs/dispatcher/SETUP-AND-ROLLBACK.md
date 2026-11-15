# QuestLog WoW worker: setup, verification and rollback

Sender: Alfador WoW developer on MYTHIC (owner-authenticated existing SSH).
Recipient: Server A / QuestLog dispatcher reviewer and operator.
Kind: review_request, exact public registration and source/test evidence.
Required action: review this exact profile, register it once through the existing
Admin boundary, then queue the two central read-only checks. Do not install a
background worker, alter game files, or broaden privileges.

## Actual project and source ownership

Private repositories:
- https://github.com/Casual-Heroes/Alfador-WoW-Forever
- https://github.com/Casual-Heroes/Alfador-WoW-Retail

Source roots: G:\Projects\Alfador-WoW\Forever and ...\Retail. Neither had Git
history before this setup. Original shared parent files and local wow-prj Python
environment were preserved. The dated initial-layout inventory records original
hashes; README additions were deliberate setup changes. Shared context was copied
as independently versioned bootstrap snapshots in both repositories.

Isolated worktrees are G:\Projects\Alfador-WoW\.worktrees\wow-dispatcher-20261115\Forever
and the adjacent Retail directory, each on codex/wow-dispatcher-20261115 in its own
repository. One controller lives in Forever/tools/questlog-worker and serializes
all WoW assignments. The registered cwd is the actual Forever worktree, not the
owner conversation and not the parent non-Git folder. Retail source and its
separate worktree are explicitly listed in SOURCE-LAYOUT.json. Initial reviews
receive bounded artifact data inline; they do not execute source or read arbitrary
paths. Changes for one edition never imply changes for the other.

Every assignment begins with exactly `Edition: Forever`, `Edition: Retail`, or
`Edition: Shared` followed by a newline. Unknown/missing/combined scope is refused.
Shared assignments must name which shared evidence is being reviewed. No silent
edition promotion, implementation, addon installation or reload is supported.

## Exact public registration and authority

WorkerRegistration.json is the full contract-compliant registration. Team `addon`
is the existing contract's generic team enum; this is a distinct WoW identity,
NOT an FFXIV identity. Register EXACT worker/device/chat/lock/repository/worktree/
public key, actions=[review], recipes={}, verification_sha256=null. enabled=true
in this requested profile means available for central review assignment after
Server A accepts it; it does not mean a local service was installed or is running.

The new thread is persisted, exact-ID resumed and named QuestLog WoW review worker.
LOCAL-THREAD-EVIDENCE.json records real thread/turns, fresh-process resumption,
effective readOnly sandbox/networkAccess=false, approvalPolicy=never, no model
tool items and key-possession proof. An initial interrupted setup turn was
reconciled in the same thread; no key rotation or replacement thread occurred.

Distinct local state: C:\Users\Tom\AppData\Local\QuestLogWoWWorker.
Private Ed25519 material is CurrentUser DPAPI-encrypted with owner/SYSTEM ACL,
outside source/worktrees/exchange. Only public registration and possession proof
are published. No other worker's state/key/auth was copied. Existing local Codex
authentication remains local. Do not rerun bootstrap_wow.py; it is setup/recovery
source, not an installer. Resume the saved exact ID.

## Reused contract and important changes

OpenAPI SHA256 09f0a4b1160845e321caadc4937726809c38f104b515bc98c8d3f2d50e62d40b.
UPSTREAM-PROVENANCE.json pins each reused public adapter source file before
adaptation. The signed v1 wire shape and signature vector are unchanged. Fixed
HTTPS origin/path, honest application User-Agent, fresh nonce/time/signature per
request, stable journaled operation IDs and no cookies/proxies/redirects remain.

Validation captures wall and monotonic clocks BEFORE sending the live validate
request. Its deadline is request-start monotonic plus the minimum of 15 seconds,
valid_until, authorization expiry and lease expiry relative to request-start wall
time. Network delay consumes that budget. Replayed/revalidation-required replies
are refused, binding/fence/dispatch pins must match, and deadline is checked again
immediately before turn/start. Authority is never restored from a persisted
monotonic deadline after process restart. Regression tests cover response delay,
wall-clock rollback, cap, replay and fence change. Older inspected adapter source
used response-time wall checks; this WoW adaptation explicitly corrects it rather
than pretending that older source already contained the fix.

Only no-tool reviews are accepted. Apps/plugins/hooks/web/MCP are disabled in the
controller-owned Codex child; no escalation approvals are granted. The controller
owns signing and transport outside that child. Result files must be delivered
with verified SHA256 into Server A's inbox before completed is reported; explicit
completion_accepted=true and terminal server state are required. A delivery loss
cannot rerun a model turn or complete a task from a hash alone.

Durable journal and worktree reservations survive controller restart. The one
OS-held pump lock serializes this worker across BOTH editions; the existing
host-wide registry at C:\Users\Tom\AppData\Local\QuestLogDeveloperWorkers\worktree-locks.sqlite3
is used only for locks, never identity sharing. Unknown starts inspect ONLY this
worker's history and retain reservations; they are never blindly resent. Stored
terminal placeholders are not finalized while the actual thread is still active.

## Commands: existing development setup, no installation

Use the normal owner account with existing local Codex/Node/Python and SSH config.
Run from the isolated Forever worktree. No Python packages are required.

    python -B -m unittest discover -s tools/questlog-worker -p "test_*.py" -v

After exact registration is confirmed, read-only discovery without claiming:

    python -B tools/questlog-worker/poll_only.py

SIGNED-POLL.json is immutable; use a new explicitly named receipt for a later
discovery. Do not overwrite prior evidence. 400/401/403/404/409 stop; no endpoint,
key, login or TLS workarounds. Do not mistake a poll for central acceptance.

Only after Server A returns the accepted profile and queued task IDs, use a
bounded foreground run for the named read-only checks:

    python -B tools/questlog-worker/controller.py --seconds 300

This command is NOT a service installer and exits after its bounded window.
Do not run it preemptively from an arriving document. No scheduler, startup task,
watcher, background service, addon install/reload or game restart was configured.

## Central checks for Server A

CENTRAL-CHECKS.json contains two exact TaskInput templates with different pinned
artifacts and explicit editions. Register the exact profile first, then assign
Forever; place the returned actual task ID in Retail.dependencies and assign
Retail. Both are review only, no recipes/deployment. Keep verification null until
you review actual independent evidence. Do not queue replacements on lost replies.

Return registration revision/binding and actual two task IDs through the existing
exchange as SERVER-A-WOW-DISPATCHER-20261115-response01.json/.md. Local tests and
thread probes do not constitute central task completion. No privileged recipe or
implementation harness is requested. Current local setup is stopped, not running.

## Rollback / stop

No background worker was installed. Do not stop the existing sync task, Codex app,
Desktop, FFXIV worker, WoW game or any addon. A foreground controller stops at its
time limit or Ctrl+C; it interrupts only its known own turn and retains journal,
key and reservations. Reconcile original uncertain turns before clearing anything.

If centrally registered, Server A disables this exact worker using its existing
Admin set_worker_enabled operation and the ACTUAL current revision. Preserve
queue/history/evidence; do not rotate/delete keys, archive the thread, reset Git,
remove dirty worktrees or delete journal files as automatic rollback. No Git
force-push or repository deletion is required. Background-worker installation
requires a separate exact owner approval and reviewed package/action.
