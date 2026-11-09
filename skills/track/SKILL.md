---
name: track
description: Log and review job application outcomes — what you applied to, who responded, interviews scheduled, offers received, rejections. Local JSONL tracker at job-search/outcomes.jsonl. Use when the user says "track my applications", "log that I applied to X", "which companies haven't responded", or "show my application history".
---

# Application Tracker

You maintain a lightweight, local-only tracker of job-hunt outcomes. No spreadsheet. No cloud. One append-only JSONL file at `job-search/outcomes.jsonl`, written and read via the `log_outcome` and `list_outcomes` MCP tools.

Why this exists:

1. **For the user, today.** Answers "where am I in the funnel?" without maintaining a spreadsheet.
2. **For the project, over time.** The schema is stable enough that aggregate, consented analysis across users could one day measure real response-rate lift — honestly, instead of hallucinating a number. That consent prompt does not exist yet and will only ship with an explicit opt-in. See `SECURITY.md`.

## Event vocabulary

Each log entry is one of:

| Event | When to log |
|---|---|
| `shortlisted` | Job appeared in `jobs-final.json` (optional — logged automatically only if user asks) |
| `customized` | Agents produced the application package (research/resume/cover letter/interview prep) |
| `applied` | User (or `/apply`) submitted the application |
| `responded` | Recruiter/company replied in any form (auto-reject counts too — log as `rejected`) |
| `interview` | Phone screen / interview scheduled or completed |
| `offer` | Offer received |
| `rejected` | Rejection received |
| `withdrawn` | User pulled out |

Schema and additive-change policy: see `INTEGRATE.md` → "Trajectory / outcome log".

## Workflow — "log an outcome"

If the user says something like *"log that I applied to Monzo"* or *"got a rejection from Stripe"*:

1. Extract `company`, `role`, `event`. Ask for whatever is missing — in one short message, not a form.
2. If you've just written an application package in the same session, infer `source`, `score`, and `variant` from `job-search/[company-slug]/`.
3. Call `log_outcome` with the fields you have.
4. Confirm briefly:
   > Logged: **rejected** — Stripe (Senior PM). You're at 3 responses from 12 applications this month.

## Workflow — "show me my tracker"

If the user says *"show my application tracker"*, *"where am I behind?"*, *"how's the funnel looking?"*:

1. Call `list_outcomes` with a reasonable `limit` (50 by default).
2. Summarize in a short markdown table — never dump raw JSON.
3. Compute two numbers worth showing:
   - **Funnel**: applied → responded → interview → offer (counts).
   - **Stale**: applied ≥ 14 days ago, no later event for that company — nudge list.

Example output:

> **Application tracker** · last 30 days
>
> | Funnel | Count |
> |---|---|
> | Applied | 12 |
> | Responded | 4 |
> | Interview | 2 |
> | Offer | 0 |
>
> **Stale (no follow-up ≥ 14d):**
> - Monzo — Senior PM — applied 2026-10-21
> - Revolut — Product Lead — applied 2026-10-18
>
> Want me to draft a short follow-up email for either?

## Workflow — "which companies are still open?"

Everything with an `applied` event but no `rejected`, `offer`, or `withdrawn` event for the same `company`. Compute client-side from `list_outcomes` output.

## What you never do

- **Never send tracker data anywhere.** Reading and writing are local file operations. If a user asks you to "sync my tracker to X", say no — the project's privacy stance is in `SECURITY.md`.
- **Never fabricate entries.** Only log events the user confirmed, or events that happened within this same Claude Code session (an `/apply` submission you observed).
- **Never silently overwrite.** `log_outcome` appends. Rewriting history requires the user to say so explicitly; even then, just append a new entry with `event: "withdrawn"` or a corrective note rather than editing the file.

## Nudges (optional)

After `list_outcomes`, it's OK to proactively suggest one small next action — but only one, and only if stale items exist:

> You have 2 stale applications. Want me to draft a 2-line follow-up to the hiring manager at Monzo?

If the user says no, drop it. Don't nag.
