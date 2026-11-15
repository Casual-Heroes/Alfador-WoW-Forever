# ADR-0001: Server-authoritative brain and capability-only clients

- Status: Accepted
- Date: 2026-11-01
- Decision owner: Ryven
- Applies to: Alfador Core, Alfador Desktop, Meld overlays, future mobile/web clients

## Context

Alfador has one persistent brain hosted by Alfador Core. Desktop, Meld, mobile,
and browser applications are bodies that capture input, render output, and
perform device-local operations. If a client interprets speech or owns
assistant policy, behavior diverges by device and server enforcement can be
bypassed.

Meld's WebChannel listens only on the Windows loopback interface. Therefore the
server must authorize Meld actions, while a narrowly scoped Windows adapter
performs the final loopback call.

## Decision

**The server decides; clients capture, present, and execute narrowly typed
capabilities.**

Alfador Core exclusively owns:

- wake names and aliases;
- mode-aware command recognition;
- dialogue, personality, memory, and tool policy;
- whether a command is authorized;
- command settings such as clip enablement and duration;
- generation of typed client-action requests.

Clients may own only:

- microphone capture, VAD, and audio encoding;
- transport of unmodified transcripts to Core;
- audio playback and visual rendering;
- operating-system/device integration;
- execution of an explicit, allowlisted, typed Core action;
- reporting action success or failure to Core.

A client must never:

- parse transcripts to decide assistant intent;
- maintain wake aliases or command phrases;
- silently substitute local policy for Core policy;
- accept arbitrary command names or model-generated API calls;
- expose a generic local command-execution surface.

For Meld clipping, Core emits only:

```text
CLIENT_ACTION_REQUEST
action=MELD_RECORD_CLIP
target_capability=windows.meld
request_id=<opaque id>
duration_seconds=10|30|60|90|120
```

Alfador Desktop validates that exact schema, invokes the fixed
`meld.recordClip` command on `127.0.0.1:13376`, and returns a
`client.action_result`. No transcript phrase matching occurs in Desktop.
The settings window may present Core's allowlisted clip durations, but the
authenticated Core endpoint validates and persists the selected value. Desktop
does not store or independently choose clip policy.

For an authenticated QuestLog record that Core decides should open, Core emits
only:

```text
CLIENT_ACTION_REQUEST
action=OPEN_QUESTLOG_URL
target_capability=windows.default_browser
request_id=<opaque id>
url=https://questlog.casual-heroes.com/...
allowed_host=questlog.casual-heroes.com
```

Desktop independently requires HTTPS, the exact QuestLog hostname, the default
HTTPS port, and no embedded credentials before asking the operating system to
open the URL. It does not accept generic browser actions or infer them from
speech.

In Wake mode, a command is authorized either when the wake name appears in the
same final transcript or while Core's rolling wake conversation remains open.
This accommodates STT fragment boundaries without moving wake policy into the
client. Outside that server-owned window, the command is ignored.

## Enforcement

- Core tests verify Wake, Active, Standby, and Off behavior and ensure direct
  commands bypass the dialogue model.
- Protocol validation rejects unrecognized client action results.
- Desktop's architecture check runs as part of `npm run lint` and rejects
  transcript-command policy or arbitrary Meld command dispatch in `src/`.
- Changes to this boundary require a new superseding ADR, protocol tests, and
  explicit approval from the decision owner.

## Consequences

Device-local APIs remain reachable without moving the brain back onto Windows.
New integrations require a typed Core action plus a narrow client capability
adapter. This adds a small protocol round trip, but prevents policy drift and
keeps all Alfador bodies consistent.
