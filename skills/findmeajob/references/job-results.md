# Job Results Presentation

Guidelines for presenting job search results to the user.

## Format — Markdown Table With Real Apply Links

**Always present results as a markdown table with clickable Apply links.** Never give the user JSON, never use placeholder `[Link]` text — pull the real `job_url` from each record.

The table groups jobs by tier so the user can scan quickly:

```markdown
### Top Matches for [role] — [N] roles found

#### 🥇 Top Tier (highest fit)

| # | Role | Company | Salary | Location | Posted | Apply |
|---|------|---------|--------|----------|--------|-------|
| 1 | Senior ML Engineer, LLM Distillation | **Waymo** | $213-263k | Mountain View, CA | 1d ago | [Apply](https://www.indeed.com/viewjob?jk=…) |
| 2 | Forward Deployed Engineer | **SuperAnnotate** | $175-250k | San Francisco, CA | 1d ago | [Apply](…) |

#### 🥈 Strong Matches

| # | Role | Company | Salary | Location | Posted | Apply |
|---|------|---------|--------|----------|--------|-------|
| 7 | Senior SWE, Backend (Mesh Traffic) | **Affirm** | $169-240k | Chicago, IL | 1d ago | [Apply](…) |

#### 🥉 Worth a Look

…
```

## Tiering Rules

Use the score from `process_jobs.py` to bucket:
- **🥇 Top Tier** — score ≥ 15 OR direct AI/LLM/agent role with senior+ title
- **🥈 Strong Matches** — score 8-14, recognizable companies, salary in range
- **🥉 Worth a Look** — score 5-7, smaller companies or partial fit

Show **at most ~15 in the main table.** Mention how many more are in the JSON file and offer to expand a tier.

## Salary Formatting

- Both bounds: `$213-263k`
- One bound: `$150k+`
- Missing: `not listed` (italic) — don't make up numbers

## Posted Date

Use relative time: `1d ago`, `3d ago`, `1w ago`. Pull from `date_posted`.

## Company Name Edge Cases

- If `company` is `None` or `null`, look at `desc_preview` for the actual company name and use that. Note `(verify in posting)` next to it.

## Rules

- **Never present JSON to the user as the deliverable** — it's a working artifact, not output.
- **Always include the real `job_url`** as a markdown link labeled "Apply".
- Group by relevance tier, not by source board.
- Keep one row per job; use parenthetical hints (`(fintech)`, `(hybrid Seattle)`, `(US Federal)`) for context that affects fit.
- If two listings are the same role at the same company in different cities, keep one and note the other locations inline: `Mountain View, CA · also Austin, TX`.
- Note salient flags inline: `(hybrid)`, `(equity)`, `(visa-friendly)`, `(US citizenship required)` when present in the description.

## After the Table

Always end with the selection prompt:

> **Which of these interest you?**
> - Pick numbers (e.g., "1, 3, 5")
> - Say **"top tier"** to take everything in the gold tier
> - Say **"all"** to keep everything
> - Say **"more"** to see ranks 16-30
> - Refine: tell me what to change (looser remote, different keywords, shorter window)
