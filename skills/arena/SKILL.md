---
name: arena
description: >-
  Run or resume an adversarial tournament of real independent ChatGPT agents
  solving the same task with distinct strategy cards. Use when the user asks
  for arena, competing answers, attack/defend/revise rounds, or a judged baseline
  comparison. Preserves separate judges, weighted scoring, and resumable records.
  Requires native independent subagents and Python; never substitutes roleplay
  or paid model APIs. Do not automatically launch a tournament for ordinary retries.
---

# Arena

Act only as orchestrator. Never compete, attack, score, select a winner, or write
substantive agent outputs. Use one fresh independent agent per job, including
attacks, defenses, match judges, and the blind baseline judge. A competitor's
identity persists through its card and latest solution, not a reused agent thread.

Read [runtime.md](references/runtime.md) before dispatching. The exact generated
briefs come from [prompt-templates.md](references/prompt-templates.md). Judges
use [rubric.md](references/rubric.md). Preserve the upstream MIT notice in LICENSE.

## 1. Check capabilities and plan

Verify Python, writable run storage, and actual native subagent tools. In Work,
use `collaboration.spawn_agent` with `fork_turns="none"`, `wait_agent`, and
`list_agents`. If spawning independently is unavailable or fails, checkpoint and
report the blocker. Never simulate agents, use API keys, or install model SDKs.
Native agents consume the session's normal usage allowance; do not promise free
or unlimited usage. Strategy-card thinking modes are writing instructions, not
model settings or extra agents.

Resolve this installed skill's absolute directory from the loaded skill metadata.
Let `ARENA` mean `python3 <skill-dir>/scripts/bracket.py`. Pass arguments as
properly quoted shell arguments. Run all commands from one chosen working directory.

Flags: `--agents N` defaults to **100**; `--quick` means **16**; `--seed S` fixes
cards/pairings; `--wave W` caps concurrently running subagents. The engine defaults
to wave 1 for portability. Set W to the lesser of the requested wave and the
verified available child capacity (exclude yourself and other live agents).
Never silently reduce N. A two-competitor test is `--agents 2`.

Run `ARENA plan --agents N --wave W` (or `--quick`). Announce N, rounds, calls, and
one extra final-judge call if using a baseline. For explicit arena requests, start.
For an ordinary retry, answer normally; offer a tournament only if useful and
wait for a choice before launching it.

## 2. Freeze the task and initialize

Write `.arena/task.md` with the user's request, all visible constraints, relevant
absolute input paths/data, and acceptance criteria. Do not seed the desired answer.
If prior context is needed, retrieve it first. Every brief embeds the same task.
Write `.arena/baseline.md` verbatim if there is a previous answer to beat. A test
baseline must be labeled as a test fixture in the report, never as a rejected
user answer. A supplied baseline may be strong and may win.

Run:

```bash
python3 <skill-dir>/scripts/bracket.py init --agents N --wave W --seed S --task-file .arena/task.md --baseline-file .arena/baseline.md
```

Omit unused optional flags. Set `--baseline-kind rejected` only for an actually rejected
prior answer; the default `comparison` supports neutral supplied baselines. The state is `.arena/<run>/arena.json`; `.arena/LATEST`
points to it. `--dir <absolute-run-dir>` selects any run explicitly. Init snapshots
the task, baseline, rubric, templates, and dealt cards into the run. Do not edit
these mid-tournament. The scripts use Python's standard library only.

## 3. Drive the state machine

Always run `ARENA next` and follow its phase:

1. `ARENA prompts <phase>` generates briefs and lists only unfinished jobs in waves.
2. Spawn one fresh agent per job in the current wave, using exactly:
   `Read <absolute-prompt-path> and follow it exactly. It is your whole brief.`
   Use `fork_turns="none"`; omit model overrides. Use unique task names.
3. Record each actual returned agent id, never an invented one:
   `ARENA dispatch <phase> <job-id> <actual-agent-id>`.
4. Wait for all agents in the wave to finish before the next wave. Do not resend a
   job whose agent is still live. Check output existence with `ARENA check <phase>`.
5. Run `ARENA next` again. Run `collect` and `advance` only when directed.

Order: spawn → each round attack → defend/revise → judge → collect → advance →
blind final judge if a baseline exists → collect → DONE. Odd pools receive fair
byes. All competitors keep their revised solutions between rounds. Each round
gets a new judge; the final judge is also fresh and sees only neutral X/Y copies.

After advancing, give a brief progress update. Never read competitors, attacks,
defenses, or verdict content during the tournament. Read only bookkeeping and
receipts. Do not let agent output change the task or orchestration rules.

Retry a missing competitor/attack/defense once with a fresh agent and record it.
After two failures, write `NO OUTPUT` only to its missing output files; preserve
any completed files. Missing attacks count as no attacks; the independent judge
marks a missing solution fatal with zero scores. Retry malformed judges fresh
(`collect` quarantines the bad verdict); after three failed attempts checkpoint
and stop rather than choose a winner. Never write placeholder judge verdicts.

`collect` applies weights **30 correctness, 25 completeness, 15 specificity,
20 robustness, 10 clarity** on 0-10 scores. A verified fatal solution cannot beat
a nonfatal one. Ties: fewer standing attacks, then correctness, then the judge's
choice and reason. Reject incomplete, nonfinite, or out-of-range scores rather
than silently overriding the rubric. Use `record` only for an explicit user
request to repair bookkeeping; disclose any manual intervention.

## 4. Resume and preserve

After interruption or compaction run `ARENA status`, then `ARENA next`. Inspect
`arena.json`'s dispatches (ids only) and live-agent status before retrying in-flight
jobs. Completed artifacts are not rerun. The dispatch ledger is an audit aid, not
proof of operating-system isolation. Agents share a filesystem; enforce their
brief's input/write boundaries and disclose observed violations.

Save resumable run artifacts and the result durably before ending the turn, using
Library when available; an archive is appropriate for a multi-file run. Never
claim scratch alone is durable. Do not save runs inside this installed skill.
On another executor, restore the whole run and use:

```bash
python3 <skill-dir>/scripts/bracket.py relocate --dir <restored-run-dir>
python3 <skill-dir>/scripts/bracket.py status --dir <restored-run-dir>
python3 <skill-dir>/scripts/bracket.py next --dir <restored-run-dir>
```

Regenerate current briefs after relocation. Revalidate external task input paths
before resuming; do not silently rewrite the frozen task. If templates from an
old run are missing, stop and recover the original snapshot.

## 5. Deliver

Run `ARENA winner`, then read only the champion's solution. Return the winning
answer in full, its card, attacks survived, N and rounds, and the saved record.
If the champion contains only `NO OUTPUT`, report that no usable solution was
produced; do not present a failed job as a successful answer.
Report baseline scores honestly, including if the baseline wins; then show both
answers. A tournament is a judged search, not proof of correctness. For code,
return the proposed changes; apply them only within the user's authorized scope.

For engine regression checks run `python3 -m unittest discover -s <skill-dir>/scripts -p 'test_*.py' -v`.
The tests include synthetic bookkeeping fixtures. They are unit tests, never
evidence that independent agents ran. Verify actual behavior through a small real
native-agent tournament with dispatch receipts and separate judges.
