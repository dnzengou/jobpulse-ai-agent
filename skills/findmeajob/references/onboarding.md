# Onboarding Questionnaire

Ask these questions one at a time. Be conversational. Use multiple choice where possible.

## Questions

### 1. Role / Job Title
> What kind of role are you looking for?
>
> For example: "Software Engineer", "Product Manager", "Data Scientist", "Marketing Manager"

Accept free text. This becomes the `search_term` for JobSpy.

### 2. Location
> Where are you looking to work?
>
> A) Specific city/area (e.g., "San Francisco, CA")
> B) Anywhere in a country (e.g., "USA")
> C) Remote only
> D) Doesn't matter

If A: ask for the city/state. If C: set `is_remote=true`. If D: use "USA" as default.

### 3. Remote Preference
Only ask if they chose A or B above:
> Are you open to remote positions too, or only on-site/hybrid?
>
> A) Remote is fine
> B) On-site/hybrid only
> C) Remote only

### 4. Experience Level
> What's your experience level?
>
> A) Entry level / New grad (0-2 years)
> B) Mid-level (2-5 years)
> C) Senior (5-10 years)
> D) Lead / Staff / Principal (10+ years)
> E) Executive / Director

This helps with result relevance but doesn't directly map to a JobSpy parameter. Use it when presenting results and for resume context.

### 5. Employment Type
> What type of employment?
>
> A) Full-time (default)
> B) Part-time
> C) Contract
> D) Internship
> E) Open to any

Maps to JobSpy `job_type` parameter.

### 6. Salary Range (optional)
> Do you have a target salary range? (Optional — skip if you prefer)

If provided, note it for result filtering and resume context.

### 7. Industry (optional)
> Any specific industry? (Optional)
>
> For example: "fintech", "healthcare", "education", "e-commerce"

If provided, append to search term or use for result filtering.

### 8. Anything Else
> Anything else I should know? Specific companies you're targeting, skills you want to use, things you want to avoid?

Free text. Store any relevant notes in preferences.

## Saving Preferences

After collecting answers, write to `job-search/preferences.md`:

```
# Job Search Preferences

**Role:** [their answer]
**Location:** [their answer]
**Remote:** [yes/no/only]
**Experience Level:** [their answer]
**Employment Type:** [their answer]
**Salary Range:** [their answer or "Not specified"]
**Industry:** [their answer or "Any"]
**Notes:** [anything else they mentioned]

**Last Updated:** [date]
```
