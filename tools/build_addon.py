"""Test and package the Forever addon from its source and pinned quest catalog."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
from build_quest_catalog import SOURCE, catalog_lua

NAME = 'Alfador-wow-0.0.22-16001'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_immutable(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise RuntimeError('Existing build differs; create a new version instead of overwriting: ' + path.name)
    else:
        with path.open('xb') as stream:
            stream.write(data)


def main():
    addon = ROOT / 'addons' / 'Alfador-wow'
    paths = {f'Alfador-wow/{name}': addon / name
             for name in ('Alfador-wow.toc', 'Alfador.lua', 'QuestGuide.lua', 'README.md', 'DATA-NOTICE.md',
                          'Media/Alfador.tga', 'Media/Direction.tga', 'Media/Janus.tga')}
    paths['MANUAL-TEST.md'] = ROOT / 'docs' / 'ALFADOR-WOW-MANUAL-TEST.md'
    for path in SOURCE.rglob('*'):
        if path.is_file():
            paths[f'Polestar-source/reference_data/{SOURCE.name}/{path.relative_to(SOURCE).as_posix()}'] = path
    paths['Polestar-source/tools/build_quest_catalog.py'] = ROOT / 'tools/build_quest_catalog.py'
    payload = {name: path.read_bytes() for name, path in paths.items()}
    payload['Alfador-wow/QuestCatalog.lua'] = catalog_lua()
    toc = payload['Alfador-wow/Alfador-wow.toc'].decode('utf-8')
    if not re.search(r'^## Interface: 16001\s*$', toc, re.M):
        raise RuntimeError('Unexpected TOC interface')
    if not re.search(r'^## Version: 0\.0\.22\s*$', toc, re.M):
        raise RuntimeError('Unexpected addon version')
    test_groups = []
    for folder in ('tools', 'core_candidate', 'tests'):
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / folder),
                                 '-p', 'test_*.py'], cwd=ROOT.parent, capture_output=True, text=True)
        output = result.stdout + result.stderr
        if result.returncode:
            sys.stderr.write(output)
            raise RuntimeError('Failed test group: ' + folder)
        count = re.search(r'Ran (\d+) tests?', output)
        if not count or int(count.group(1)) == 0 or 'skipped=' in output:
            raise RuntimeError('Empty or skipped test group: ' + folder)
        test_groups.append({'group': folder, 'passed': int(count.group(1))})
    for name, path in paths.items():
        if payload[name] != path.read_bytes():
            raise RuntimeError('Source changed while testing: ' + name)
    # Test-only Lupa is pinned, local and excluded from the package.
    sys.path.insert(0, str(ROOT / '.builddeps'))
    import lupa
    from lupa.lua51 import LuaRuntime as Lua51
    from lupa.lua54 import LuaRuntime as Lua54
    if lupa.__version__ != '2.6':
        raise RuntimeError('Expected isolated test runtime lupa==2.6')
    manifest = {
        'artifactKind': 'forever-addon-source-candidate',
        'name': NAME, 'date': '2026-11-21',
        'target': {'game': 'wow-forever', 'version': '1.60.1', 'guideBuilds': ['70959', '71037'], 'historicalCaptureBuild': '70959', 'interface': 16001},
        'tests': test_groups, 'totalPassed': sum(item['passed'] for item in test_groups),
        'testRuntime': {'lupa': lupa.__version__, 'lua': [Lua51().lua_implementation, Lua54().lua_implementation]},
        'inGameAcceptance': 'not-performed', 'gameInstallationChanged': False,
        'coreDelivery': 'not-implemented', 'xpAndTiming': 'selected-quest-xp-needs-in-game-validation;timing-unavailable',
        'files': {name: {'sha256': sha(data), 'bytes': len(data)} for name, data in sorted(payload.items())},
    }
    manifest_bytes = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode('utf-8')
    payload['BUILD-MANIFEST.json'] = manifest_bytes
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 21, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            package.writestr(info, data)
    data = archive.getvalue()
    # Verify actual members and their contents, without extraction or Lua import.
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        if set(package.namelist()) != set(payload) or package.testzip() is not None:
            raise RuntimeError('Archive verification failed')
        for name, expected in payload.items():
            if package.read(name) != expected:
                raise RuntimeError('Archive content differs: ' + name)
    destination = ROOT / 'builds'
    destination.mkdir(exist_ok=True)
    write_immutable(destination / (NAME + '.zip'), data)
    write_immutable(destination / (NAME + '.manifest.json'), manifest_bytes)
    write_immutable(destination / (NAME + '.zip.sha256'), (sha(data) + '  ' + NAME + '.zip\n').encode('ascii'))
    print(json.dumps({'archive': str(destination / (NAME + '.zip')), 'sha256': sha(data),
                      'testsPassed': manifest['totalPassed'], 'inGameAcceptance': 'not-performed'}, indent=2))


if __name__ == '__main__':
    main()
