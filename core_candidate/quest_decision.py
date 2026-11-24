"""Isolated Core-side WoW Forever decision logic. No I/O or transport."""
from dataclasses import dataclass
from math import dist, isfinite

from quest_pilot import Timing


@dataclass(frozen=True)
class Point:
    """Planar yards in a verified map space, with optional UI map percentages."""
    map_id: int
    space: str
    x: float
    y: float
    map_percent: tuple[float, float] | None = None


@dataclass(frozen=True)
class Weapon:
    name: str
    slot: str
    hands: int
    damage_per_second: float | None = None
    usable: bool | None = None


@dataclass(frozen=True)
class Pickup:
    quest_id: int
    name: str
    giver: str
    pickup: Point
    listed_xp: int | None
    source: str
    build: str
    turnin: Point | None = None
    turnin_giver: str | None = None
    delivery: bool = False
    minimum_level: int | None = None
    faction: str | None = None
    follow_up_to: tuple[int, ...] = ()
    story: str | None = None
    weapons: tuple[Weapon, ...] = ()
    rewards: tuple[str, ...] = ()
    story_kind: str = 'unknown'


@dataclass(frozen=True)
class JournalStop:
    quest_id: int
    name: str
    point: Point
    unfinished: bool


@dataclass(frozen=True)
class QuestMeasurement:
    quest_id: int
    timing: Timing
    effective_xp: int | None = None
    xp_source: str | None = None


@dataclass(frozen=True)
class Observation:
    actor: str
    character: str
    build: str
    sampled_at: float
    position: Point
    level: int
    faction: str
    offers: frozenset[tuple[int, str]] = frozenset()
    active: frozenset[int] = frozenset()
    completed: frozenset[int] = frozenset()
    journal_stops: tuple[JournalStop, ...] = ()
    equipped_weapon: Weapon | None = None
    progress_revision: str | None = None
    measurements: tuple[QuestMeasurement, ...] = ()


def _same_space(first: Point, second: Point) -> bool:
    return (first.map_id == second.map_id and first.space == second.space
            and all(isfinite(value) for value in (first.x, first.y, second.x, second.y)))


def _distance(first: Point, second: Point) -> float | None:
    if _same_space(first, second):
        return dist((first.x, first.y), (second.x, second.y))
    return None


def _detours(observation: Observation, start: Point, end: Point) -> list[dict]:
    vx, vy = end.x - start.x, end.y - start.y
    length_squared = vx * vx + vy * vy
    if length_squared < 50 ** 2:
        return []
    best = {}
    for stop in observation.journal_stops:
        if (not stop.unfinished or stop.quest_id not in observation.active
                or stop.quest_id in observation.completed or not _same_space(start, stop.point)):
            continue
        px, py = stop.point.x - start.x, stop.point.y - start.y
        along = (px * vx + py * vy) / length_squared
        if not 0 <= along <= 1:
            continue
        offset = dist((px, py), (along * vx, along * vy))
        if offset <= 125 and (stop.quest_id not in best or offset < best[stop.quest_id][0]):
            best[stop.quest_id] = offset, stop
    nearest = sorted(best.values(), key=lambda row: (row[0], row[1].quest_id))[:3]
    return [{'quest_id': stop.quest_id, 'name': stop.name, 'off_direct_line_yards': round(offset),
             'map_percent': stop.point.map_percent}
            for offset, stop in nearest]


def _weapon_choices(rewards: tuple[Weapon, ...], equipped: Weapon | None) -> list[dict]:
    choices = []
    for reward in rewards:
        delta = None
        if (equipped and reward.usable is True and reward.slot == equipped.slot and reward.hands == equipped.hands
                and reward.damage_per_second is not None and equipped.damage_per_second is not None
                and all(isfinite(value) and value > 0
                        for value in (reward.damage_per_second, equipped.damage_per_second))):
            delta = round(reward.damage_per_second - equipped.damage_per_second, 2)
        choices.append({'name': reward.name, 'usable': reward.usable, 'weapon_dps_delta': delta})
    return choices


