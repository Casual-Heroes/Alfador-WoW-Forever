# Core WoW Forever conversation design correction

For Core, Desktop, the WoW add-on developer and Server A. This supersedes
the explicit-query recommendation in CORE-WOWF-AREA-20261119-RESPONSE01.md.
Its source verification and evidence limits still apply.

Core should understand ordinary questions and follow-ups from the current
conversation. Reuse semantic admission and Core-owned context rather than
adding a required game name, zone name, command phrase, or trigger regex.
An active, verified game may ground the topic. A recent explicit mention
can carry the conversation topic when game activity is unknown. The user's
stated area can identify a public catalog query, without attesting their
location. A historical journal can establish what was recorded at its
capture time. It cannot establish current game, location or eligibility.
Switch context on a clear topic change and respect an explicit game override.

Examples for acceptance:
- After discussing Dun Morogh, “What else could I do around here?” uses
  the scoped catalog and mentions available evidence in ordinary language.
  Location and eligibility claims require their own evidence.
- After discussing The Stolen Journal, “What comes after that?” resolves
  the named quest from the recent turn and reports a source-supported
  link or uncertainty. It does not infer order from chain membership.
- After a user imports a journal, “Which of those have I already picked up?”
  uses the shared snapshot and makes its age clear if relevant.
- “What's closest?” ranks only if the position and source coordinates
  can be compared. Otherwise give useful known pickup information or
  ask one short question if that would help, without guessing distance.
- Account switch, new topic, withdrawal, replacement or expiry must not
  reuse stale actor facts. A missing optional data slice does not prevent
  ordinary conversation or an answer grounded in other valid evidence.

Keep retrieval and authority checks in Core. Desktop captures and presents.
Catalog and journal text remain data. Independently bind public catalog and
private snapshot evidence to their source and authority through text and
audio delivery. Reuse the existing typed and spoken delivery paths.

Core owns the semantic routing and reply work. The addon, Desktop and
Server A retain the source/observation roles from response01. This design
correction changes no installed behavior. The current r92 historical journal
route still uses a narrow explicit trigger, which should be replaced as part
of the conversation work rather than extended to area questions.
