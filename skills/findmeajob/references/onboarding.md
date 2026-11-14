# Onboarding — 3-question fast path (+ optional deepening)

Goal: get to a first search in under 60 seconds. Rest is optional and
captured opportunistically later in the conversation.

**Rule:** one question per turn. Conversational, not a form. If the user
answers more than one question in a single message, accept it and skip ahead.

## The fast path (3 questions)

### Q1 — Role and seniority in one sentence
> **What role are you hunting for?**
>
> One line is fine — I can read seniority out of it. For example:
> *"Senior data engineer, 7 years"* or *"Staff AI engineer, LLM infra"* or
> *"VP Product, B2B SaaS"*.

Accept free text. Parse seniority (entry/mid/senior/lead/exec) from the
answer. Only ask explicitly if ambiguous.

### Q2 — Location & remote in one
> **Where?** City, country, or `remote` — and whether you'll travel for
> hybrid days.
>
> Examples: *"remote, Europe timezone"*, *"NYC, hybrid 2 days"*,
> *"Berlin or remote"*, *"anywhere in the US"*.

Parse the string. Set `is_remote=true` if "remote" is the whole answer.
Capture a location string for JobSpy regardless.

### Q3 — Dealbreakers
> **Any dealbreakers?** Industries to skip, minimum salary, no on-call,
> visa sponsorship required, etc. Say "none" if nothing comes to mind.

Freeform. Store under `Notes:` in `preferences.md`.

**That's enough to run a first search.** Save the three answers to
`job-search/preferences.md` and move to Step 3 (resume) in the SKILL.md flow.

## Optional deepening (ask only if useful)

Trigger each of these *in context*, not upfront:

- **Employment type** — only if `job_type` would meaningfully narrow results
  (e.g. user mentioned "contract-to-hire" or "internship").
- **Industry** — only if the user hasn't named one and the first search comes
  back with too much variety.
- **Target companies** — ask when offering to run company research so the
  user can pre-seed a short list.
- **Salary target** — ask when presenting results so the scorer can sort
  compensation; many users prefer to see real listings before stating a number.

## Returning users

If `job-search/preferences.md` exists:

> **Welcome back.** I have you down for *[role]* in *[location]* — still
> accurate, or shall we tweak it?
>
> - **Yes, same** → jump to deep search
> - **Tweak a field** → quick edit
> - **Full reset** → run `/setup` to wipe and start over

Do not re-run the full questionnaire; the whole point is that we stored it.

## Saving `preferences.md`

```markdown
# Job Search Preferences

**Role:** [free-text role + seniority as given]
**Seniority (parsed):** entry | mid | senior | lead | exec
**Location:** [city/country/remote string]
**Remote:** yes | no | hybrid
**Employment Type:** [only if asked, else "Full-time (default)"]
**Salary Target:** [only if given]
**Industry:** [only if given]
**Dealbreakers / Notes:** [free text]

**Last Updated:** [YYYY-MM-DD]
```

Keep the schema stable — downstream agents (`resume-customizer`,
`company-researcher`) read these keys by name.
