# Troubleshooting

## “Couldn't add plugin. Try again.”

1. Download the current file from `dist/Arena-ChatGPT-Plugin.zip`.
2. Use **Choose file** to select the newly downloaded copy; retrying an already-selected old copy resubmits the old bytes.
3. Confirm the manifest says version 1.0.1 or newer. Do not upload GitHub's source archive.
4. Check any detailed package findings shown by the host. A generic message alone does not identify the cause.

The initial package lacked publisher metadata, used 24-pixel branding, and carried nonportable policy product names. Version 1.0.1 supplies `author.name` and `interface.developerName`, uses 512-pixel square assets, normalizes skill metadata, and places a single compatibility manifest at the archive root. The user confirmed successful import after choosing the corrected file.

The local validator checks documented structural, metadata, and asset constraints. It is not OpenAI's server-side validation service and cannot promise that every host build accepts a package. Reference: https://developers.openai.com/plugins/deploy/submission-errors.

## “Native subagents unavailable”

The host must expose real native independent agents. Move to an eligible Work environment if available. Importing the skill cannot grant native agent tools. Do not replace the run with simulated personalities, reuse a competitor as judge, or add paid APIs.

## A wave exceeds capacity

Lower `--wave` to verified available child capacity. Count the orchestrator and other live agents against shared limits. Do not silently change the requested competitor count. A lifetime-agent limit without a documented release method is a checkpoint-and-stop condition.

## A job is missing or still running

Use `check <phase>` and inspect actual live-agent status. Wait for existing live work before retrying. Retry missing competitor/attack/defense outputs once in a fresh context. Follow the skill's failure handling; only the independent judge scores missing candidate answers.

## A verdict is rejected

The engine rejects missing/invalid scores, missing boolean fatal flags, missing match standing lists, incorrect match IDs, ambiguous picks, or empty reasons. It retains the bad file and lists a fresh judge job. Do not manually invent a verdict. After three failed judge attempts, save a checkpoint and report the blocker.

## A restored run still references old paths

Run `relocate --dir <restored-run-dir>`, then `status` and `next` with the same explicit directory. Regenerate the current phase's briefs. External files named in the task must still be available or be resolved with the user; relocation does not silently rewrite the task.

## The baseline wins

That is a valid outcome. Report both scores and the judge's reason, and show both answers. The tournament is not required to beat a strong baseline.

## A file is missing after the session ended

Scratch storage is temporary. Preserve the entire run in durable storage before ending the session. This repository intentionally excludes `.arena/` records; saving source does not save the user's tournament data.
