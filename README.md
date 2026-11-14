<div align="center">

# JobPulse AI Agent

### Your AI job-search command center

Search 8 job boards, get company research, tailor your resume, write cover letters, prep for interviews, and apply — all from a single Claude command.

[![Version](https://img.shields.io/badge/version-0.3.1-7c3aed?style=for-the-badge)](https://github.com/dnzengou/jobpulse-ai-agent/blob/main/BLUEPRINT.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-06b6d4?style=for-the-badge)](LICENSE)
[![Discord](https://img.shields.io/badge/Community-Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/babcVNJBet)

[Quick Start](#quick-start) · [Live Site](https://jobpulse-ai-agent.vercel.app) · [Blueprint](BLUEPRINT.md) · [Discord](https://discord.gg/babcVNJBet)

</div>

---

## Demo

<!-- Paste your YouTube demo URL here once recorded — replace VIDEO_ID with the YouTube ID -->
<!-- [![Watch the demo](https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg)](https://youtu.be/VIDEO_ID) -->

> Demo coming soon — a 60-second walkthrough.

## Quick Start

**1. Install the plugin** — inside Claude Code, run:

```
/plugin marketplace add JCodesMore/jcodesmore-plugins
/plugin install jobs-for-ai-agents@jcodesmore-plugins
```

**2. Restart Claude Code** — quit the app and reopen.

**3. Run `/findmeajob`** — answer 3 questions and it does the rest.

## Try it

Talk to Claude like a friend:

- *"Find me a remote senior frontend role at a small company."*
- *"Review my resume and tell me what to fix."*
- *"Tailor my resume for this Acme Corp posting."*
- *"What's the culture like at Stripe?"*

## What's inside

**Four skills** · **Eight agents** · **One MCP server** (5 tools, 8 job boards) · **Browser-assisted apply** · **Pipeline tracker** · **Agent-SEO kit**

| Skill | What it does |
|---|---|
| `/findmeajob` | Full workflow: 3-question onboarding → resume → job search → research → application packages → pipeline tracker (CSV + dashboard) |
| `/apply` | Browser-assisted form fill — guided, confirmed at every step, never auto-submits |
| `/setup` | View/edit preferences, reset data, manage resumes |
| `/agent-seo` | Standalone deliverable — produces `llms.txt`, `agents.json`, JSON-LD, `robots.txt`, `sitemap.xml` to make any site or product citable by Perplexity, ChatGPT Search, Claude, and Gemini |

| Agent | What it produces |
|---|---|
| `resume-reviewer` | Scored feedback + improved resume |
| `resume-builder` | Resume built from your existing files |
| `company-researcher` | Structured research brief with red/green flags + customization notes |
| `resume-customizer` | JD-tailored resume (re-keyed, not fabricated) |
| `cover-letter-writer` | 3-paragraph targeted letter, 200–280 words |
| `interview-prepper` | STAR-outline behavioral Qs + technical Qs + questions to ask |

## Community

[**Discord**](https://discord.gg/babcVNJBet) — chat, help, show-and-tell · [**Issues**](https://github.com/JCodesMore/jobs-for-ai-agents/issues) — bugs & feature requests · [**Contribute**](CONTRIBUTING.md) · [**More plugins**](https://github.com/JCodesMore/jcodesmore-plugins)

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
git clone https://github.com/JCodesMore/jobs-for-ai-agents.git
cd jobs-for-ai-agents
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

[Apache License 2.0](LICENSE) — © 2026 JCodesMore

---

*Part of [jcodesmore-plugins](https://github.com/JCodesMore/jcodesmore-plugins).*
