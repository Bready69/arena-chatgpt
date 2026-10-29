#!/usr/bin/env python3
"""Local structural checks; this is not the host's server-side validator."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import math
import re
import stat
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
import yaml


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, limit, name, single_line=False):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= limit, f'Invalid {name}')
    require(not any(unicodedata.category(c) in ('Cc', 'Cf', 'Zl', 'Zp') and c not in ('\n', '\r', '\t') for c in value), f'Unsupported text in {name}')
    if single_line:
        require('\n' not in value and '\r' not in value, f'{name} must be one line')


def validate(path):
    require(path.stat().st_size <= 100 * 1024**2, 'ZIP exceeds compressed size limit')
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        require(bool(infos) and len(infos) <= 5000, 'Invalid archive entry count')
        require(sum(i.file_size for i in infos) <= 512 * 1024**2, 'Archive expands beyond size limit')
        seen = set()
        files = {}
        for info in infos:
            name = info.filename
            plain = name.rstrip('/')
            parts = plain.split('/')
            require(plain and plain == plain.strip() and not plain.startswith('/') and '\\' not in plain, 'Unsafe path')
            require(len(parts) <= 20 and all(p not in ('', '.', '..') for p in parts), 'Unsafe path segment')
            normalized = unicodedata.normalize('NFC', plain).casefold()
            require(normalized not in seen, 'Duplicate or normalization-colliding path')
            seen.add(normalized)
            require(not info.flag_bits & 1, 'Encrypted entries are unsupported')
            require(info.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED), 'Unsupported compression')
            require(info.file_size <= 100 * 1024**2, 'Entry too large')
            require(stat.S_IFMT(info.external_attr >> 16) in (stat.S_IFREG, stat.S_IFDIR), 'Special archive member')
            if not info.is_dir():
                files[name] = archive.read(info)
        require(archive.testzip() is None, 'ZIP integrity failure')
        require('.codex-plugin/plugin.json' in files and 'plugin.json' not in files, 'Expected one root compatibility manifest')
        require(not any('/.codex-plugin/plugin.json' in name for name in files), 'Nested plugin root')
        require(not any('.arena' in PurePosixPath(name).parts or '__pycache__' in name or name.endswith(('.pyc', '.pyo')) for name in files), 'Private/generated files included')
        manifest = json.loads(files['.codex-plugin/plugin.json'])
        require(isinstance(manifest, dict), 'Manifest must be an object')
        require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', manifest.get('name', '')), 'Invalid plugin name')
        require(re.fullmatch(r'\d+\.\d+\.\d+', manifest.get('version', '')), 'Invalid release version')
        text(manifest.get('description'), 1024, 'description')
        text(manifest.get('author', {}).get('name'), 120, 'author.name')
        require(manifest.get('skills') == './skills/', 'Unsupported skills path')
        require('apps' not in manifest and 'mcpServers' not in manifest, 'Unexpected server binding')
        interface = manifest.get('interface', {})
        for key, limit in [('displayName', 30), ('shortDescription', 30), ('longDescription', 4000), ('developerName', 80)]:
            text(interface.get(key), limit, key, key != 'longDescription')
        require(interface.get('category') == 'Productivity', 'Unexpected category')
        prompts = interface.get('defaultPrompt', [])
        prompts = [prompts] if isinstance(prompts, str) else prompts
        require(isinstance(prompts, list) and 0 < len(prompts) <= 3, 'Invalid prompt list')
        for prompt in prompts:
            text(prompt, 128, 'defaultPrompt', True)
        capabilities = interface.get('capabilities', [])
        require(isinstance(capabilities, list) and len(capabilities) <= 20, 'Invalid capabilities')
        for capability in capabilities:
            text(capability, 120, 'capability', True)

        def image(name, base=''):
            require(isinstance(name, str) and name.startswith('./') and '..' not in PurePosixPath(name).parts, 'Invalid asset path')
            full = base + name[2:]
            require(full in files and len(files[full]) <= 5 * 1024**2, 'Missing or oversized image')
            require(full.endswith('.svg'), 'This package validator expects the included SVG branding')
            svg = ET.fromstring(files[full])
            require(svg.tag == '{http://www.w3.org/2000/svg}svg', 'Invalid SVG')
            values = [float(v) for v in svg.attrib['viewBox'].split()]
            require(len(values) == 4 and all(math.isfinite(v) for v in values), 'Invalid SVG viewBox')
            require(48 <= values[2] == values[3] <= 4096, 'Image must be square and at least 48px')
            require(float(svg.attrib['width']) == float(svg.attrib['height']) >= 48, 'Invalid SVG dimensions')

        image(interface.get('composerIcon'))
        image(interface.get('logo'))
        skill_names = set()
        skill_paths = [p for p in files if p.startswith('skills/') and p.endswith('/SKILL.md')]
        require(bool(skill_paths), 'No skill present')
        for skill_path in skill_paths:
            require(len(PurePosixPath(skill_path).parts) == 3, 'Nested skill')
            content = files[skill_path].decode('utf-8')
            require(content.startswith('---\n'), 'Missing skill frontmatter')
            sections = content.split('---', 2)
            require(len(sections) == 3 and bool(sections[2].strip()), 'Missing skill body')
            meta = yaml.safe_load(sections[1])
            require(isinstance(meta, dict), 'Skill metadata must be a mapping')
            text(meta.get('name'), 64, 'skill name')
            text(meta.get('description'), 1024, 'skill description')
            require(meta['name'] not in skill_names, 'Duplicate skill identity')
            skill_names.add(meta['name'])
            require(len(manifest['name'] + ':' + meta['name']) <= 64, 'Skill identity too long')
            base = skill_path.rsplit('/', 1)[0] + '/'
            metadata = yaml.safe_load(files[base + 'agents/openai.yaml'])
            require(isinstance(metadata, dict) and isinstance(metadata.get('interface'), dict), 'Missing skill interface')
            si = metadata['interface']
            text(si.get('display_name'), 80, 'skill display_name')
            text(si.get('short_description'), 240, 'skill short_description')
            policy = metadata.get('policy', {})
            require(isinstance(policy, dict) and set(policy) <= {'products', 'allow_implicit_invocation'}, 'Invalid skill policy')
            if 'products' in policy:
                require(isinstance(policy['products'], list) and set(policy['products']) <= {'CHAT', 'CODEX'}, 'Unsupported policy products')
            if 'allow_implicit_invocation' in policy:
                require(isinstance(policy['allow_implicit_invocation'], bool), 'Invalid implicit invocation flag')
            for key in ('icon_small', 'icon_large'):
                if key in si:
                    image(si[key], base)
        for name in ('scripts/bracket.py', 'scripts/strategies.json', 'references/prompt-templates.md', 'references/rubric.md', 'references/runtime.md'):
            require('skills/arena/' + name in files, f'Missing tournament component: {name}')
        deck = json.loads(files['skills/arena/scripts/strategies.json'])
        require(math.prod(len(deck[k]) for k in ('reasoning', 'workflows', 'strategies')) == 2160, 'Unexpected strategy deck')
        require(b'Copyright (c) 2026 Jake Schincariol' in files.get('LICENSE', b''), 'Missing upstream copyright')
        checksums = {}
        for line in files['SHA256SUMS.txt'].decode().splitlines():
            digest, name = line.split('  ', 1)
            require(name in files and name not in checksums, 'Invalid checksum path')
            checksums[name] = digest
            require(hashlib.sha256(files[name]).hexdigest() == digest, f'Checksum mismatch: {name}')
        require(set(checksums) == set(files) - {'SHA256SUMS.txt'}, 'Incomplete checksum manifest')
    print(f'Package checks passed: {manifest["name"]} {manifest["version"]}, {len(skill_paths)} skill(s), {len(files)} files')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    try:
        validate(args.archive)
    except (ValueError, KeyError, TypeError, ET.ParseError, zipfile.BadZipFile) as exc:
        parser.exit(1, f'Package check failed: {exc}\n')
