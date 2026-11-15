"""
Smoke tests for the JobSpy MCP server.

Verifies that the server imports cleanly, tools are registered, and helper
functions work correctly. Does NOT make real network calls to job boards —
that requires manual integration testing.

Run: python -m pytest mcp/test_server.py  (or) python mcp/test_server.py
"""

import json
import os
import tempfile
from datetime import date, datetime

import pandas as pd

from job_server import (
    VALID_EVENTS,
    VALID_JOB_TYPES,
    VALID_SITES,
    _format_results,
    _normalize_salary,
    _outcomes_path,
    _serialize,
    _slug,
    _validate_sites,
    get_search_tips,
    get_supported_sites,
    list_outcomes,
    log_outcome,
)


def test_serialize_handles_dates():
    assert _serialize(date(2026, 3, 31)) == "2026-03-31"
    assert _serialize(datetime(2026, 3, 31, 12, 0)) == "2026-03-31T12:00:00"


def test_serialize_rejects_other_types():
    try:
        _serialize("not a date")
    except TypeError:
        return
    raise AssertionError("Should have raised TypeError")


def test_format_results_empty():
    df = pd.DataFrame(columns=["title", "company", "job_url"])
    parsed = json.loads(_format_results(df))
    assert parsed == {"count": 0, "results": []}


def test_format_results_with_data():
    df = pd.DataFrame([{
        "title": "Software Engineer",
        "company": "Acme Corp",
        "location": "San Francisco, CA",
        "date_posted": date(2026, 3, 30),
        "job_url": "https://example.com/job/123",
        "job_type": "fulltime",
        "is_remote": False,
        "min_amount": 120000,
        "max_amount": 180000,
        "currency": "USD",
        "interval": "yearly",
        "site": "indeed",
        "description": "Build great software.",
    }])
    parsed = json.loads(_format_results(df))
    assert parsed["count"] == 1
    row = parsed["results"][0]
    assert row["title"] == "Software Engineer"
    assert row["company"] == "Acme Corp"
    assert row["min_amount"] == 120000
    assert row["date_posted"] == "2026-03-30"


def test_format_results_handles_nan():
    df = pd.DataFrame([{
        "title": "Designer",
        "company": "StartupXYZ",
        "location": "Remote",
        "min_amount": float("nan"),
        "max_amount": float("nan"),
    }])
    parsed = json.loads(_format_results(df))
    row = parsed["results"][0]
    assert row["min_amount"] is None
    assert row["max_amount"] is None


def test_normalize_salary_annualizes_hourly():
    r = _normalize_salary({"interval": "hourly", "min_amount": 60, "max_amount": 80})
    assert r["interval"] == "yearly"
    assert r["min_amount"] == 60 * 2080
    assert r["max_amount"] == 80 * 2080
    assert r["salary_note"] == "annualized from hourly"


def test_normalize_salary_passes_yearly_through():
    r = _normalize_salary({"interval": "yearly", "min_amount": 100000, "max_amount": 160000})
    assert r["min_amount"] == 100000
    assert r["max_amount"] == 160000
    assert "salary_note" not in r


def test_validate_sites_accepts_valid():
    assert _validate_sites(["indeed", "linkedin"]) is None


def test_validate_sites_rejects_invalid():
    err = _validate_sites(["indeed", "myspace"])
    assert err is not None and "myspace" in err


def test_valid_sites_list():
    for site in ("indeed", "linkedin", "glassdoor", "zip_recruiter",
                 "google", "bayt", "naukri", "bdjobs"):
        assert site in VALID_SITES
    assert len(VALID_SITES) == 8


def test_valid_job_types():
    assert VALID_JOB_TYPES == ["fulltime", "parttime", "internship", "contract"]


def test_get_supported_sites():
    out = get_supported_sites()
    assert "## Supported Job Boards" in out
    for site in VALID_SITES:
        assert site in out


def test_get_search_tips():
    out = get_search_tips()
    assert "## Job Search Tips" in out
    assert "Search terms" in out


def test_slug():
    assert _slug("Acme Corp, Inc.") == "acme-corp-inc"
    assert _slug("  Multi   spaces  ") == "multi-spaces"
    assert _slug("already-good") == "already-good"


def test_outcome_log_roundtrip(tmp_path=None):
    tmp_path = tmp_path or tempfile.mkdtemp(prefix="jobpulse-test-")
    os.environ["JOBPULSE_WORKDIR"] = str(tmp_path)
    try:
        path = _outcomes_path()
        if path.exists():
            path.unlink()

        rejected = json.loads(log_outcome(
            event="applied", company="Acme", role="Senior PM",
            source="indeed", score=22,
        ))
        assert rejected["ok"] is True
        assert rejected["appended"]["event"] == "applied"
        assert rejected["appended"]["company"] == "Acme"

        bad = json.loads(log_outcome(event="exploded", company="X", role="Y"))
        assert "error" in bad

        listing = json.loads(list_outcomes())
        assert listing["total"] == 1
        assert listing["returned"] == 1
        assert listing["entries"][0]["role"] == "Senior PM"

        log_outcome(event="responded", company="Acme", role="Senior PM")
        log_outcome(event="applied",   company="Other", role="Staff ML")
        filtered = json.loads(list_outcomes(event="applied"))
        assert filtered["returned"] == 2
        for e in filtered["entries"]:
            assert e["event"] == "applied"

        by_company = json.loads(list_outcomes(company="ACME"))
        assert by_company["returned"] == 2
        for e in by_company["entries"]:
            assert e["company"] == "Acme"
    finally:
        os.environ.pop("JOBPULSE_WORKDIR", None)


def test_valid_events_set():
    for e in ("applied", "responded", "interview", "offer", "rejected",
              "shortlisted", "customized", "withdrawn"):
        assert e in VALID_EVENTS


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t()
    print(f"All {len(tests)} tests passed!")
