# Architecture and port differences

## Components

| Path | Responsibility |
| --- | --- |
| `.codex-plugin/plugin.json` | Importable plugin identity and presentation |
| `skills/arena/SKILL.md` | Orchestrator workflow and boundaries |
| `skills/arena/scripts/bracket.py` | Standard-library state machine, pairing, cards, scoring, and CLI |
| `skills/arena/scripts/strategies.json` | 15 reasoning modes, 12 workflows, 12 strategies |
| `skills/arena/references/prompt-templates.md` | Exact briefs for competitor, attacker, defender, match judge, final judge |
| `skills/arena/references/rubric.md` | Written criteria, anchors, fatal rule, and tie-breaks |
| `skills/arena/references/runtime.md` | Native Work adapter and supported execution rules |
| `scripts/build_plugin.py` | Deterministic installable ZIP build |
| `scripts/validate_package.py` | Local package checks derived from documented upload requirements |

## Execution

Python does bookkeeping, not inference. The orchestrator invokes native Work agents. Every job is a fresh context with `fork_turns="none"`; no paid model endpoints, API credentials, model SDKs, or shell model runners are used.

The first phase deals balanced unique cards and produces independent answers. Every match then has two attackers, two defenders, and a fresh judge. A competitor persists through its card and latest standalone solution. A later-round job never relies on an earlier agent thread's hidden memory.

Judges do not receive strategy cards. The optional final judge sees neutral X/Y copies, with the mapping kept in state. Filesystem boundaries are instructional, so this is not a malicious-agent containment system.

## State

Each run snapshots its task, optional baseline, rubric, prompt templates, and dealt cards. Atomic `arena.json` state includes pairings, eliminations, champion, final comparison, and dispatch receipts. `.arena/LATEST` selects a default run. Each CLI invocation reloads state from disk.

`next` progresses through spawn, per-round attacks/defenses/judgment/collection/advancement, and optional final judgment. Malformed verdicts are quarantined with distinct filenames so retries do not overwrite evidence.

## Scoring integrity

Each judge must supply five numeric scores in [0, 10], an explicit boolean fatal flag, an unambiguous pick, and a reason. Match verdicts must identify the match and include standing-attack lists for both candidates. The engine computes weighted totals and applies fatal and tie rules.

If a judge's pick conflicts with the arithmetic, the computed winner prevails. A legacy winner-only `survived` list may describe the losing pick, so those claims are omitted and the arithmetic explanation is retained. Optional `survived_by` evidence can identify the correct candidate explicitly.

## Differences from upstream

Original source: https://github.com/Jakeschincariol/arena-skill at `df07b8e518e10cdecd8cd7712d9958b6f396250e`.

Preserved: independent job contexts, original card deck/dealer, default 100 and quick 16, seeded pairing, fair byes, attack/defend/revise phases, separate judges, criterion weights, fatal/tie rules, state-based resume, and blind baseline comparison.

Adapted: Claude Agent/Task calls and Claude-specific variables were replaced by native Work collaboration tools. Waves default to one for portability and must fit actual capacity. Templates are snapshotted per run. Dispatch receipts and relocation support were added. Incomplete/nonfinite scores no longer fall back to an unscored judge pick. Baseline snapshots preserve exact text. Metadata and square branding assets meet the documented plugin package checks.

These runtime checks cannot guarantee a host's future availability, scheduling limits, or model correctness.
