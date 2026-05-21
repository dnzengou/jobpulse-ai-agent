# Jobs for AI Agents — Production Blueprint v0.4.0

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
       ├─ salary-negotiator (agent) ──→ market rate research + counter-offer email
       │
       ├─ linkedin-optimizer (agent) ──→ profile audit + section rewrites
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
  salary-negotiator.md     Market rate research, offer evaluation, counter-offer email + BATNA
  linkedin-optimizer.md    Profile audit, headline rewrite, About/Experience optimization

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
1. company-researcher              (independent — runs first)
   │
   ├─ 2. resume-customizer         (needs research.md)
   ├─ 3. cover-letter-writer       (needs research.md)
   └─ 4. interview-prepper         (needs research.md)

On offer received:
   5. salary-negotiator            (needs offer details from user + optional research.md)

Profile optimization (standalone — anytime):
   6. resume-reviewer              (needs base resume only)
   7. resume-builder               (scans user files)
   8. linkedin-optimizer           (needs base resume + LinkedIn profile text)
```

Agents 2, 3, 4 can run in parallel after agent 1 completes.
Agent 5 is triggered separately when user receives an offer.
Agents 6, 7, 8 can be invoked independently at any point in the workflow.

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
├── linkedin-optimized.md            ← LinkedIn profile optimization (standalone)
└── [company-slug]/
    ├── research.md
    ├── apply-link.md
    ├── [name]-resume-[slug].{md,pdf}
    ├── cover-letter.md
    ├── interview-prep.md
    └── salary-negotiation.md        ← On offer received
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
| `salary-negotiation.md` | Market rate data (P25/median/P75), offer evaluation, counter email draft, BATNA talking points |
| `linkedin-optimized.md` | Section audit scores, optimized headline, rewritten About, skills gap, completeness checklist |
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
| 0.4.0 | Generalized for public release: 2 new agents (salary-negotiator, linkedin-optimizer), 4-persona "Who it's for" section, comparison table vs. manual/LinkedIn Premium/ChatGPT, 7-item FAQ with accordion, 8 natural-language command cards, expanded deliverables grid (8 cards), metric strip updated (8 agents), vercel.json cleanup (remove deprecated name). |

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
**Deployment ID:** `dpl_HPHMp1yBeLQaWPzvwv6h9US4fTvV` *(v0.4.0, 2026-05-21)*
**Previous:** `dpl_BMHJgc6RfwWtiPhF5iPsrJAGDg3s` *(v0.3.2)*
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

## Tool Characterization

### What it is
JobPulse is a **Claude Code plugin** — a local-first, AI-powered job application pipeline.
It turns Claude into a personal recruiter + career strategist that runs entirely on the user's machine.

### What it does (end-to-end)
```
1. SEARCH   → Multi-board scrape (8 boards, batch queries, dedupe, score, rank)
2. RESEARCH → Per-company brief (culture, tech, red flags, resume customization notes)
3. TAILOR   → Resume re-keyed to JD vocabulary (never fabricates)
4. WRITE    → Cover letter (3 paragraphs, 200-280 words, company-specific opener)
5. PREP     → Interview guide (STAR outlines from resume, technical Qs, questions to ask)
6. NEGOTIATE → Salary playbook (market rates, counter email, BATNA)
7. OPTIMIZE → LinkedIn profile audit + section rewrites for recruiter visibility
8. APPLY    → Browser-assisted form fill with explicit user confirmation at each step
```

### What it is NOT
- Not a SaaS product (no server, no account, no database)
- Not a browser extension or standalone app
- Not a replacement for human judgment — it presents options, user decides
- Not a resume fabricator — all content grounded in user-provided facts

### Core invariants
- All user data stays on local disk (`job-search/`)
- No submit without explicit "submit" keyword
- No API keys required for scraping
- No telemetry or usage tracking
- All agent outputs are editable markdown / PDF

---

## Public Personas & Use Cases

JobPulse is designed for any professional, not just software engineers.

### Persona 1 — Tech Professional
**Profile:** Software engineer, AI/ML engineer, data scientist, DevOps, architect, engineering manager
**Search pattern:** Stack-matched keywords (Python, LLM, distributed systems...), remote-first, startup or FAANG
**Key agents:** company-researcher → resume-customizer → interview-prepper
**Niche:** process_jobs.py default scorer; salary-negotiator for competing offers

### Persona 2 — Business & BD Leader
**Profile:** Business development, sales, partnerships, growth manager, strategy
**Search pattern:** Domain BD scorer (`BIZ_DEV_KW`); startup BD, GTM, channel partners
**Key agents:** company-researcher → cover-letter-writer (relationship-focused opening) → salary-negotiator
**Niche:** Dual-track search (industry A + industry B) for versatile BD profiles

### Persona 3 — Niche Specialist
**Profile:** Space tech, deep tech, blockchain/Web3, climate, biotech, fintech innovation
**Search pattern:** Domain scorers (SPACE_KW, DEEPTECH_KW, BLOCKCHAIN_KW, INNOVATION_KW...)
**Key agents:** Full pipeline; 2-pass search strategy for thin markets
**Niche:** Direct-outreach guidance when boards capture < 30% of openings

### Persona 4 — Career Changer
**Profile:** Pivoting industries, re-entering workforce, upskilling to new domain
**Search pattern:** Transferable keyword extraction; broader title patterns; skills bridging
**Key agents:** resume-builder (extract transferable skills) → resume-customizer (bridge vocab gap) → interview-prepper (address career change narrative)
**Niche:** linkedin-optimizer adds biggest value here (reposition profile for new industry)

---

## Expansion Roadmap

### v0.4.x — Consolidation
- [ ] `process_jobs.py` multi-persona mode: `--persona tech|bd|niche|career-change`
- [ ] Auto-detect persona from resume content (no manual flag needed)
- [ ] Salary range normalization for non-USD currencies (SEK, EUR, GBP)
- [ ] PDF resume output improvements (better markdown-to-PDF rendering)

### v0.5.0 — Application tracker
- [ ] `job-search/tracker.md` — kanban-style table (Applied / Interview / Offer / Rejected)
- [ ] Auto-updated by `/apply` skill when form is submitted
- [ ] Weekly summary report: "You applied to 8 jobs. 3 responses. 1 interview scheduled."

### v0.6.0 — Referral & outreach
- [ ] `outreach-writer` agent — draft cold outreach to hiring managers / employees
- [ ] `referral-requester` agent — personalized referral ask based on LinkedIn connection research
- [ ] Generates LinkedIn DM + email variants

### v0.7.0 — Multi-language support
- [ ] Cover letter / resume bullets in target language (French, German, Spanish, Swedish...)
- [ ] Job description translation before scoring (for non-English JDs)
- [ ] Locale-aware salary normalization

### v0.8.0 — Continuous monitoring
- [ ] Scheduled re-scrape (cron via Claude Code hooks) for new postings matching saved preferences
- [ ] Alert summary: "5 new jobs match your profile since yesterday"
- [ ] Automated de-listing detection (job removed = application stale)

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

### Page sections (scroll order) — v0.4.0

```
1.  Nav           — sticky, logo + 5 links + pill CTA
2.  Hero          — animated badge (v0.4.0), h1, sub, trust line (any role/industry), 2 CTAs
3.  Metric strip  — 8 boards · 8 agents · 100% local · $0 · ∞ roles
4.  Who it's for  — 4 persona cards (Tech / Business & BD / Niche / Career Changer)
5.  Quick start   — 3 tagged steps (Install / Setup / Go) with code blocks + prereqs
6.  Terminal      — live /findmeajob demo (fintech PM scenario)
7.  Comparison    — feature table vs. manual / LinkedIn Premium / ChatGPT
8.  Try it        — 8 natural-language command cards (search, niche, resume, research,
                    negotiate, LinkedIn, cover letter, apply)
