"""
JobSpy MCP Server — thin scraping layer for the jobs-for-ai-agents plugin.

All intelligence (resume handling, company research, scoring) lives in
skills and agents. This server just scrapes and serializes.
"""

import json
import logging
from datetime import date, datetime
from typing import Optional

import pandas as pd
from mcp.server.fastmcp import FastMCP
from jobspy import scrape_jobs

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("jobspy-mcp")

mcp = FastMCP("JobSpy Job Search")

VALID_SITES = [
    "indeed", "linkedin", "glassdoor", "zip_recruiter",
    "google", "bayt", "naukri", "bdjobs",
]

VALID_JOB_TYPES = ["fulltime", "parttime", "internship", "contract"]

DEFAULT_SITES = ["indeed", "linkedin", "zip_recruiter", "google"]
DEFAULT_RESULTS = 15
DEFAULT_HOURS_OLD = 72
DEFAULT_DISTANCE = 50
DEFAULT_COUNTRY = "usa"

HOURLY_TO_ANNUAL = 2080  # 40h × 52w


def _serialize(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Not serializable: {type(obj)}")


def _normalize_salary(record: dict) -> dict:
    """Convert hourly wages to annualized estimates for consistent scoring."""
    interval = (record.get("interval") or "").lower()
    if interval == "hourly":
        for field in ("min_amount", "max_amount"):
            if record.get(field):
                record[field] = round(record[field] * HOURLY_TO_ANNUAL)
        record["interval"] = "yearly"
        record["salary_note"] = "annualized from hourly"
    return record


def _format_results(df: pd.DataFrame) -> str:
    cols = [
        "title", "company", "location", "date_posted", "job_url",
        "job_type", "is_remote", "min_amount", "max_amount",
        "currency", "interval", "site", "description",
    ]
    available = [c for c in cols if c in df.columns]
    records = df[available].to_dict(orient="records")

    for r in records:
        for k, v in r.items():
            if pd.isna(v):
                r[k] = None
        _normalize_salary(r)

    return json.dumps(
        {"count": len(records), "results": records},
        indent=2,
        default=_serialize,
    )


def _validate_sites(sites: list[str]) -> str | None:
    bad = [s for s in sites if s not in VALID_SITES]
    if bad:
        return f"Invalid site(s): {bad}. Valid: {VALID_SITES}"
    return None


@mcp.tool()
def search_jobs(
    search_term: str,
    location: str = "USA",
    site_name: Optional[list[str]] = None,
    results_wanted: int = DEFAULT_RESULTS,
    hours_old: int = DEFAULT_HOURS_OLD,
    job_type: Optional[str] = None,
    is_remote: bool = False,
    distance: int = DEFAULT_DISTANCE,
    country: str = DEFAULT_COUNTRY,
    description_format: str = "markdown",
) -> str:
    """
    Search for jobs across multiple job boards.

    Args:
        search_term: Keywords (e.g. 'senior python engineer', 'staff ml engineer')
        location: City/state or 'Remote'. E.g. 'Austin, TX', 'USA'
        site_name: Boards to search. Default: indeed, linkedin, zip_recruiter, google
        results_wanted: How many results (1–100)
        hours_old: Only jobs posted within this many hours
        job_type: fulltime | parttime | internship | contract
        is_remote: True for remote-only
        distance: Search radius in miles
        country: Country code for Indeed/Glassdoor (usa, uk, canada, etc.)
        description_format: markdown or html

    Returns:
        JSON with {count, results[]} — title, company, location, salary,
        job_url, description, site, date_posted, is_remote, job_type.
    """
    sites = site_name or DEFAULT_SITES

    err = _validate_sites(sites)
    if err:
        return json.dumps({"error": err})

    if job_type and job_type not in VALID_JOB_TYPES:
        return json.dumps({"error": f"Invalid job_type '{job_type}'. Valid: {VALID_JOB_TYPES}"})

    try:
        df = scrape_jobs(
            site_name=sites,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
            job_type=job_type,
            is_remote=is_remote,
            distance=distance,
            country_indeed=country,
            description_format=description_format,
        )

        if df.empty:
            return json.dumps({"count": 0, "results": [],
                               "message": "No results. Try broader terms, different sites, or larger hours_old."})

        return _format_results(df)

    except Exception as e:
        logger.error("search_jobs failed: %s", e)
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_jobs_batch(
    queries: list[dict],
    country: str = DEFAULT_COUNTRY,
) -> str:
    """
    Run multiple search_jobs queries and merge the results.

    Use this instead of calling search_jobs N times — one call, one context hit.

    Each query dict supports the same fields as search_jobs:
      search_term (required), location, site_name, results_wanted,
      hours_old, job_type, is_remote, distance.

    Args:
        queries: List of query dicts. E.g.:
          [
            {"search_term": "senior python engineer", "is_remote": true, "results_wanted": 50},
            {"search_term": "staff ml engineer", "is_remote": true, "results_wanted": 50},
            {"search_term": "backend engineer llm", "location": "San Francisco, CA", "results_wanted": 30}
          ]
        country: Country code for Indeed/Glassdoor (applies to all queries unless overridden)

    Returns:
        JSON with {total_queries, total_results, results[]} — merged, not deduped
        (dedup happens in process_jobs.py with URL-based dedup).
    """
    if not queries:
        return json.dumps({"error": "queries list is empty"})
    if len(queries) > 10:
        return json.dumps({"error": "Max 10 queries per batch call"})

    all_records: list[dict] = []
    query_summaries: list[dict] = []

    for i, q in enumerate(queries):
        term = q.get("search_term", "")
        if not term:
            query_summaries.append({"query": i + 1, "error": "missing search_term"})
            continue

        sites = q.get("site_name") or DEFAULT_SITES
        err = _validate_sites(sites)
        if err:
            query_summaries.append({"query": i + 1, "term": term, "error": err})
            continue

        try:
            df = scrape_jobs(
                site_name=sites,
                search_term=term,
                location=q.get("location", "USA"),
                results_wanted=q.get("results_wanted", DEFAULT_RESULTS),
                hours_old=q.get("hours_old", DEFAULT_HOURS_OLD),
                job_type=q.get("job_type"),
                is_remote=q.get("is_remote", False),
                distance=q.get("distance", DEFAULT_DISTANCE),
                country_indeed=q.get("country", country),
                description_format="markdown",
            )

            count = 0 if df.empty else len(df)
            query_summaries.append({"query": i + 1, "term": term, "found": count})

            if not df.empty:
                cols = [
                    "title", "company", "location", "date_posted", "job_url",
                    "job_type", "is_remote", "min_amount", "max_amount",
                    "currency", "interval", "site", "description",
                ]
                avail = [c for c in cols if c in df.columns]
                records = df[avail].to_dict(orient="records")
                for r in records:
                    for k, v in r.items():
                        if pd.isna(v):
                            r[k] = None
                    _normalize_salary(r)
                    r["_query_term"] = term
                all_records.extend(records)

        except Exception as e:
            logger.error("Batch query %d failed: %s", i + 1, e)
            query_summaries.append({"query": i + 1, "term": term, "error": str(e)})

    return json.dumps(
        {
            "total_queries": len(queries),
            "total_results": len(all_records),
            "query_summaries": query_summaries,
            "results": all_records,
        },
        indent=2,
        default=_serialize,
    )


@mcp.tool()
def get_supported_sites() -> str:
    """List all 8 supported job boards with descriptions."""
    sites = {
        "indeed": "Largest global engine — most reliable, fewest rate limits",
        "linkedin": "Professional network — quality listings, strict rate limits",
        "glassdoor": "Job listings + company reviews + salary data",
        "zip_recruiter": "Job matching platform — US/Canada focus",
        "google": "Aggregated listings from across the web",
        "bayt": "Middle East job portal",
        "naukri": "India's leading portal — includes skills and experience data",
        "bdjobs": "Bangladesh's premier job portal",
    }
    lines = [f"- **{k}**: {v}" for k, v in sites.items()]
    return "## Supported Job Boards\n\n" + "\n".join(lines)


@mcp.tool()
def get_supported_countries() -> str:
    """List supported countries for the country parameter."""
    try:
        from jobspy.model import Country
        countries = []
        for c in Country:
            names = c.value[0] if isinstance(c.value, tuple) else c.value
            countries.append(f"- **{c.name}**: {names}")
        return "## Supported Countries\n\n" + "\n".join(sorted(countries))
    except ImportError:
        return (
            "## Common Countries\n\nusa, uk, canada, australia, germany, "
            "france, india, singapore, brazil, mexico, japan, netherlands, "
            "sweden, ireland, new zealand"
        )


@mcp.tool()
def get_search_tips() -> str:
    """Get tips for effective job searching with this MCP server."""
    return """\
## Job Search Tips

**Search terms — be specific:**
- Role + level: "senior python engineer", "staff ml engineer", "principal backend engineer"
- Role + stack: "react typescript developer", "aws infrastructure engineer"
- Role + domain: "ai engineer llm", "backend engineer fintech", "platform engineer kubernetes"
- Try 4-6 variations via search_jobs_batch — single queries miss 70% of relevant postings

**Site selection:**
- Start: indeed + zip_recruiter + google (most reliable, fewest blocks)
- Add linkedin for quality but expect rate limits (~30% failure rate)
- Regional: bayt (Middle East), naukri (India), bdjobs (Bangladesh)

**Key filters:**
- hours_old=168 (7 days) for volume; hours_old=24 for freshness
- results_wanted=50-100 per query for deep search
- is_remote=True to filter at source; or omit and filter in process_jobs.py

**Batch search (recommended):**
  Use search_jobs_batch with 4-6 queries — one call, merged results,
  then run process_jobs.py for dedup/filter/score.

**No results?**
  Broaden search term, drop level qualifier, try different sites, increase hours_old.
"""


if __name__ == "__main__":
    mcp.run()
