"""Synthetic server-boundary demonstration; not QuestLog/Core enforcement.

The registry must be replaced by actual verified-session/permission integration.
Only this synthetic harness can create these session records. No network or
upstream credentials are implemented, accepted from requests, or stored here.
"""
from dataclasses import dataclass


@dataclass
class ServerSession:
    subject: str
    zone_id: int
    quest_ids: frozenset[int]
    expires_at: float
    verified: bool = True
    revoked: bool = False
    scope: str = 'wow.forever.quest.read'


class AccessDenied(ValueError):
    pass


class SyntheticGateway:
    def __init__(self, sessions, lookup, now):
        self.sessions = sessions  # Trusted server state in the synthetic demo.
        self.lookup = lookup      # Fixed quest-read callback, never a request URL.
        self.now = now
        self.audit = []           # In-memory demo events, not production audit storage.

    def _authorize(self, token, operation, zone_id, quest_id):
        session = self.sessions.get(token)
        if not session or not session.verified:
            raise AccessDenied('session-unverified')
        if session.revoked:
            raise AccessDenied('session-revoked')
        if session.expires_at <= self.now():
            raise AccessDenied('session-expired')
        if operation != 'wow.forever.quest.read' or session.scope != operation:
            raise AccessDenied('outside-wow-read-scope')
        if type(zone_id) is not int or type(quest_id) is not int or zone_id != session.zone_id or quest_id not in session.quest_ids:
            raise AccessDenied('outside-pilot-zone-or-quests')
        return session

    def read_quest(self, *, token, operation, zone_id, quest_id):
        started = False
        try:
            session = self._authorize(token, operation, zone_id, quest_id)
            subject = session.subject
            started = True
            result = self.lookup(subject, zone_id, quest_id)
            # Re-check so revocation during the lookup prevents data delivery.
            session = self._authorize(token, operation, zone_id, quest_id)
            if session.subject != subject:
                raise AccessDenied('session-binding-changed')
        except AccessDenied as error:
            self.audit.append({'decision': 'denied', 'reason': str(error),
                               'downstreamStarted': started, 'responseDelivered': False})
            raise
        except Exception:
            self.audit.append({'decision': 'failed', 'reason': 'upstream-failed',
                               'downstreamStarted': started, 'responseDelivered': False})
            raise
        self.audit.append({'decision': 'allowed', 'reason': 'scoped-quest-read',
                           'downstreamStarted': True, 'responseDelivered': True})
        return result  # Text in this data cannot create or expand a session.