9.  Deliverables  — 8 output cards with filename tags (incl. salary-negotiation, linkedin-optimized)
10. FAQ           — 7-item accordion (JS progressive disclosure)
11. Boards strip  — 8 board chips
12. CTA final     — "Stop searching manually" + trust footer
13. Footer        — Blueprint v0.4.0 link
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

---

## Live Search Results — Sweden All-Tracks (2026-05-21)

*18 queries · Indeed + LinkedIn + Google · 30-day window*
*611 raw → 450 deduped → 169 relevance-filtered → scored by track*

### Search files
| File | Purpose |
|------|---------|
| `job-search/search_sweden_broad.py` | 18-query Sweden broad search script |
| `job-search/score_sweden_all_tracks.py` | All-tracks scorer (6 signal libraries + primary track assignment) |
| `job-search/raw_sweden_broad.json` | 419 raw results from this pass |
| `job-search/jobs-sweden-all-tracks.json` | 169 scored + ranked results |

### Curated shortlist

#### 🛰 Space Tech — Sweden
| Role | Company | Location | Score | Apply |
|------|---------|----------|-------|-------|
| Pre-sales Solution Architect | Swedish Space Corporation | Solna | 32 | [Indeed](https://se.indeed.com/viewjob?jk=c99b52bd524a827d) |
| Propulsion Product Manager | OHB Sweden AB | Stockholm | 24 | [Indeed](https://se.indeed.com/viewjob?jk=c339a7c26331aece) |
| Industrialiseringsledare — Aerospace Systems | Saab | Linköping | 20 | [LinkedIn](https://www.linkedin.com/jobs/view/4411680126) |
| Engineering Manager — Materials & Processes | GKN Aerospace | Trollhättan | 16 | [Indeed](https://se.indeed.com/viewjob?jk=3340712077c9ee59) |

#### ⛓ Blockchain/Web3 — Remote from Sweden
| Role | Company | Location | Score | Apply |
|------|---------|----------|-------|-------|
| Technical PM — Tether Wallet (100% Remote) | Tether Operations | Stockholm | 22 | [Indeed](https://se.indeed.com/viewjob?jk=3f73c6b429f8b833) |

#### 💡 Business Innovation — Sweden
| Role | Company | Location | Score | Apply |
|------|---------|----------|-------|-------|
| Customer Innovation Manager | AAK | Karlshamn | 11 | [LinkedIn](https://www.linkedin.com/jobs/view/4393491464) |
| R&D Manager — Hardware & Mechatronics | Husqvarna | Huskvarna | 11 | [Indeed](https://se.indeed.com/viewjob?jk=d8299b1dec6eebb0) |

#### 🤝 Business Development — Stockholm / Remote
| Role | Company | Location | Remote | Score | Apply |
|------|---------|----------|--------|-------|-------|
| Partner Onboarding Manager | Soundtrack Your Brand | Stockholm | ✅ | 11 | [Indeed](https://se.indeed.com/viewjob?jk=d386eefd85a12889) |
| Business Development Manager — MSP | TD SYNNEX | Solna | — | 13 | [Indeed](https://se.indeed.com/viewjob?jk=44e0828074407ddf) |
| Nordic Business Development Manager | TD SYNNEX | Solna | — | 9 | [Indeed](https://se.indeed.com/viewjob?jk=4d83fb4183e79480) |
| Global Head of Automotive & R&D Engineering | Luxoft | Remote, SE | ✅ | 10 | [Indeed](https://se.indeed.com/viewjob?jk=a9ffbec67e48ef21) |

#### ⚗️ Deep Tech / Cloud — Stockholm
| Role | Company | Location | Score | Apply |
|------|---------|----------|-------|-------|
| Principal TPM — AWS Digital Sovereignty & European Sovereign Cloud | Amazon Web Services | Stockholm | 9 | [Indeed](https://se.indeed.com/viewjob?jk=932d9689645e79a8) |

### Market signal
Board coverage for this profile in Sweden: ~25-30%. Recommended direct-outreach targets
not currently posting: Vinnova, RISE Research Institutes, Chalmers Ventures, KTH Innovation,
EIT InnoEnergy, Ignite Sweden, Epicenter Stockholm, SSAB R&D, Ericsson Ventures.

For blockchain specifically, Sweden's web3 scene is thin on boards —
active clusters in Stockholm: Safello, Arcane Crypto, BTSE alumni, and
Scandinavian crypto funds (Blocklabs, Hack VC EU).

### Scorer logic — `score_sweden_all_tracks.py`
6 signal libraries scored independently per job:
`SPACE_KW · DEEPTECH_KW · BLOCKCHAIN_KW · INNOVATION_KW · STARTUP_KW · BIZ_DEV_KW`
Primary track = library with highest raw score. Shared bonuses: remote (+3),
manager/director title (+2), senior/principal (+1), Sweden location (+1),
salary ≥ $100k (+2). Penalties: junior/entry-level/trainee (−5 each).
