# Integrating JobPulse AI Agent

JobPulse ships as a **Claude Code plugin**, but the job-search engine is a plain [Model Context Protocol](https://modelcontextprotocol.io/) server, so anything that speaks MCP over stdio can use it: your own agents, LangGraph/LlamaIndex pipelines, in-house CLIs, CI jobs, or another LLM runtime entirely.

This document is the integration contract. For the end-user experience, start with [`README.md`](README.md); for the full architecture, see [`BLUEPRINT.md`](BLUEPRINT.md); for the "what's actually true" table, see [`FACTS.md`](FACTS.md).

## 1. Who integrates how

| Caller | Transport | Entry point |
|---|---|---|
| Claude Code (the shipping use case) | MCP stdio | [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) → `mcpServers.jobspy` |
| Another MCP-capable agent runtime | MCP stdio | Spawn `node scripts/start-mcp.mjs` as a child process |
| A Python script / notebook | Direct import | `from mcp.job_server import search_jobs, search_jobs_batch` |
| A shell script or CI job | CLI | Invoke the Python helpers directly (see §3) |
| A browser-side app | HTTP bridge | Front it with a thin HTTP shim (see §5) |

## 2. The five MCP tools

Source: [`mcp/job_server.py`](mcp/job_server.py).

### `search_jobs(search_term, location="USA", site_name=None, results_wanted=15, hours_old=72, job_type=None, is_remote=False, distance=50, country="usa", description_format="markdown") -> str`

Returns JSON: `{"count": N, "results": [...]}`. Each result has `title`, `company`, `location`, `date_posted`, `job_url`, `job_type`, `is_remote`, `min_amount`, `max_amount`, `currency`, `interval`, `site`, `description`.

### `search_jobs_batch(queries: list[dict], country="usa") -> str`

Up to **10** query dicts per call. Each dict accepts the same fields as `search_jobs`. Returns `{total_queries, total_results, query_summaries, results}` — merged but **not deduped** (dedup happens in [`skills/findmeajob/scripts/process_jobs.py`](skills/findmeajob/scripts/process_jobs.py) with URL-based dedup). Prefer this over N separate calls.

### `get_supported_sites() -> str`
### `get_supported_countries() -> str`
### `get_search_tips() -> str`

Metadata / documentation helpers for the agent to consult at query-planning time.

## 3. Direct calls (no MCP client)

For a script, notebook, or any other Python caller that doesn't want to spawn an MCP server:

```python
# Assumes you have installed mcp/requirements.txt into the active env.
import json, sys
sys.path.insert(0, "mcp")
from job_server import search_jobs_batch

payload = search_jobs_batch(queries=[
    {"search_term": "senior backend engineer", "is_remote": True, "results_wanted": 40},
    {"search_term": "staff ml engineer",       "is_remote": True, "results_wanted": 40},
    {"search_term": "python llm engineer",     "location": "Berlin, Germany", "results_wanted": 30},
])
jobs = json.loads(payload)["results"]
print(f"Got {len(jobs)} merged results from {len({j['_query_term'] for j in jobs})} queries.")
```

To reuse the processing pipeline (dedupe + filter + score):

```bash
python skills/findmeajob/scripts/process_jobs.py \
  --input raw-search-output.json \
  --profile job-search/preferences.md \
  --resume  job-search/jane-doe-resume.md \
  --output  job-search/jobs-final.json
```

## 4. From another agent runtime (MCP stdio)

Any MCP client that can launch a stdio server will work. Spawn:

```
node /path/to/jobpulse-ai-agent/scripts/start-mcp.mjs
```

The launcher auto-selects the Python venv at `mcp/.venv/` (created by [`scripts/ensure-deps.mjs`](scripts/ensure-deps.mjs) on first run). Pipe stdin/stdout for the MCP transport; `stderr` is log output.

Minimal LangChain example:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    client = MultiServerMCPClient({
        "jobpulse": {
            "transport": "stdio",
            "command": "node",
            "args": ["/path/to/jobpulse-ai-agent/scripts/start-mcp.mjs"],
        }
    })
    tools = await client.get_tools()
    # feed `tools` into your agent as usual
```

## 5. HTTP bridge (optional, for browser clients)

There's no HTTP server in this repo on purpose — MCP stdio is the contract. If you need HTTP, wrap it with a small shim. A 30-line [`fastmcp.Server.run_sse()`](https://github.com/modelcontextprotocol/python-sdk) wrapper is enough. Treat this as **your** glue code, not something JobPulse hosts.

## 6. Trajectory / outcome log (local-only)

Each run of `/findmeajob` and `/apply` optionally writes to `job-search/outcomes.jsonl` — one JSON object per line, append-only, same directory as the user's other local data. Fields:

```jsonc
{
  "ts": "2026-11-08T14:12:03Z",      // ISO 8601, UTC
  "run_id": "r_2026-11-08_a7f2",     // stable per /findmeajob session
  "event": "applied" | "shortlisted" | "customized" | "responded" | "interview" | "offer" | "rejected" | "withdrawn",
  "company": "Acme Corp",
  "role": "Senior AI Engineer",
  "source": "indeed",                // which board the job came from
  "score": 22,                       // from process_jobs.py
  "variant": "resume-v2",            // optional: which resume variant was used
  "notes": "..."                     // optional free text
}
```

This file is **never** read or written by anyone other than the user's local Claude Code session. It exists for two reasons:

1. **End-user value today**: the `/track` skill reads it to answer "how many applications am I behind on this week?" without the user maintaining a spreadsheet.
2. **Future value**: the schema is stable enough that, if a user ever opts in, aggregate statistics over this log (across many users, consented, hashed) would let the project measure real response-rate lift and evolve its scoring. That opt-in does not exist today and will not be added without an explicit consent prompt, documented in [`SECURITY.md`](SECURITY.md) before it ships.

Treat the schema as additive: new events and fields may be added; existing ones won't be renamed in-place.

## 7. Constraints you should respect

- **Job-board rate limits are real.** JobSpy backs off, but don't hammer. If you're running batch searches on a schedule, start with `hours_old=168` (one week) and increase interval before you increase volume.
- **This repo does not ship with cookies for authenticated boards** (e.g. LinkedIn personalized search). If you need those, configure JobSpy directly on your side.
- **No telemetry back to JobPulse.** Your deployments are yours. Don't advertise otherwise to your own users.

## 8. Versioning

The MCP tool contract follows the version in [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json). Breaking changes to tool names, parameters, or return shapes bump the major version and get a migration note in [`CHANGELOG.md`](CHANGELOG.md). Additive changes (new tools, new optional params) bump minor.

Questions? [Issues](https://github.com/dnzengou/jobpulse-ai-agent/issues) · [Discord](https://discord.gg/babcVNJBet).
