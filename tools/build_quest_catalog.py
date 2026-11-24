"""Generate the bundled local index from the pinned Polestar tables."""
import hashlib
import json
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'reference_data/polestar-forever-db-2026.11.1'
NEARBY_MAPS = {1426, 1429, 1455}  # Dun Morogh, Elwynn Forest, Ironforge
STORY = {
    35: 'Goldshire sends you to the Westbrook garrison to learn what is threatening Elwynn’s roads.',
    40: 'Remy Two Times sends you to Marshal Dughan. It connects Goldshire to the trouble at Westbrook.',
    182: 'The Frostmane trolls threaten Coldridge Valley. This quest introduces the conflict that continues in The Stolen Journal.',
    218: 'Recover Grelin Whitebeard’s journal from the Frostmane trolls. It continues the Coldridge Valley story after The Troll Cave.',
}


def lua_text(text):
    # Decimal byte escapes preserve UTF-8 and prevent data from becoming Lua code.
    return '"' + ''.join(
        chr(byte) if 32 <= byte < 127 and byte not in (34, 92) else f'\\{byte:03d}'
        for byte in text.encode('utf-8')
    ) + '"'


def catalog_lua():
    manifest = json.loads((SOURCE / 'datapackage.json').read_bytes())
    index = json.loads((SOURCE / 'index.json').read_bytes())
    tables = {}
    for resource in manifest['resources']:
        raw = (SOURCE / resource['path']).read_bytes()
        if f"sha256:{hashlib.sha256(raw).hexdigest()}" != resource['hash']:
            raise ValueError(f"Polestar table changed: {resource['name']}")
        tables[resource['name']] = [json.loads(line) for line in raw.splitlines()]
        if len(tables[resource['name']]) != index['counts'][resource['name']]:
            raise ValueError(f"Polestar row count changed: {resource['name']}")

    names = {
        kind: {row['id']: row.get('name') for row in tables[kind]}
        for kind in ('npc', 'object', 'item')
    }
    links = {}
    for table, field in [('quest_start', 'pickup'), ('quest_end', 'turnin')]:
        for row in tables[table]:
            name = names.get(row['kind'], {}).get(row['id'])
            if name:
                links.setdefault(row['quest'], {}).setdefault(field, set()).add(name)

    # Candidate pickup zones come from the starter's spawn, not the quest's
    # objective area. A map envelope is approximate and maps can overlap.
    starter_maps = {}
    starter_points = {}
    pickup_frames = {}
    maps_by_world = {}
    for frame in tables['ui_map']:
        maps_by_world.setdefault(frame['map'], []).append(frame)
        if frame['ui_map'] in NEARBY_MAPS:
            if frame['ui_map'] in pickup_frames:
                raise ValueError('Multiple coordinate frames for a nearby pilot map')
            pickup_frames[frame['ui_map']] = frame
    for point in tables['spawn']:
        if point['kind'] not in ('npc', 'object'):
            continue
        for frame in maps_by_world.get(point['map'], []):
            if (min(frame['top'], frame['bottom']) <= point['x'] <= max(frame['top'], frame['bottom'])
                    and min(frame['left'], frame['right']) <= point['y'] <= max(frame['left'], frame['right'])):
                starter_maps.setdefault((point['kind'], point['id']), set()).add(frame['ui_map'])
                if frame['ui_map'] in pickup_frames:
                    x = (point['y'] - frame['left']) / (frame['right'] - frame['left'])
                    y = (point['x'] - frame['top']) / (frame['bottom'] - frame['top'])
                    name = names[point['kind']].get(point['id'])
                    if name:
                        key = (point['kind'], point['id'], frame['ui_map'])
                        starter_points.setdefault(key, set()).add((round(x, 6), round(y, 6), name))
    by_map = {}
    points_by_map = {map_id: {} for map_id in pickup_frames}
    for row in tables['quest_start']:
        for map_id in starter_maps.get((row['kind'], row['id']), ()):
            by_map.setdefault(map_id, set()).add(row['quest'])
            points = starter_points.get((row['kind'], row['id'], map_id))
            if points:
                points_by_map[map_id].setdefault(row['quest'], set()).update(points)

    turnin_points = {map_id: {} for map_id in pickup_frames}
    for row in tables['quest_end']:
        for map_id in turnin_points:
            points = starter_points.get((row['kind'], row['id'], map_id))
            if points:
                turnin_points[map_id].setdefault(row['quest'], set()).update(points)

    item_sources = {}
    for row in tables['item_source']:
        if row['kind'] in ('npc', 'object'):
            item_sources.setdefault(row['item'], set()).add((row['kind'], row['id']))

    objectives = {}
    for row in tables['quest_objective']:
        kind, target = row['kind'], row.get('target')
        source_kind = {'kill': 'npc', 'talk': 'npc', 'object': 'object'}.get(kind)
        name_kind = 'item' if kind == 'item' else source_kind
        sources = item_sources.get(target, ()) if kind == 'item' else [(source_kind, target)]
        name = names.get(name_kind, {}).get(target)
        mapped = {}
        if name:
            for map_id in pickup_frames:
                points = set().union(*(starter_points.get((src_kind, src_id, map_id), set())
                                       for src_kind, src_id in sources))
                if points:
                    mapped[map_id] = points
        objectives.setdefault(row['quest'], {})[row['n']] = (kind, name, row.get('count'), mapped)

    prereqs = {}
    successors = {}
    for row in tables['quest_prereq']:
        # Breadcrumbs and alternative groups do not establish a single lock.
        entry = prereqs.setdefault(row['quest'], {'all': set(), 'any': set()})
        if not row.get('breadcrumb') and row['mode'] == 'all':
            entry['all'].add(row['pre'])
        else:
            entry['any'].add(row['pre'])
        successors.setdefault(row['pre'], {}).setdefault(row['quest'], set()).add(
            'breadcrumb' if row.get('breadcrumb') else row['mode'])

    for reward in tables['quest_reward']:
        kind = reward['kind']
        name = names['item'].get(reward['id'])
        if kind in ('item', 'choice') and name:
            count = reward.get('count', 1)
            text = f'{count} × {name}' if count > 1 else name
            links.setdefault(reward['quest'], {}).setdefault(kind, set()).add(text)

    lines = [
        '-- Generated from Polestar forever-db 2026.11.1. See DATA-NOTICE.md.',
        'local _, addon = ...',
        'addon.catalog = {',
    ]
    quests = tables['quest']
    if len({quest['id'] for quest in quests}) != len(quests):
        raise ValueError('Duplicate quest ID')
    for quest in quests:
        info = links.get(quest['id'], {})
        fields = {}
        if quest.get('title'):
            fields['title'] = quest['title']
        for name, values in info.items():
            fields[name] = ', '.join(sorted(values))
        values = [f'{key}={lua_text(value)}' for key, value in sorted(fields.items())]
        for key in ('min_level', 'side', 'races', 'classes', 'xp', 'money_copper'):
            if key in quest:
                values.append(f'{key}={quest[key]}')
        if 'repeatable' in quest:
            values.append('repeatable=' + str(quest['repeatable']).lower())
        if quest['id'] in STORY:
            values.append('story=' + lua_text(STORY[quest['id']]))
        if quest['id'] in successors:
            ordered = sorted(successors[quest['id']].items())
            values.append('next={' + ','.join(
                f'{{{quest_id},{lua_text("/".join(sorted(modes)))}}}' for quest_id, modes in ordered) + '}')
        requirements = prereqs.get(quest['id'])
        if requirements:
            if requirements['all']:
                values.append('requires={' + ','.join(map(str, sorted(requirements['all']))) + '}')
            if requirements['any']:
                values.append('complex_prereq=true')
        lines.append(f"    [{quest['id']}] = {{{', '.join(values)}}},")
    lines.append('}')
    lines.append('addon.pickupsByMap = {')
    catalog_ids = {quest['id'] for quest in quests}
    for map_id, ids in sorted(by_map.items()):
        lines.append(f'    [{map_id}] = {{' + ','.join(map(str, sorted(ids & catalog_ids))) + '},')
    lines.append('}')
    lines.append('addon.pickupFrames = {')
    for map_id, frame in sorted(pickup_frames.items()):
        corners = ','.join(str(frame[key]) for key in ('map', 'top', 'left', 'bottom', 'right'))
        lines.append(f'    [{map_id}] = {{{corners}}},')
    lines.append('}')
    def lua_points(points):
        return '{' + ','.join(f'{{{x},{y},{lua_text(name)}}}' for x, y, name in sorted(points)) + '}'

    for name, maps in [('pickupPoints', points_by_map), ('turninPoints', turnin_points)]:
        lines.append(f'addon.{name} = {{')
        for map_id, quests in sorted(maps.items()):
            lines.append(f'    [{map_id}] = {{')
            for quest_id, points in sorted(quests.items()):
                if quest_id in catalog_ids:
                    lines.append(f'        [{quest_id}] = {lua_points(points)},')
            lines.append('    },')
        lines.append('}')

    lines.append('addon.routeObjectives = {')
    for quest_id, entries in sorted(objectives.items()):
        if quest_id not in catalog_ids or not any(entry[3] for entry in entries.values()):
            continue
        lines.append(f'    [{quest_id}] = {{')
        for n, (kind, name, count, maps) in sorted(entries.items()):
            points = ','.join(f'[{map_id}]={lua_points(values)}' for map_id, values in sorted(maps.items()))
            label = lua_text(name) if name else 'false'
            lines.append(f'        [{n}] = {{{lua_text(kind)},{label},{count or "false"},{{{points}}}}},')
        lines.append('    },')
    lines.append('}')
    return ('\n'.join(lines) + '\n').encode('utf-8')
