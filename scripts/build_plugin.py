#!/usr/bin/env python3
"""Build a reproducible plugin ZIP without private records or repository metadata."""
from pathlib import Path
import hashlib
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'dist' / 'Arena-ChatGPT-Plugin.zip'
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def package_files():
    paths = [ROOT / 'LICENSE', ROOT / 'README.md']
    for directory in ('.codex-plugin', 'assets', 'skills'):
        for path in (ROOT / directory).rglob('*'):
            if path.is_symlink():
                raise ValueError(f'Symlink is not allowed: {path.relative_to(ROOT)}')
            if path.is_file() and '__pycache__' not in path.parts and path.suffix not in ('.pyc', '.pyo'):
                paths.append(path)
    return sorted(paths, key=lambda p: p.relative_to(ROOT).as_posix())


def main():
    files = package_files()
    checksum = ROOT / 'SHA256SUMS.txt'
    checksum.write_text(''.join(
        hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.relative_to(ROOT).as_posix() + '\n'
        for path in files
    ), encoding='utf-8', newline='\n')
    files = sorted(files + [checksum], key=lambda p: p.relative_to(ROOT).as_posix())
    directories = set()
    for path in files:
        parent = path.relative_to(ROOT).parent
        while parent != Path('.'):
            directories.add(parent.as_posix() + '/')
            parent = parent.parent
    entries = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in files}
    entries.update({directory: b'' for directory in directories})
    OUTPUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUTPUT, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=FIXED_TIME)
            info.create_system = 3
            mode = (stat.S_IFDIR | 0o755) if name.endswith('/') else (stat.S_IFREG | 0o644)
            info.external_attr = mode << 16
            if name.endswith('/'):
                info.external_attr |= 0x10
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, data)
    print(f'Built {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
