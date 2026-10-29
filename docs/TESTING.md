# Testing and verification limits

## Engine regression checks

```bash
python -m unittest discover -s skills/arena/scripts -p 'test_*.py' -v
```

The 37 checks cover the dealer, seeded pairings, fair byes, bracket advancement, full phase bookkeeping, weighted scoring, fatal and tie rules, malformed verdict handling, dispatch identifier uniqueness, template snapshots, relocation, verbatim baseline copies, and correct winner evidence.

Some tests use synthetic files or random winners to exercise bookkeeping at larger sizes. Those fixtures are not independent model agents and must never be described as live tournaments.

## Real native-agent test

During the port, two initial competitors solved a self-contained lap-summary task. Each had a distinct strategy card. The run used eight fresh native job agents: two competitors, two attackers, two defenders, a separate match judge, and a separate blind final judge.

The match scored 97 versus 67.5. The blind final comparison scored the champion 97 versus a deliberately flawed test baseline's 39.5. Both attackers reported zero concrete attacks; this exercised the phase sequence but did not verify concession of a valid opponent attack. The champion's executable checks passed again after the run.

A first run was superseded after one job was launched because baseline wording was misleading. That job was interrupted, so nine tournament job launches occurred overall, eight belonging to the completed run. No judge thread was reused from a competitor. Raw private records are not part of this public repository.

No live 100-competitor run was performed for this verification. The user subsequently confirmed plugin version 1.0.1 imported successfully. A successful import does not establish native-agent availability in every client.

## Packaging

```bash
python -m pip install -r requirements-dev.txt
python scripts/build_plugin.py
python scripts/validate_package.py dist/Arena-ChatGPT-Plugin.zip
```

The builder includes the manifest, skills, branding, root README/license, and checksum manifest. It excludes private run records, environment files, source-control data, generated Python caches, and unrelated repository documentation. Fixed archive timestamps make rebuilds comparable.

The validator checks ZIP integrity and safe file paths, exactly one compatibility manifest at the root, required fields/limits, valid skill frontmatter and metadata, supported policy values, complete referenced assets, square image dimensions, required tournament resources, and checksum consistency.

The local checks are not a substitute for host import validation or a real native-agent trial. CI only runs engine/package checks; it never calls a model or consumes API credentials.
