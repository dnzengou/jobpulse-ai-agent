# agents.json — the "package.json for agents"

A machine-readable manifest at `/agents.json` that tells a tool-using agent
how to install the product, what tools it exposes, and where the docs live.

The format is still settling across the ecosystem; the shape below is the
superset that Claude Code, LangChain, and CrewAI-style runners can all read.
Keep it short.

## Shape

```json
{
  "schema_version": "0.1",
  "name": "<product>",
  "description": "<one-sentence pitch, same as llms.txt line 1>",
  "homepage": "https://example.com",
  "repository": "https://github.com/<owner>/<repo>",
  "license": "Apache-2.0",
  "install": {
    "claude_code": [
      "/plugin marketplace add <marketplace-path>",
      "/plugin install <plugin-name>@<marketplace-name>"
    ],
    "cli": "npx <package>"
  },
  "entrypoints": {
    "slash_commands": ["/findmeajob", "/apply", "/setup"],
    "mcp_server": {
      "name": "<server-name>",
      "transport": "stdio",
      "tools": ["search_jobs", "search_jobs_batch", "get_supported_sites"]
    }
  },
  "capabilities": [
    "Search 8 job boards",
    "Build or review a resume",
    "Tailor resume per job posting",
    "Write cover letters and interview prep",
    "Browser-assisted application"
  ],
  "docs": {
    "readme": "https://github.com/<owner>/<repo>/blob/main/README.md",
    "blueprint": "https://github.com/<owner>/<repo>/blob/main/BLUEPRINT.md",
    "llms_txt": "https://example.com/llms.txt"
  },
  "contact": {
    "issues": "https://github.com/<owner>/<repo>/issues",
    "community": "<discord/slack url>"
  }
}
```

## Rules

1. **Install commands must be copy-pasteable.** An agent will paste them.
2. **Keep `capabilities` to 3–7 items.** One sentence each. These are the lines
   that end up in agent-generated product comparisons.
3. **Point `docs.llms_txt` at the absolute URL** so an agent can chain-fetch.
4. **Do not list credentials, API keys, or environment variables.** If the
   product needs them, link to a docs page that explains how to obtain them
   safely.