def decide_pickup(pickups: tuple[Pickup, ...], observation: Observation, *, actor: str, character: str,
                  build: str, now: float, focus: str = 'leveling', quest_id: int | None = None,
                  budget_seconds: int | None = None) -> dict:
    """Return explanation facts for an already authorized, typed observation.

    The caller supplies Core's authenticated actor, character and clock. This
    helper does not authenticate, admit or send observations.
    """
    if focus not in {'leveling', 'nearby', 'rewards', 'weapon', 'story', 'side'}:
        raise ValueError('Unsupported quest focus')
    if budget_seconds is not None and (type(budget_seconds) is not int or budget_seconds <= 0):
        raise ValueError('Time budget must be positive seconds')
    if (not actor or not character or observation.actor != actor or observation.character != character
            or observation.build != build or not isfinite(now) or not isfinite(observation.sampled_at)
            or not 0 <= now - observation.sampled_at <= 15):
        return {'status': 'current observation unavailable', 'recommendation': None}

    ranked = []
    measurements = {entry.quest_id: entry for entry in observation.measurements}
    over_budget = False
    for quest in pickups:
        if (quest.build != build or (quest_id is not None and quest_id != quest.quest_id)
                or quest.quest_id in observation.active or quest.quest_id in observation.completed
                or (quest.minimum_level is not None and observation.level < quest.minimum_level)
                or (quest.faction is not None and observation.faction != quest.faction)):
            continue
        pickup_distance = _distance(observation.position, quest.pickup)
        if pickup_distance is None or pickup_distance > 1200:
            continue
        offered = (quest.quest_id, quest.giver) in observation.offers
        follow_up = sorted(observation.completed.intersection(quest.follow_up_to))
        delivery_distance = (_distance(quest.pickup, quest.turnin)
                             if quest.delivery and quest.turnin else None)
        detours = _detours(observation, quest.pickup, quest.turnin) if delivery_distance is not None else []
        weapons = _weapon_choices(quest.weapons, observation.equipped_weapon)
        gain = max((item['weapon_dps_delta'] or 0 for item in weapons), default=0)
        measurement = measurements.get(quest.quest_id)
        if not (measurement and observation.progress_revision
                and measurement.timing.progress_revision == observation.progress_revision):
            measurement = None
        timing = measurement.timing if measurement and measurement.timing.source else None
        duration = timing.total(observation.progress_revision) if timing else None
        travel = timing.travel_seconds if timing else None
        if type(travel) not in (int, float) or not isfinite(travel) or not 0 <= travel <= 86400:
            travel = None
        xp = measurement.effective_xp if (measurement and measurement.xp_source
                                          and type(measurement.effective_xp) is int
                                          and measurement.effective_xp >= 0) else None
        rate = xp * 60 / duration if xp is not None and duration is not None else None
        fits = (duration <= budget_seconds if duration is not None and budget_seconds is not None else None)
        if fits is False:
            over_budget = True
            continue
        distance_cost = pickup_distance + (delivery_distance if delivery_distance is not None else 1200)
        proximity_score = (quest.listed_xp or 0) / (500 + distance_cost)
        story_kind = quest.story_kind if quest.story_kind in {'story', 'side'} else 'unknown'
        has_story = story_kind == 'story' or (story_kind == 'unknown' and bool(quest.story))
        story_score = 0.10 if has_story else 0
        weapon_score = min(0.5, max(0, gain))
        score = proximity_score + story_score + weapon_score + bool(follow_up) + bool(detours)
        if focus == 'nearby':
            priority = (travel is not None, -(travel if travel is not None else pickup_distance), score)
            basis = 'estimated travel time' if travel is not None else 'straight-line pickup distance'
        elif focus == 'story':
            priority = (has_story, 0, score)
            basis = 'sourced story relevance' if has_story else 'catalog leads without a confirmed story match'
        elif focus == 'side':
            priority = (story_kind == 'side', 0, score)
            basis = 'sourced side quest' if story_kind == 'side' else 'catalog leads without a confirmed side quest match'
        elif focus in {'rewards', 'weapon'}:
            options = len(weapons) + (len(quest.rewards) if focus == 'rewards' else 0)
            priority = (gain > 0, gain if gain > 0 else bool(options), score)
            basis = 'comparable weapon DPS' if gain > 0 else 'listed reward choices and proximity'
        else:
            priority = (rate is not None, rate or 0, score)
            basis = 'estimated XP per minute' if rate is not None else 'listed XP and proximity'
        recommendation = {
            'quest_id': quest.quest_id, 'quest': quest.name, 'quest_giver': quest.giver,
            'instruction': 'pick up' if offered else 'check with quest giver', 'confirmed_offer': offered,
            'catalog_source': quest.source, 'listed_xp': quest.listed_xp, 'chain_from_ids': follow_up,
            'pickup_yards_straight_line': round(pickup_distance), 'turnin_giver': quest.turnin_giver,
            'map_id': quest.pickup.map_id, 'pickup_map_percent': quest.pickup.map_percent,
            'turnin_map_percent': quest.turnin.map_percent if delivery_distance is not None else None,
            'delivery_yards_straight_line': round(delivery_distance) if delivery_distance is not None else None,
            'comparison_basis': basis, 'effective_xp': xp, 'effective_xp_source': measurement.xp_source if xp is not None else None,
            'travel_time_seconds': travel, 'completion_time_seconds': duration, 'xp_per_minute': rate,
            'fits_time_budget': fits, 'timing_source': timing.source if travel is not None or duration is not None else None,
            'possible_stops': detours, 'story_kind': story_kind, 'story_reason': quest.story,
            'reward_choices': list(quest.rewards), 'weapon_choices': weapons,
            'equipped_weapon': observation.equipped_weapon.name if observation.equipped_weapon else None,
        }
        ranked.append((fits is True, offered, *priority, -pickup_distance, -quest.quest_id, recommendation))
    ranked.sort(key=lambda row: row[:-1], reverse=True)
    chosen = ranked[0][-1] if ranked else None
    status = 'recommendation available' if chosen else 'no supported pickup'
    if not chosen and over_budget:
        status = 'no estimated pickup fits the time budget'
    return {'status': status, 'focus': focus, 'time_budget_seconds': budget_seconds,
            'timing_coverage': ('complete' if all(row[-1]['completion_time_seconds'] is not None for row in ranked)
                                else 'partial') if ranked else 'unavailable',
            'rate_coverage': ('complete' if all(row[-1]['xp_per_minute'] is not None for row in ranked)
                              else 'partial') if ranked else 'unavailable',
            'recommendation': chosen, 'alternatives': [row[-1] for row in ranked[1:3]]}


