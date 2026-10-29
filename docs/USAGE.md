# Usage and resuming

## Example requests

```text
Use Arena with 4 competitors to solve: design a reliable lap timing algorithm for a casual racing game. Preserve duplicate times and handle missing data explicitly.
```

```text
Use $arena --agents 4 --seed 7 to improve the answer below. Compare the champion blind against the supplied original answer.
```

Provide all constraints in the request, including audience, length, input files, output format, and what must remain unchanged. The orchestrator freezes a self-contained task and embeds the same task in every brief. Do not give separate competitors extra hints.

## Flags

| Flag | Meaning |
| --- | --- |
| `--agents N` | Number of competitors; original default 100; maximum 2,160 distinct cards |
| `--quick` | 16 competitors; mutually exclusive with `--agents` |
| `--seed S` | Records deterministic cards and pairings; does not make model responses deterministic |
| `--wave W` | Requested maximum concurrent jobs; the orchestrator must respect actual host capacity |

A run without a baseline takes `N + 5 × (N - 1)` jobs, excluding retries. A baseline adds one fresh judge. A one-competitor run is a trivial special case and does not exercise a competitive match.

## Baselines

A baseline is an answer to compare against. It may be an earlier answer, an explicit benchmark, or a labeled test fixture. It is copied verbatim, including whitespace and line endings. Only use `--baseline-kind rejected` for an actually rejected prior answer; the default is `comparison`.

The final judge receives neutral X/Y copies and must not read state, strategy cards, or original source paths. Either answer can win. If the baseline is preferred, report that honestly and show both answers.

## Engine commands

The installed skill's absolute directory is host-specific. In the examples below, `<skill-dir>` means the directory containing its `SKILL.md`. Replace placeholders before executing. Run commands from one working directory or pass an explicit run directory.

```bash
python3 <skill-dir>/scripts/bracket.py plan --agents 4 --wave 2
python3 <skill-dir>/scripts/bracket.py init --agents 4 --wave 2 --seed 7 --task-file task.md
python3 <skill-dir>/scripts/bracket.py next
```

For a supplied baseline:

```bash
python3 <skill-dir>/scripts/bracket.py init --agents 4 --seed 7 --task-file task.md --baseline-file baseline.md --baseline-kind comparison
```

`next` directs orchestration. `prompts <phase>` writes briefs and lists missing jobs. It does not run agents. The host must launch each job as a fresh native context and record the returned identifier with `dispatch`.

| Command | Purpose |
| --- | --- |
| `plan` | Show bracket size, calls, and waves |
| `next` | Determine the next required action from disk |
| `prompts spawn/attack/defend/judge/final` | Generate phase briefs and list unfinished jobs |
| `dispatch <phase> <job-id> <real-agent-id>` | Record an actual returned native agent identifier |
| `check <phase>` | List missing output files |
| `collect` | Validate judge verdicts, compute scores, and record results |
| `advance` | Close a judged round and pair the survivors |
| `status` | Report current progress |
| `winner` | Report champion, card, scores, and baseline outcome |
| `relocate --dir <restored-run>` | Repair stored paths after restoring a run elsewhere |

The `record` command is for explicitly authorized bookkeeping repair only. It is not a substitute for an independent judge.

## Stop and resume

Tell the orchestrator to stop. It should interrupt live work when appropriate, preserve the run, and report the checkpoint. Later:

```bash
python3 <skill-dir>/scripts/bracket.py status --dir <run-dir>
python3 <skill-dir>/scripts/bracket.py next --dir <run-dir>
```

Check live-agent status and recorded dispatches before retrying missing outputs. Never dispatch a duplicate while its first agent remains live. Existing completed outputs are not regenerated as candidate work.

After moving or restoring files:

```bash
python3 <skill-dir>/scripts/bracket.py relocate --dir <restored-run-dir>
python3 <skill-dir>/scripts/bracket.py status --dir <restored-run-dir>
python3 <skill-dir>/scripts/bracket.py next --dir <restored-run-dir>
```

Regenerate the current phase's briefs after relocation. Revalidate external task-input paths. Do not silently alter the frozen task or replace missing template/rubric snapshots with newer versions.

## Output and applying code

Return the champion's full answer, its strategy card, the attacks it survived, rounds and competitor count, baseline scores when present, and the saved run record. A `NO OUTPUT` champion means failure to produce a usable answer.

Agents propose code inside the run. Applying a winning diff to a real project is a separate action within the user's authorized scope.
