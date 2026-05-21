# Jobs for AI Agents — Production Blueprint v0.3.1

*Updated: 2026-05-21*

---

## Purpose

A Claude Code plugin that automates the entire job application workflow:
search → shortlist → research → resume customization → cover letter → interview prep → browser-assisted apply.

Everything runs locally. Only job-board queries leave the machine.

---

## Architecture

```
User
  │
  └─ /findmeajob (skill)
       │
       ├─ search_jobs_batch (MCP tool) ──→ JobSpy → 8 job boards
       │
       ├─ process_jobs.py (Python) ──→ dedupe / filter / score / rank
       │
       ├─ company-researcher (agent) ──→ web search + browser-use
       │
       ├─ resume-customizer (agent) ──→ tailors base resume
       │
       ├─ cover-letter-writer (agent) ──→ 3-para targeted letter
       │
       ├─ interview-prepper (agent) ──→ STAR outlines + Q&A guide
       │
       └─ /apply (skill) ──→ browser-use → form fill + submit
```

---

## File Map

```
.claude-plugin/
  plugin.json              MCP server config + SessionStart hook

mcp/
  job_server.py            MCP server — search_jobs, search_jobs_batch,
                           get_supported_sites, get_supported_countries, get_search_tips
  pyproject.toml
  requirements.txt         mcp, python-jobspy, pandas

scripts/
  start-mcp.mjs            Launches Python MCP server via Node.js
  ensure-deps.mjs          SessionStart hook: creates .venv, installs deps (hash-cached)

skills/
  findmeajob/
    SKILL.md               Main workflow: onboarding → search → present → customize → apply
    scripts/
      process_jobs.py      Dedupe + filter + score pipeline
    references/
      onboarding.md        Questionnaire flow (one question at a time)
      deep-search.md       Search algorithm docs
      job-results.md       Results table format (tiered markdown with apply links)
  apply/
    SKILL.md               Browser-assisted application (fill + confirm + submit)
  setup/
    SKILL.md               Config management (view/edit prefs, reset data)

agents/
  resume-reviewer.md       Score + improve existing resume
  resume-builder.md        Build resume from user's files
  company-researcher.md    Company + JD deep dive; outputs research brief + customization notes
  resume-customizer.md     Tailor base resume for one specific job
  cover-letter-writer.md   3-paragraph targeted cover letter (200-280 words)
  interview-prepper.md     Behavioral Qs, STAR outlines, technical Qs, questions to ask

references/
  resume-best-practices.md  Content rules (DOs/DON'Ts, section order, bullets, ATS)
  resume-formatting.md      Format rules (fonts, margins, dates, file naming)
  company-evaluation-criteria.md  Research checklist + brief output format
  job-posting-analysis.md   How to extract requirements from JDs
```

---

## MCP Tools

| Tool | Purpose |
|------|---------|
| `search_jobs` | Single-query search across ≤8 job boards |
| `search_jobs_batch` | Multi-query search (4-10 queries, merged) — **preferred** |
| `get_supported_sites` | Lists all 8 boards with descriptions |
| `get_supported_countries` | Lists countries for Indeed/Glassdoor |
| `get_search_tips` | Best practices for queries and filters |

**search_jobs_batch** is the key performance win: one context hit instead of N, merged results with `_query_term` tag, then piped to process_jobs.py for scoring.

---

## process_jobs.py Pipeline

```
Input: 1+ result files (raw JSON array OR MCP tool-result wrapper OR {count, results} shape)
  │
  ├─ load_jobs_from_path()  — handles all 3 input shapes
  ├─ slim()                 — keeps 13 fields + 1200-char desc preview
  ├─ dedupe()               — URL-based (fallback: title+company)
  ├─ passes_filters()       — RELEVANT_TITLE + EXCLUDE_TITLE + PM + contract + remote/hybrid/onsite
  ├─ extract_resume_keywords()  — finds tech stack from resume for scoring
  └─ score()                — AI/ML keywords, stack match, seniority, salary, penalties

Output: ranked JSON array with _score field
```

### CLI flags

