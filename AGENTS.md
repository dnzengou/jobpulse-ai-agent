# Jobs for AI Agents Plugin

AI-powered job search assistant. Searches 8 job boards, handles resumes, researches companies, customizes applications, and optionally assists with browser-based form submission.

## MCP Tools

- `search_jobs` — Search one query across multiple job boards
- `search_jobs_batch` — Run 4-10 queries in one call, merged results (preferred for deep search)
- `get_supported_sites` — List all 8 supported job boards
- `get_supported_countries` — List supported countries
- `get_search_tips` — Search best practices

## Skills

Read the skill files in `skills/` for detailed workflow guidance:

- `skills/findmeajob/SKILL.md` — Main job search workflow (onboarding → search → research → customize → optionally apply)
- `skills/apply/SKILL.md` — Browser-assisted application — opens the form, fills fields with user confirmation, submits only on explicit "submit"
- `skills/setup/SKILL.md` — Configuration management (view/edit preferences, reset data, manage resumes)

## Agents

Agent instructions are in `agents/`:

- `agents/resume-reviewer.md` — Score and improve an existing resume
- `agents/resume-builder.md` — Build a resume from scratch by scanning the user's files
- `agents/company-researcher.md` — Deep-dive a company + job posting; produces a structured brief with Resume Customization Notes
- `agents/resume-customizer.md` — Tailor the base resume to a specific job using the research brief
- `agents/cover-letter-writer.md` — Write a targeted 3-paragraph cover letter (200-280 words)
- `agents/interview-prepper.md` — Generate role-specific behavioral + technical questions, STAR outlines, and questions to ask

## Reference Knowledge

Shared best practices in `references/`:

- `references/resume-best-practices.md` — Authoritative resume content rules
- `references/resume-formatting.md` — Formatting standards (fonts, margins, dates, bullets)
- `references/company-evaluation-criteria.md` — Research checklist + brief output format
- `references/job-posting-analysis.md` — How to extract real requirements from JDs

## Data Layout

All user data stays local in `job-search/`:

```
job-search/
├── preferences.md                           ← Search criteria (from onboarding)
├── [name]-resume.{md,pdf}                   ← Base resume
├── jobs-final.json                          ← Scored, ranked job shortlist
└── [company-slug]/
    ├── research.md                          ← Company research brief
    ├── apply-link.md                        ← Apply URL + application status
    ├── [name]-resume-[slug].{md,pdf}        ← Customized resume
    ├── cover-letter.md                      ← Targeted cover letter
    └── interview-prep.md                    ← Interview prep guide
```

## Typical Flow

```
/findmeajob
  → Onboarding (role, location, remote pref, salary, etc.)
  → Resume review or build (optional)
  → search_jobs_batch (4-7 queries, 50 results each)
  → process_jobs.py (dedupe, filter, score)
  → Ranked table presented to user
  → User selects jobs
  → Per job: company-researcher → resume-customizer + cover-letter-writer + interview-prepper
  → Delivery: research brief + customized resume + cover letter + interview prep + apply link
  → (Optional) /apply → browser-assisted form submission
```
