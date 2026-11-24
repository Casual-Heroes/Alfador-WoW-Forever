"""Offline Core-side candidate, NOT client policy or a deployed Core service.

Inputs represent already validated, character-bound evidence. This module does
not authenticate captures, fetch data, or infer permission from quest text.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Timing:
    travel_seconds: float | None
    objective_seconds: float | None
    turnin_seconds: float | None
    source: str
    progress_revision: str

    def total(self, revision):
        values = (self.travel_seconds, self.objective_seconds, self.turnin_seconds)
        if not self.source or self.progress_revision != revision:
            return None
        if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in values):
            return None
        total = sum(values)
        return total if 0 < total <= 86400 else None


@dataclass(frozen=True)
class Quest:
    quest_id: int
    zone_id: int
    subject: str
    revision: str
    required_level: int | None
    on_quest: bool | None
    turned_in: bool | None
    prerequisites_verified: bool
    reward_xp: int | None
    xp_source: str | None
    timing: Timing | None = None
    text: str = ''  # Untrusted content. Never interpreted as authority or instructions.


def compare_quests(quests, *, subject, zone_id, level, revision, budget_seconds=1200):
    """Compare 1-50 individual next quests, not a combined route.

    Timing must describe remaining travel/objectives/turn-in at this revision.
    XP must already be verified for this character/level/build by the resolver.
    A nonempty source field is provenance, not independent proof of verification.
    """
    if not 1 <= len(quests) <= 50 or len({q.quest_id for q in quests}) != len(quests):
        raise ValueError('one-to-fifty-distinct-quests-required')
    if (type(level) is not int or level < 1 or type(zone_id) is not int or zone_id < 1
            or not subject or not revision or type(budget_seconds) is not int or budget_seconds <= 0):
        raise ValueError('invalid-character-context')
    rows, excluded = [], []
    for quest in quests:
        reason = None
        if type(quest.quest_id) is not int or quest.quest_id <= 0:
            raise ValueError('invalid-quest-id')
        if quest.subject != subject or quest.revision != revision:
            reason = 'character-or-revision-mismatch'
        elif quest.zone_id != zone_id:
            reason = 'outside-current-zone'
        elif type(quest.required_level) is not int or quest.required_level < 1:
            reason = 'level-requirement-unknown'
        elif quest.required_level > level:
            reason = 'level-too-low'
        elif quest.on_quest is not True or quest.turned_in is not False or quest.prerequisites_verified is not True:
            reason = 'eligibility-not-established'
        if reason:
            excluded.append({'questId': quest.quest_id, 'reason': reason})
            continue
        xp = quest.reward_xp
        xp_known = type(xp) is int and xp >= 0 and bool(quest.xp_source)
        total = quest.timing.total(revision) if quest.timing is not None else None
        rows.append({'questId': quest.quest_id, 'rewardXP': xp if xp_known else None,
                     'estimatedSeconds': total,
                     'estimatedXPPerMinute': xp * 60 / total if xp_known and total is not None else None,
                     'fitsBudget': total <= budget_seconds if total is not None else None})
    result = {'basis': 'single-quest-remaining-time', 'zoneId': zone_id,
              'budgetSeconds': budget_seconds, 'revision': revision,
              'candidates': rows, 'excluded': excluded, 'recommendedQuestIds': []}
    if not rows:
        return dict(result, status='no-eligible-evidence', explanation='No eligible quest was established.')
    if any(row['rewardXP'] is None for row in rows):
        return dict(result, status='xp-unavailable', explanation='Verified character-specific quest XP is missing; no rate ranking.')
    if any(row['estimatedSeconds'] is None for row in rows):
        # Compare only XP, explicitly declining a speed/budget claim for either.
        for row in rows:
            row['estimatedXPPerMinute'] = None
        return dict(result, status='xp-only', explanation='Compare quest XP only; I cannot yet tell which is faster.')
    fitting = [row for row in rows if row['fitsBudget']]
    if not fitting:
        return dict(result, status='none-fit', explanation='No evaluated remaining quest is estimated to fit the available time.')
    best = max(row['estimatedXPPerMinute'] for row in fitting)
    result['recommendedQuestIds'] = [row['questId'] for row in fitting
                                    if math.isclose(row['estimatedXPPerMinute'], best, rel_tol=1e-9)]
    return dict(result, status='estimated-rate-comparison',
                explanation='Best estimated quest reward XP/min among evaluated eligible quests that fit; not a full leveling route.')
