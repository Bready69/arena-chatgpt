# Arena for ChatGPT

<img src="assets/icon.svg" alt="Arena" width="80" height="80">

**Independent agents compete to improve one answer.**

Arena gives real independent competitors the same task and distinct strategy cards. Each pair attacks the other answer, defends and revises its own, and receives a verdict from a separate judge. A single-elimination bracket produces a champion. An optional fresh judge then compares it blind with a supplied baseline.

This is an unofficial ChatGPT port of [Jake Schincariol's Arena](https://github.com/Jakeschincariol/arena-skill), distributed under the MIT license. It uses native agents in the host session and does not call paid model APIs.

## Install

1. Download [Arena-ChatGPT-Plugin.zip](dist/Arena-ChatGPT-Plugin.zip).
2. In ChatGPT, open **Customize → Plugins → Add**, choose the ZIP, and select **Add plugin**.
3. Open a Work conversation and select Arena.
4. Start small:

```text
Use Arena with 4 competitors to solve: <your task>
```

For a direct skill invocation:

```text
Use $arena --agents 4 --seed 7 to solve: <your task>
```

Use the plugin ZIP in `dist/`, rather than GitHub's **Download ZIP** source archive. The source archive has a different purpose and layout. Import UI availability varies by client. See [installation](docs/INSTALLATION.md).

**Requires Python, writable storage, and native independent subagents.** The bundled adapter targets Work's `collaboration.spawn_agent` with `fork_turns="none"`. Importing a plugin does not add these tools to a host that lacks them. Arena checkpoints and reports a blocker instead of roleplaying competitors or using a paid API.

## How it works

| Stage | Who does the work |
| --- | --- |
| Initial solutions | One fresh independent agent per competitor |
| Attacks | Two fresh agents per match, each attacking the other answer |
| Defenses and revisions | Two fresh agents per match, preserving each competitor's card and approach |
| Match verdict | A separate fresh judge checks the work and scores both answers |
| Next round | Winners carry their revised answers forward; odd pools receive fair byes |
| Optional baseline check | Another fresh judge scores neutral X/Y copies of champion and baseline |

A competitor's identity is its card and latest solution file. Every job uses a fresh context, including later rounds. The orchestrator does not compete or judge.

The deck contains **2,160 distinct cards**: 15 reasoning modes × 12 workflows × 12 strategies. The seeded dealer balances their use without repeating cards.

## Choose a size

| Competitors | Rounds | Job-agent calls without baseline | With baseline |
| ---: | ---: | ---: | ---: |
| 2 | 1 | 7 | 8 |
| 4 | 2 | 19 | 20 |
| 8 | 3 | 43 | 44 |
| 16 (`--quick`) | 4 | 91 | 92 |
| 100 (original default) | 7 | 595 | 596 |

Calls are not all concurrent. `--wave` controls the wave size within the host's verified capacity. The engine's portable default is one job per wave. Native agents consume normal session usage; no claim of unlimited or zero-cost model usage is made.

Use an explicit small `--agents` value while learning the workflow. See [usage and resuming](docs/USAGE.md).

## Scoring

Each criterion is scored from 0 to 10:

| Criterion | Weight |
| --- | ---: |
| Correctness | 30 |
| Completeness | 25 |
| Specificity | 15 |
| Robustness | 20 |
| Clarity | 10 |

The weighted total is out of 100. A verified fatal flaw cannot beat a nonfatal solution. Exact ties use fewer standing attacks, then correctness, then the judge's justified preference. The engine enforces the arithmetic and rejects malformed verdicts. [Full rubric](skills/arena/references/rubric.md).

## State and privacy

Run records live under `.arena/` in the working directory. They include task text, candidate answers, critiques, revisions, verdicts, and actual dispatch receipts. State is written atomically; `status` and `next` resume the run. Save records durably before ending a temporary session.

Agents have independent contexts but **share a filesystem**. Their read/write boundaries are instructions, not an operating-system security sandbox. Only use task inputs you are authorized to share with participating agents. Run records are excluded from this repository by default. See [security](SECURITY.md).

## Verification

The port passed **37 engine checks** and a real two-competitor tournament with eight fresh job agents, including separate match and final judges. The champion scored 97 against a deliberately flawed fixture baseline's 39.5. Both attackers reported no concrete attacks; the live test exercised the phases but not concession of an opponent's valid attack.

The user confirmed that plugin version **1.0.1 imported successfully**. Larger brackets have bookkeeping regression coverage; a live 100-competitor tournament was not run as part of the port verification. Scores are judgments, not proof that an answer is correct. [Testing details](docs/TESTING.md).

## Build and test

The engine itself uses only the Python standard library. Development package validation additionally uses PyYAML.

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s skills/arena/scripts -p 'test_*.py' -v
python scripts/build_plugin.py
python scripts/validate_package.py dist/Arena-ChatGPT-Plugin.zip
```

GitHub Actions runs the checks and verifies that the committed plugin ZIP is reproducible from source.

## Documentation

- [Installation](docs/INSTALLATION.md)
- [Usage, commands, baselines, and resuming](docs/USAGE.md)
- [Architecture and port differences](docs/ARCHITECTURE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Testing and limits](docs/TESTING.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [Attribution](THIRD_PARTY_NOTICES.md) and [MIT license](LICENSE)

