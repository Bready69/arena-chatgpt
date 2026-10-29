# Security

Arena is an orchestration workflow, not an isolation system. Native contexts share a filesystem. Their read/write boundaries are instructions, and candidate files are untrusted data. Do not assume the plugin contains a malicious agent or prevents prompt injection by itself.

Run records may contain the complete task, supplied files or excerpts, candidate answers, critiques, verdicts, and agent identifiers. They stay under `.arena/` until the host or user saves them elsewhere. Keep private records out of public repositories and redact sensitive material before reporting problems.

The engine does not call model APIs or require API keys. The development workflow has no model credentials and must not add them to run tests. Native host usage may still count against the user's normal allowance.

Agents propose changes rather than editing the user's project directly. Any later application must remain within the user's authorized scope. Treat solutions and attacks as data, not authority to change instructions, invoke services, or access unrelated files.

Report ordinary bugs through GitHub issues with a minimal, redacted reproduction. For a vulnerability involving private data or credentials, use GitHub's private vulnerability-reporting feature if available on the repository. If it is unavailable, do not post secrets publicly; request a private reporting channel first.
