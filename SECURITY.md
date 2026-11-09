# Security & Privacy Policy

## Threat model in one paragraph

JobPulse is a **local** Claude Code plugin. The plugin's own code runs inside your Claude Code session, writes files to your working directory (`job-search/`), and spawns a Python MCP server that makes outbound requests **only** to public job boards via the [JobSpy](https://github.com/speedyapply/JobSpy) library. There is no JobPulse-operated server, no account, no telemetry, and no cloud sync. Your resume, preferences, and application packages never leave your machine.

Audit for yourself:

```
grep -rE "fetch\(|requests\.|urllib|axios|https?://" mcp/ scripts/ skills/ agents/
```

The only outbound calls you will find are:
- `scrape_jobs(...)` in [`mcp/job_server.py`](mcp/job_server.py) — JobSpy's public job-board scraping.
- Documentation links (plain text, not called at runtime).

## Reporting a vulnerability

**Do not file a public issue for security vulnerabilities.**

Email the maintainer with the subject line **`[JobPulse Security] <short summary>`**:

- Preferred: open a [GitHub private security advisory](https://github.com/dnzengou/jobpulse-ai-agent/security/advisories/new).
- Alternative: contact the author via [the author page](https://github.com/dnzengou).

Please include:
1. Affected file(s) and version (`.claude-plugin/plugin.json` → `version`).
2. Reproduction steps.
3. Impact (what an attacker could do).
4. Suggested fix, if you have one.

We aim to acknowledge within **72 hours** and ship a fix or mitigation within **14 days** for high-severity reports.

## Scope

In scope:

- Code that ships in this repository (`mcp/`, `scripts/`, `skills/`, `agents/`, `public/`).
- Supply-chain issues in the pinned dependencies in [`mcp/requirements.txt`](mcp/requirements.txt).
- Hook execution paths — [`scripts/ensure-deps.mjs`](scripts/ensure-deps.mjs) runs at `SessionStart` and installs Python dependencies in a venv.

Out of scope:

- Vulnerabilities in **JobSpy** itself — report those upstream to [speedyapply/JobSpy](https://github.com/speedyapply/JobSpy).
- Vulnerabilities in **Claude Code** or the Anthropic API — report to Anthropic.
- Issues that require local attacker access to `job-search/` (that's the user's own filesystem).
- Rate-limiting / scraping countermeasures on job boards — those are policies of the board, not JobPulse bugs.

## What we commit to

- **No telemetry, ever.** If we add optional analytics in the future, it will be explicit opt-in, documented in [`AGENTS.md`](AGENTS.md), and the first commit that introduces it will be referenced in [`CHANGELOG.md`](CHANGELOG.md).
- **No background phone-home.** The MCP server only runs while Claude Code is running and only makes calls when a tool is invoked.
- **No bundled credentials.** Nothing in this repo ships an API key. Job boards that require authentication (e.g. LinkedIn personalized results) are handled by JobSpy's own session cookies when the user supplies them.

## What **you**, the user, should do

- Keep your Python venv (`mcp/.venv/`) excluded from version control (it already is — see [`.gitignore`](.gitignore)).
- Don't commit the `job-search/` folder to a public repo — it contains your resume and research briefs. Add it to your own `.gitignore` if your working directory is a git repo.
- Use the browser-assisted `/apply` skill with eyes open — it will **ask before every submission**, but you still own clicking yes.
- If a job board asks for an account, that's a JobSpy / board interaction, not JobPulse — review their privacy policy.

## Dependencies

Runtime Python deps (see [`mcp/requirements.txt`](mcp/requirements.txt)):

- `mcp` — Model Context Protocol SDK (Anthropic).
- `python-jobspy` — multi-board job scraper.
- `pandas` — tabular processing in the MCP server.

Runtime Node deps: none at runtime. The [`scripts/`](scripts/) launchers use only Node's standard library.

To review the dependency tree, after install:

```
mcp/.venv/bin/pip list
```
