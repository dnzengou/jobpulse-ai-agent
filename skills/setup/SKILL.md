---
name: setup
description: Configure job finder plugin — manage preferences, reset data, change default settings. Use when the user wants to reconfigure the job finder, clear saved data, or adjust search defaults.
---

# Job Finder Setup

A utility for managing the job finder plugin's saved data and settings.

## Step 1 — Check Current State

Check what data exists:

```
ls job-search/ 2>/dev/null
cat job-search/preferences.md 2>/dev/null
```

## Step 2 — Present Options

> **Job Finder Setup**
>
> Here's what I can help with:
>
> **A) View preferences** — See your saved job search criteria
> **B) Edit preferences** — Update your search criteria
> **C) Reset everything** — Clear all saved data (preferences, resumes, research)
> **D) Manage resumes** — View or delete saved resumes
> **E) Configure defaults** — Change default job boards, result count, etc.

### If A (View):
Display the contents of `job-search/preferences.md` in a readable format.

### If B (Edit):
Show current preferences and ask which ones to change. Update `job-search/preferences.md`.

### If C (Reset):
Confirm with the user first:
> This will delete all saved preferences, resumes, and company research. Are you sure?

If confirmed, remove the `job-search/` directory.

### If D (Manage resumes):
List files in `job-search/` matching `*resume*`. Offer to view or delete specific ones.

### If E (Configure defaults):
Show current defaults and offer to change:
- Default job boards (which sites to search)
- Default number of results
- Default search radius
- Default country

Save to `job-search/preferences.md` under a `## Defaults` section.
