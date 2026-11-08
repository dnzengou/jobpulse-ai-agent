# Contributing to JobPulse AI Agent

Thanks for taking an interest. JobPulse is a small, focused Claude Code plugin — most useful contributions are small too. This guide keeps everyone pointed in the same direction.

## Ground rules

1. **Verify before you ship.** If you change a user-visible claim (on the landing page, README, or anywhere else), update [`FACTS.md`](FACTS.md) so the claim still maps to code or docs.
2. **No fabricated social proof.** No made-up user counts, star counts, ratings, reviews, logos, or testimonials. If we don't have it, we don't claim it. See [`FACTS.md`](FACTS.md) for the standard.
3. **Keep the local-only invariant.** Any PR that adds a non-local network call to a JobPulse-owned endpoint will be rejected. If you have an idea for an opt-in analytics or cloud feature, open a discussion first.
4. **Trim first, add second.** A 10-line removal that improves clarity beats a 100-line feature. Dependencies are liabilities.
5. **Follow the project's "no comments unless the WHY is non-obvious" rule** — mirror the style of the existing Python and JS modules. Well-named identifiers over narration.

## Dev setup

```bash
git clone https://github.com/dnzengou/jobpulse-ai-agent.git
cd jobpulse-ai-agent

# MCP server (Python)
cd mcp
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Smoke tests (no network calls)
.venv/bin/python test_server.py
```

To run the plugin locally against Claude Code:

```bash
claude --plugin-dir /path/to/jobpulse-ai-agent
```

## Where to put things

| You want to add… | Put it here |
|---|---|
| A new job board | Upstream in [JobSpy](https://github.com/speedyapply/JobSpy), not here — this repo is a thin wrapper. |
| A new MCP tool | New `@mcp.tool()` function in [`mcp/job_server.py`](mcp/job_server.py), plus a smoke test in [`mcp/test_server.py`](mcp/test_server.py). |
| A new agent | A single `.md` file under [`agents/`](agents/). Read any existing agent first to match the voice. |
| A new workflow / slash command | A new skill directory under [`skills/`](skills/) with a `SKILL.md`. |
| A new reference doc the agents cite | Under [`references/`](references/). Keep it short and factual. |
| A new credibility / discoverability file | Repo root, and mirror the public-facing ones under [`public/`](public/). |

## Commit messages

Write human commit messages. Imperative mood, short subject line (≤ 72 chars), details in the body if they matter.

```
feat(tracker): add log_outcome MCP tool + /track skill

Local JSONL trajectory log at job-search/outcomes.jsonl. No telemetry;
file exists so future releases can measure response-rate lift honestly
instead of claiming numbers we haven't earned.
```

## Pull requests

- One logical change per PR. If you're doing a credibility pass and a feature, split them.
- Update [`CHANGELOG.md`](CHANGELOG.md) under `## [Unreleased]` in the same PR.
- If you touch user-visible copy, run through [`FACTS.md`](FACTS.md) to make sure every claim still has proof.
- CI is simple: the smoke tests in `mcp/test_server.py` must pass.

## Code of conduct

Participation in this project is governed by [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Short version: be kind, be specific, assume good faith, flag harassment.

## License

By contributing you agree your contributions will be licensed under [Apache 2.0](LICENSE), the same license as the rest of the project.
