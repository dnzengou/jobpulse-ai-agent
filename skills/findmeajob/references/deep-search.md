# Deep Search Algorithm

Why deep search by default: a single `search_jobs` call with one term and `results_wanted=25` returns ~25 jobs and a lot of them are off-target (Mechanical Engineer when you searched "Software Engineer," Service Engineer in healthcare, etc.). Indeed's title matching is fuzzy. Running 4-6 query variations in parallel + scoring + filtering produces a much richer shortlist.

## Step 1 — Generate query variations

Pick 4-6 search terms. Always include:
- The user's literal role (e.g., `senior software engineer`)
- 2-3 related role names (e.g., `full stack engineer`, `backend engineer`, `platform engineer`)
- 1-2 specialty terms based on resume strengths (e.g., `AI engineer`, `machine learning engineer` if their resume shows AI/ML experience)

Skip variants the user has explicitly excluded (e.g., if they said "no Java," don't add `Java developer`).

## Step 2 — Run all queries in parallel

In a single message, fire all `search_jobs` calls. Parameters:

| Param | Value | Why |
|-------|-------|-----|
| `results_wanted` | `100` | More raw material to filter from |
| `hours_old` | `168` | 7 days — balances freshness with volume |
| `is_remote` | from preferences | |
| `job_type` | from preferences | |
| `country` | `usa` (or user's country) | |
| `site_name` | user's chosen sites, default `["indeed"]` only initially | LinkedIn often blocked; Glassdoor/ZipRecruiter/Google Jobs return empty in many runs. Indeed is the most reliable. Re-try other sites only if Indeed thin. |

**Expected behavior:** each query will likely return 100 jobs and exceed the context size limit. The MCP tool auto-saves to a file and returns its path in the error message. **Capture each file path** — these are the inputs to the processor.

## Step 3 — Process

Run the processor script with all the captured file paths:

```
python ${CLAUDE_PLUGIN_ROOT}/skills/findmeajob/scripts/process_jobs.py \
  --input <path1> <path2> ... <pathN> \
  --profile job-search/preferences.md \
  --resume job-search/[name]-resume.md \
  --output job-search/jobs-final.json
```

The script:

1. **Loads** every input file and parses the JSON-of-JSON shape JobSpy returns
2. **Slims** each record to the fields needed for ranking + display (title, company, location, salary, url, date, source, first 1000 chars of description)
3. **Dedupes** by `job_url` (falls back to title+company if URL missing)
4. **Filters titles**:
   - Keep: software / developer / engineer / backend / frontend / full.?stack / SRE / DevOps / architect / platform / cloud / ML / AI / LLM / data engineer / staff engineer / principal engineer
   - Drop: mechanical / civil / aerospace / biomedical / chemical / petroleum / optical / HVAC / maintenance / conveyance / sensing / service engineer (IS) / technician / nurse / construction / sales engineer / pre-sales / electrical eng / environmental eng / field eng / process eng / project engineer / safety eng / hardware eng / firmware / embedded / robotics / QA-only / quality eng / manufacturing / industrial / production
5. **Filters body**: drops contract listings (matches `contract|c2c|w2/1099|corp.?to.?corp` in title or first 300 chars of description)
6. **Drops Product Manager / Program Manager** roles even if they slipped through title relevance (they often score high for "AI Agents" without being engineering roles)
7. **Scores** each remaining job. See [Scoring](#scoring) below.
8. **Sorts descending** and writes to the output JSON.

## Scoring

The defaults bias toward AI-heavy senior generalist roles. Tune by passing `--weights` if a user has a different focus (e.g., pure infra, pure frontend).

| Signal | Points |
|--------|--------|
| Has AI/LLM keywords (ai engineer, llm, genai, rag, vector, mcp, claude, openai, agent) per match | +5 |
| Has ML keywords (machine learning, ml ‎, artificial intelligence) per match | +3 |
| Tech stack matches user's resume (typescript, python, react, node.js, next.js, etc.) per match | +2 |
| Title contains "senior" | +2 |
| Title contains "staff" or "principal" | +2 |
| `is_remote` true | +2 |
| Has any salary listed | +1 |
| Salary min ≥ $100k | +2 |
| Salary min ≥ $150k | +2 (cumulative with above) |
| Stack mismatch (cobol, mainframe, mumps, vb.net, powerbuilder, sharepoint, sap abap) per match | -4 |

The processor reads the user's resume to pull their actual stack signals — a Go developer gets `go`, `golang`, `kubernetes` boosted instead of the defaults.

## Step 4 — Tier and present

Use the scored output to build a tiered markdown table. See `job-results.md`.

## Re-running

If the user asks to refine, you don't need to re-search if the underlying data is fresh enough (< 24h old). Just re-run the processor with adjusted weights or filters and present a new table.

If they want fresher data, repeat from Step 1 with whatever new constraints they gave (different keywords, different sites, looser remote, etc.).
