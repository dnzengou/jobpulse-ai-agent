<div align="center">

# JobPulse AI Agent

### Your AI job-search command center

Search 8 job boards, get company research, tailor your resume, write cover letters, prep for interviews, and apply — all from a single Claude command.

[![Version](https://img.shields.io/badge/version-0.4.0-7c3aed?style=for-the-badge)](https://github.com/dnzengou/jobpulse-ai-agent/blob/main/BLUEPRINT.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-06b6d4?style=for-the-badge)](LICENSE)
[![Discord](https://img.shields.io/badge/Community-Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/babcVNJBet)

[Quick Start](#quick-start) · [Live Site](https://jobpulse-ai-agent.vercel.app) · [Blueprint](BLUEPRINT.md) · [Facts](FACTS.md) · [Integrate](INTEGRATE.md) · [Changelog](CHANGELOG.md) · [Discord](https://discord.gg/babcVNJBet)

</div>

---

## Demo

<!-- Paste your YouTube demo URL here once recorded — replace VIDEO_ID with the YouTube ID -->
<!-- [![Watch the demo](https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg)](https://youtu.be/VIDEO_ID) -->

> Demo coming soon — a 60-second walkthrough.

## Quick Start

**1. Install the plugin** — inside Claude Code, run:

```
/plugin marketplace add dnzengou/jobpulse-ai-agent
/plugin install jobpulse-ai-agent@jobpulse-ai-agent
```

**2. Restart Claude Code** — quit the app and reopen.

**3. Run `/findmeajob`** — answer 3 questions and it does the rest.

> Not using the marketplace yet? Clone the repo and point Claude Code at it: `claude --plugin-dir /path/to/jobpulse-ai-agent` (see [Advanced install](#user-content-advanced-install-without-the-marketplace)).

## Try it

Talk to Claude like a friend:

- *"Find me a remote senior frontend role at a small company."*
- *"Review my resume and tell me what to fix."*
- *"Tailor my resume for this Acme Corp posting."*
- *"What's the culture like at Stripe?"*

## What's inside

**Three skills** · **Eight agents** · **One MCP server** (5 tools, 8 job boards) · **Browser-assisted apply**

| Skill | What it does |
|---|---|
| `/findmeajob` | Full workflow: onboarding → resume → job search → research → application packages |
| `/apply` | Browser-assisted form fill — guided, confirmed at every step, never auto-submits |
| `/setup` | View/edit preferences, reset data, manage resumes |

| Agent | What it produces |
|---|---|
| `resume-reviewer` | Scored feedback + improved resume |
| `resume-builder` | Resume built from your existing files |
| `company-researcher` | Structured research brief with red/green flags + customization notes |
| `resume-customizer` | JD-tailored resume (re-keyed, not fabricated) |
| `cover-letter-writer` | 3-paragraph targeted letter, 200–280 words |
| `interview-prepper` | STAR-outline behavioral Qs + technical Qs + questions to ask |
| `salary-negotiator` | Market rate research + counter-offer email + BATNA talking points |
| `linkedin-optimizer` | Profile audit + headline/About/experience rewrites for recruiter + ATS visibility |

## Community

[**Discord**](https://discord.gg/babcVNJBet) — chat, help, show-and-tell · [**Issues**](https://github.com/dnzengou/jobpulse-ai-agent/issues) — bugs & feature requests · [**Contribute**](CONTRIBUTING.md) · [**Security**](SECURITY.md)

<details>
<summary><b>Where your data lives</b></summary>

Everything stays in your working directory, in a `job-search/` folder:

```
job-search/
├── preferences.md                    ← your search criteria
├── jon-smith-resume.pdf              ← your base resume
├── acme-corp/
│   ├── research.md                   ← company research
│   ├── jon-smith-resume-acme-corp.pdf ← customized resume
│   └── apply-link.md                 ← application URL
└── startup-xyz/
    ├── research.md
    ├── jon-smith-resume-startup-xyz.pdf
    └── apply-link.md
```

Nothing leaves your machine except the actual job-board queries. No telemetry, no analytics.

</details>

<details>
<summary><b>Troubleshooting</b></summary>

| Something's off | Fix |
|---|---|
| *"Python not found"* | Install Python 3.10+ from [python.org](https://www.python.org/downloads/). The job-scraping engine runs on Python. |
| *"JobSpy not installed"* or import errors | The first run installs Python deps automatically — give it a minute, then retry. |
| Plugin doesn't show up after install | Fully quit Claude Code and reopen. The plugin registers on startup. |
| Searches return nothing | Some boards rate-limit aggressively. Try a narrower location or fewer sites. |

More help in the [Discord](https://discord.gg/babcVNJBet).

</details>

<details>
<summary><b>Advanced install (without the marketplace)</b></summary>

If you'd rather clone and run it directly:

```bash
git clone https://github.com/dnzengou/jobpulse-ai-agent.git
cd jobpulse-ai-agent
claude --plugin-dir .
```

**Requirements:** Python ≥ 3.10, Node.js ≥ 18.

</details>

<details>
<summary><b>Built on</b></summary>

- [JobSpy](https://github.com/speedyapply/JobSpy) — multi-board job scraper (Indeed, LinkedIn, Glassdoor, ZipRecruiter, Google Jobs, Bayt, Naukri, BDJobs)
- [Model Context Protocol SDK](https://github.com/modelcontextprotocol/sdk) — tool exposure to Claude

</details>

## License

[Apache License 2.0](LICENSE) — © 2026 JobPulse AI Agent contributors

## For AI agents & LLM search engines

- [`FACTS.md`](FACTS.md) — every claim on every surface, mapped to the code or doc that proves it.
- [`llms.txt`](llms.txt) — curated map of the repo for LLM-powered search ([llmstxt.org](https://llmstxt.org)).
- [`ai.txt`](ai.txt) — AI-use policy (what you may reuse, cite, and train on).
- [`INTEGRATE.md`](INTEGRATE.md) — how other agents, apps, and CI call the MCP server.
- [`CITATION.cff`](CITATION.cff) — machine-readable citation metadata.

If an AI tool cites JobPulse, we want it cited on something that's actually true — verify against the links above.
