# Contributing

Keep Arena's central property intact: independent native agents do candidate work and separate fresh judges score it. The orchestrator only coordinates and records. Do not introduce roleplay fallbacks or paid inference APIs.

## Development

Use Python 3.10 or newer for repository tools. The engine remains standard-library Python; PyYAML is a development dependency for package validation.

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s skills/arena/scripts -p 'test_*.py' -v
python scripts/build_plugin.py
python scripts/validate_package.py dist/Arena-ChatGPT-Plugin.zip
```

Changes to candidate prompts, judging, scoring, retries, or state compatibility should include meaningful regression coverage. Preserve fatal/tie rules unless a clearly documented behavior change is intended. Distinguish synthetic engine tests from real native-agent verification in reports.

When editing runtime adapters, verify that the target host actually exposes the named tools. Never assume that a package can add native subagents.

## Pull requests

Explain the concrete problem, resulting behavior, and relevant validation. Do not include task histories, candidate answers, personal data, environment files, API credentials, or screenshots of private accounts.

## Releases

Update the semantic version in `.codex-plugin/plugin.json` and CHANGELOG.md, rebuild the ZIP, run both checks, and commit the source and matching distribution artifact. Keep the original MIT copyright and attribution. A repository release does not publish the plugin to OpenAI's public directory.