def render_pickup_advice(result: dict) -> str:
    """Render the evidence after Core has resolved the user's goal and quest."""
    quest = result['recommendation']
    if not quest:
        return {
            'current observation unavailable': 'Where are you standing now? I need your current location to compare pickups.',
            'no estimated pickup fits the time budget': 'The quests I could time are estimated to take longer than you have.',
        }.get(result['status'], 'I don’t have a supported pickup for this choice at your location.')

    name, giver = quest['quest'], quest['quest_giver']
    first = f'Pick up {name} from {giver}' if quest['confirmed_offer'] else f'Check with {giver} for {name}'
    if quest['pickup_map_percent']:
        x, y = quest['pickup_map_percent']
        first += f' ({x:.1f}, {y:.1f})'
    sentences = [first + '.']
    if quest['listed_xp'] is not None:
        sentences.append(f"Polestar lists {quest['listed_xp']:,} XP." if quest['catalog_source'].startswith('Polestar')
                         else f"The catalog lists {quest['listed_xp']:,} XP.")
    if quest['pickup_yards_straight_line'] > 0:
        sentences.append(f"The pickup is about {quest['pickup_yards_straight_line']:,} yards straight-line from you.")
    if quest['delivery_yards_straight_line'] is not None and quest['turnin_giver']:
        sentences.append(f"Turn it in to {quest['turnin_giver']}, about {quest['delivery_yards_straight_line']:,} yards "
                         'straight-line from the pickup.')
    if quest['travel_time_seconds'] is not None and result['focus'] == 'nearby':
        sentences.append(f"Estimated travel is {quest['travel_time_seconds'] / 60:.1f} minutes.")
    if quest['completion_time_seconds'] is not None:
        sentences.append(f"Estimated completion is {quest['completion_time_seconds'] / 60:.1f} minutes.")
    elif result['time_budget_seconds'] or result['focus'] == 'leveling':
        sentences.append('I still need objective and travel timing to compare completion speed.'
                         if quest['travel_time_seconds'] is None else
                         'I have a travel estimate, but the full quest timing is still unknown.')
    if quest['xp_per_minute'] is not None and result['focus'] == 'leveling':
        qualifier = ' among quests with comparable timing and XP' if result['rate_coverage'] != 'complete' else ''
        sentences.append(f"That’s about {quest['xp_per_minute']:.0f} XP per minute{qualifier}.")
    if quest['story_reason'] and result['focus'] in {'story', 'side'}:
        sentences.append(quest['story_reason'])
    elif quest['chain_from_ids'] and result['focus'] == 'story':
        sentences.append('The catalog connects it to a quest you completed.')
    elif result['focus'] == 'side' and quest['story_kind'] == 'side':
        sentences.append('The source identifies this as a side quest.')
    if result['focus'] in {'weapon', 'rewards'}:
        choices = quest['reward_choices'] + [weapon['name'] for weapon in quest['weapon_choices']]
        if choices:
            sentences.append('Listed rewards include ' + ', '.join(choices) + '.')
        upgrades = [weapon for weapon in quest['weapon_choices'] if (weapon['weapon_dps_delta'] or 0) > 0]
        if upgrades:
            best = max(upgrades, key=lambda weapon: weapon['weapon_dps_delta'])
            sentences.append(f"{best['name']} shows {best['weapon_dps_delta']:g} more weapon DPS than "
                             f"{quest['equipped_weapon']}.")
        elif quest['weapon_choices']:
            sentences.append('I can’t confirm a weapon upgrade from this evidence.')
    if quest['possible_stops']:
        stop = quest['possible_stops'][0]
        sentences.append(f"Your journal still shows an unfinished objective for {stop['name']} near the direct line.")
    return ' '.join(sentences)