| Flag | Effect |
|------|--------|
| `--include-hybrid` | Accept hybrid roles (default: remote only) |
| `--include-onsite` | Accept all locations |
| `--min-score N` | Drop jobs scoring below N |

---

## Agent Dispatch Order (per selected job)

```
1. company-researcher         (independent — runs first)
   │
   ├─ 2. resume-customizer    (needs research.md)
   ├─ 3. cover-letter-writer  (needs research.md)
   └─ 4. interview-prepper    (needs research.md)
```

Agents 2, 3, 4 can run in parallel after agent 1 completes.

---

## Browser-Use Integration

Two entry points:

**company-researcher** — Uses browser-use to open job posting URLs for full JD extraction, and to browse company sites / Glassdoor / LinkedIn for research.

**`/apply` skill** — Full browser-assisted application:
1. Navigates to apply URL
2. Fills form fields section by section with user confirmation
3. Uploads customized PDF resume
4. Shows review summary before submit
5. Submits only on explicit "submit" keyword from user
6. Records application date in `apply-link.md`

Safety guarantees: Never submits without explicit "submit". Never fills SSN / bank / ID fields. Never invents data not from resume or confirmed by user.

---

## Data Storage (local, user's machine)

```
job-search/
├── preferences.md
├── [name]-resume.{md,pdf}
├── jobs-final.json
└── [company-slug]/
    ├── research.md
    ├── apply-link.md
    ├── [name]-resume-[slug].{md,pdf}
    ├── cover-letter.md
    └── interview-prep.md
```

---

## Design Principles

1. **Batch before score.** `search_jobs_batch` → `process_jobs.py` — never present raw JobSpy output.
2. **Agent-per-concern.** Each agent has a single, scoped responsibility with a defined input/output contract.
3. **No fabrication.** All resume/cover-letter agents work only with confirmed facts from the user's materials.
4. **Permission before action.** Browser apply requires two explicit confirmations (start + submit). Sensitive fields are flagged to user, not auto-filled.
5. **Local-first.** All user data written to `job-search/`. No external persistence.
6. **Reference-authoritative.** Agents load shared markdown references rather than encoding style preferences inline — single source of truth for resume standards.

---

## Example Deliverables per Job Application

| File | Content |
|------|---------|
| `research.md` | Company overview, role analysis, red/green flags, resume customization notes |
| `[name]-resume-[slug].pdf` | Base resume tailored to this JD (reordered, re-keyworded, factual) |
| `cover-letter.md` | 3-paragraph, 200-280 word targeted letter with company-specific opener |
| `interview-prep.md` | 5-6 behavioral Qs with STAR outlines, 3-5 technical Qs, questions to ask |
| `apply-link.md` | Apply URL + application status + date applied |

---

## Cost

All scraping uses python-jobspy (no API keys required for most boards). Web research uses Claude's built-in WebSearch. Browser-use uses Claude in Chrome (available in Claude Code). No external paid APIs required for core functionality.

Optional paid additions: Context7 MCP (live library docs), Playwright MCP (headless browser automation as alternative to Claude in Chrome).

---

## Version History

| Version | Changes |
|---------|---------|
| 0.1.0 | Initial release — findmeajob skill, 4 agents, JobSpy MCP |
| 0.2.0 | Deep search processor, tiered results table, setup skill |
| 0.3.0 | search_jobs_batch tool, salary normalization, cover-letter-writer agent, interview-prepper agent, /apply skill with browser-use, hybrid/min-score flags in processor, expanded title patterns, Karpathy-style agent prompts |
| 0.3.1 | Niche-role search patterns, custom domain scorers, two-pass strategy, European market guidance, blockchain/web3 profile support, JobSpy country limitations doc, landing page, Vercel/Netlify deploy, GitHub push |
| 0.3.2 | Worldmonitor-inspired onboarding UX redesign: benefit-first hero, 5-metric strip, 3-step quick start with tagged steps + prereqs, live terminal demo, natural language command cards, deliverables grid with filename tags, trust signals, animated live badge. Vercel production deploy. |

---

## Deployment

### Repository
- **GitHub:** https://github.com/dnzengou/jobpulse-ai-agent
- **Branch:** `main`

