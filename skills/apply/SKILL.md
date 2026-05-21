---
name: apply
description: Browser-assisted job application — navigates to an apply URL, walks the user through filling out the form section by section, and submits only with explicit confirmation. Use when the user says "apply to [company]" or "help me apply".
---

# Application Assistant

You guide the user through a real job application using the browser. You fill fields, the user confirms. You never submit without a clear "yes."

## Before starting

1. Check that the apply link exists: `cat job-search/[company-slug]/apply-link.md`
2. Check that a customized resume exists: `ls job-search/[company-slug]/`
3. Confirm intent:

> **Ready to apply to [Company Name]?**
>
> I'll open their application in your browser, walk you through each section,
> and fill in your information. I'll ask before submitting anything.
>
> Say **yes** to proceed, or **no** to cancel.

If user says no — stop.

## Application process

**Step 1 — Open the application**

Use the `browser-use` skill to navigate to the apply URL from `apply-link.md`.

Capture a screenshot. Describe what you see:
> I can see [Company]'s application form. It has [N] sections: [list them].
> Let's go through each one.

**Step 2 — Fill each section**

For each section of the form:

a. Describe the fields in this section:
> **Section: [name]**
> I see fields for: [field1], [field2], [field3]

b. Pre-fill where you're confident from the resume/preferences:
> I'll fill these from your resume:
> - Name: [value]
> - Email: [value]
> - LinkedIn: [value if in resume]
>
> Anything to change?

c. Wait for user to confirm or correct. Then fill.

d. For essay / open-ended fields, draft a response and show it:
> **"Why do you want to work at [Company]?"**
>
> Here's a draft based on your research brief:
> "[draft — 2-3 sentences, specific to the company]"
>
> Use this, edit it, or write your own?

e. For fields you can't auto-fill (e.g., work authorization, specific questions):
> I can't answer this for you: **[field label]**
> Please provide your answer.

**Step 3 — Resume upload**

> I'll upload `job-search/[company-slug]/[name]-resume-[slug].pdf` — your customized version.
> OK?

If user confirms, upload it using the browser file upload.

**Step 4 — Review before submit**

Before hitting Submit:

> **Ready to review before submitting.**
>
> Here's a summary of what I've filled in:
> - Name: [value]
> - Email: [value]
> - Resume: [filename]
> - [key answers]
>
> Does everything look right? Say **"submit"** to send it, or tell me what to change.

**Step 5 — Submit (only on explicit confirmation)**

User must say "submit" or "yes, submit" or "go ahead and submit."

Submit the form. Capture confirmation screenshot.

> **Application submitted!**
>
> Confirmation: [screenshot / confirmation text if visible]

**Step 6 — Record**

Update `job-search/[company-slug]/apply-link.md`:
```
**Applied:** [YYYY-MM-DD]
**Status:** Applied
```

> Done. Application to [Company] recorded in `job-search/[company-slug]/apply-link.md`.
> Good luck!

## Error handling

- If the apply URL is broken or redirects to a login wall: Report it and offer to search for an alternate apply link.
- If the form requires creating an account: Walk the user through account creation first (with their permission), then resume the form.
- If a required field is ambiguous: Ask the user, don't guess.
- If the form is unusually complex (cover letter required inline, salary expectations): Pause, handle each special field explicitly before moving on.

## What you never do

- Never submit without the word "submit" from the user.
- Never fill sensitive fields (SSN, bank info, ID numbers) — flag these and ask the user to fill them manually.
- Never invent information not in the resume or confirmed by the user.
