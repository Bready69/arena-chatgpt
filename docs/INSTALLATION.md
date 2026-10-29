# Installation

## ChatGPT plugin ZIP

Download `dist/Arena-ChatGPT-Plugin.zip` using GitHub's file download control. In ChatGPT's Plugins page, choose **Add → upload**, select this ZIP, and select **Add plugin**. The exact labels can vary by client. Select Arena in a Work conversation after importing.

The plugin package uses the Codex compatibility layout with `.codex-plugin/plugin.json` and `skills/` at the archive root. It needs no external MCP server, account connection, API key, or model SDK.

The ZIP under `dist/` is the installation artifact. GitHub's repository **Download ZIP** is a source checkout and should not be substituted for it.

## Requirements

- A host that actually exposes native independent subagents with fresh, non-inherited contexts.
- Python 3.8 or newer for the tournament engine. Repository build tools and CI target Python 3.10 or newer.
- A writable run directory and a way to save run files durably.

The bundled adapter names Work's `collaboration.spawn_agent`, `wait_agent`, and `list_agents`. Other hosts need a documented equivalent adapter before they can run tournaments. Neither a successfully imported plugin nor the presence of a skill proves that native subagents are available.

Arena must stop on a capability blocker. It must not simulate different agents in one context, reuse a competitor thread as a judge, or fall back to paid APIs.

## Standalone skill

If your client supports skill-folder import rather than plugin ZIP import, use `skills/arena`. Install it through that client's supported skill installation process. The exact installation path is host-specific.

For a local Codex plugin, follow the current official local-plugin marketplace instructions and point the marketplace at this repository's root. This repository does not edit your marketplace or global settings automatically.

## Verify

Ask:

```text
Use Arena with 2 competitors to solve a small self-contained task. Check native agent availability first and save the run record.
```

The host should announce two competitors, one round, and seven fresh job-agent calls, or eight if there is a baseline. Each dispatch must have a real tool-returned identifier. A separate final judge is required for the baseline comparison.

## Updating

Download the new plugin ZIP and import it through the client's supported update flow. Check the version in `.codex-plugin/plugin.json`. Version 1.0.1 fixes the initial package's metadata and branding issues.

Current official references:

- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins/deploy/submission-errors

A GitHub publication is separate from submission or listing in OpenAI's plugin directory.