### Static landing page (`public/index.html`)
A self-contained HTML/CSS landing page. No build step, no dependencies.
Describes the plugin, shows a terminal demo, lists features, and provides install instructions.

### Vercel (preferred)
Config: `vercel.json` → serves `public/` as static output.

**Live URL:** https://jobpulse-ai-agent.vercel.app
**Deployment ID:** `dpl_BMHJgc6RfwWtiPhF5iPsrJAGDg3s`
**Region:** Washington D.C. (iad1)
**Status:** ✅ Production — auto-deploys on every push to `main`

```bash
vercel --prod --yes   # redeploy manually
```

### Netlify (alternative)
Config: `netlify.toml` → `publish = "public"`.

Deploy:
```bash
# One-time
npm i -g netlify-cli
netlify deploy --prod --dir public

# Or connect GitHub repo at app.netlify.com/start — auto-deploys on push
```

Live URL pattern: `https://jobpulse-ai-agent.netlify.app`

### What is and isn't deployed

| Deployed to Vercel/Netlify | NOT deployed |
|---------------------------|-------------|
| `public/index.html` (landing page) | MCP Python server (runs locally via Claude Code) |
| Static assets | Skills / agents / references (Claude Code plugin files) |
| | `job-search/` (user data, gitignored) |

The MCP server and plugin files are distributed via GitHub and installed with
`claude --plugin-dir .` or via the Claude Code plugin marketplace.
The Vercel/Netlify site is purely a marketing/documentation landing page.

---

## Niche-Role Search Playbook

*Derived from live Sweden / Europe space + deep tech searches (2026-05-21)*

### When process_jobs.py is the wrong scorer

`process_jobs.py` is tuned for software engineering roles. For non-SWE profiles
(innovation managers, BD leads, technology transfer, blockchain BD) use a
**domain-specific scorer** instead:

```
job-search/score_[domain].py    ← custom RELEVANT/EXCLUDE/score() for the domain
```

Pattern:
```python
RELEVANT = re.compile(r"[domain keywords]", re.I)
EXCLUDE  = re.compile(r"[noise titles]", re.I)
def score(j): ...  # domain-specific signals
```

### Two-pass search strategy

For niche roles in small markets (e.g. space in Scandinavia):

**Pass 1 — Targeted:** exact role terms, shorter window (14 days), remote filter on.
```
is_remote=True, hours_old=336, results_wanted=40
```

**Pass 2 — Broadened:** looser terms, longer window (30 days), no remote filter,
expanded geo (Europe vs. Sweden-only), drop `is_remote`.
```
is_remote=False, hours_old=720, results_wanted=30
```

Merge both passes → dedupe → domain scorer → rank.

### JobSpy country support notes

| Site | Sweden | Europe-wide | Notes |
|------|--------|-------------|-------|
| Indeed | ✅ `country_indeed="sweden"` | ✅ | Most reliable |
| LinkedIn | ✅ via location string | ✅ | Rate limits ~30% |
| Google Jobs | ✅ | ✅ | Good aggregation |
| Glassdoor | ❌ | Partial | No Sweden support — skip for SEK searches |
| Zip Recruiter | US/CA only | ❌ | Skip for European searches |

For European-scope searches use `country_indeed="uk"` with `location="Europe"`.

### Market concentration — space/deep tech Sweden

Job boards capture ~30% of space/deep tech openings in Sweden. Direct outreach
to key employers is often more effective:

| Company | Profile |
|---------|---------|
| OHB Sweden | Spacecraft systems prime |
| Swedish Space Corporation | Ground segment + launch services |
| RUAG / Beyond Gravity | Satellite structures |
| Saab Aeronautics/Space | Dual-use defence + space |
| Vinnova | National innovation agency — program managers |
| RISE Research Institutes | State deep tech commercialization |
| Chalmers Ventures / KTH Innovation | University spin-out ecosystems |

---

## User Profile — Active Search

*Stored in `job-search/preferences.md`. Reference for query generation.*

```
Role tracks:
  Track A: Space & Deep Tech Business Innovation Manager
  Track B: Blockchain Business Developer / Web3 BD

Profile signals:
  - Engineering background (technical credibility in deep tech / blockchain)
  - Startup experience (early-stage, ecosystem, venture)
  - Innovation toolbox (design thinking, lean startup, jobs-to-be-done,
    technology transfer, ecosystem building, partnerships)
  - Remote-first, Europe-wide open
  - Target market: remote roles; open to hybrid in major EU tech hubs

Query strategy:
  Track A: space BD + deep tech innovation + aerospace commercialization +
           frontier tech manager + ESA ecosystem + NewSpace startup
  Track B: blockchain BD + web3 partnerships + DeFi BD + crypto ecosystem +
           L2/protocol BD + tokenomics + decentralized finance startup

Scoring boosts (both tracks):
  - "startup" / "early-stage" / "scale-up"
  - "engineering" / "technical background" in JD
  - "remote" flag
  - Innovation methodology language
  - Salary transparency
```

---

## Dual-Track Search Template

When user has two profile tracks, run both in one session:

```python
# Pass 1 — Track A (space/deep tech)
queries_track_a = [
    "space technology business development remote Europe",
    "deep tech innovation manager remote",
    "new space commercialization manager",
    "aerospace business development manager Europe",
    "frontier tech BD manager startup",
    "innovation manager engineering deep tech",
]

# Pass 2 — Track B (blockchain/web3)
queries_track_b = [
    "blockchain business developer remote",
    "web3 business development manager remote",
    "blockchain ecosystem developer Europe",
    "DeFi business development remote",
    "crypto BD manager startup",
    "protocol business development blockchain",
]
```

Separate scorers per track → separate ranked lists → present in two sections.
Overlap (roles touching both: "blockchain space data", "web3 deep tech") surfaces
naturally from cross-track scoring.

---

## Landing Page — Onboarding UX Design System

*Inspired by worldmonitor-core.vercel.app. Live at https://jobpulse-ai-agent.vercel.app*

### Design principles applied

| Principle | Implementation |
|-----------|---------------|
| **Benefit-first** | Hero headline leads with outcome ("entire job hunt"), not features |
| **Friction signals upfront** | "No API keys · Your data stays local · Free · Runs in Claude Code" in hero |
| **Quantified credibility** | 5-metric strip (8 boards, 6 agents, 100% local, $0, 60s) immediately below hero |
| **Single CTA per section** | One primary action per scroll stop — no competing buttons |
| **Specificity over vagueness** | Named boards (Indeed, LinkedIn…), named agents, named output files |
| **Privacy reassurance** | Repeated: "your data stays local", "no cloud sync", "no telemetry" |

### Page sections (scroll order)

```
1. Nav          — sticky, logo + 4 links + pill CTA
2. Hero         — animated badge, h1, sub, trust line, 2 CTAs
3. Metric strip — 5 quantified numbers (boards, agents, local, cost, speed)
4. Quick start  — 3 tagged steps (Install / Setup / Go) with code blocks + prereqs
5. Terminal     — live demo of a full /findmeajob session
6. Try it       — 6 natural-language command cards with descriptions
7. Deliverables — 6 output cards with filename tags
8. Boards strip — 8 job board chips
9. CTA final    — repeat CTA with trust footer
10. Footer      — license, links
```

### Quick start step pattern

Each step uses a **tag + heading + explanation + code block** structure:

```
[INSTALL tag]  Step heading
               Explanation (why, not just what)
               > code block (copy-paste ready)
               Note (prerequisites / what to expect)
```

Tags: `INSTALL` (green) · `SETUP` (yellow) · `GO` (purple)

This pattern comes from worldmonitor: low cognitive load, clear progression,
no ambiguity about what to do next.

### Trust signal placement

Placed in 3 positions for maximum coverage:
1. **Hero trust line** — small icons + text just above CTAs
2. **Metric strip** — "100% Local" and "$0" as hard numbers
3. **CTA footer line** — "Apache 2.0 · No telemetry · No cloud sync · Your data stays yours"

### Files

| File | Purpose |
|------|---------|
| `public/index.html` | Single-file landing page (HTML + inline CSS, no build step) |
| `vercel.json` | Routes all traffic to `public/`, security headers |
| `netlify.toml` | Alternative deploy, `publish = "public"`, same headers |
