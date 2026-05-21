"""
Smoke tests for the JobSpy MCP server.

Verifies that the server imports cleanly, tools are registered,
and helper functions work correctly. Does NOT make real network
calls to job boards — that requires manual integration testing.
"""

import json
from datetime import date, datetime

# Test date serializer
from job_server import _serialize_dates, _format_job_results, VALID_SITES, VALID_JOB_TYPES
import pandas as pd


def test_serialize_dates():
    assert _serialize_dates(date(2026, 3, 31)) == "2026-03-31"
    assert _serialize_dates(datetime(2026, 3, 31, 12, 0)) == "2026-03-31T12:00:00"
    try:
        _serialize_dates("not a date")
        assert False, "Should have raised TypeError"
    except TypeError:
        pass


def test_format_job_results_empty():
    df = pd.DataFrame()
    result = _format_job_results(df)
    parsed = json.loads(result)
    assert parsed == []


def test_format_job_results_with_data():
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
    result = _format_job_results(df)
    parsed = json.loads(result)
    assert len(parsed) == 1
    assert parsed[0]["title"] == "Software Engineer"
    assert parsed[0]["company"] == "Acme Corp"
    assert parsed[0]["min_amount"] == 120000


def test_format_job_results_handles_nan():
    df = pd.DataFrame([{
        "title": "Designer",
        "company": "StartupXYZ",
        "location": "Remote",
        "min_amount": float("nan"),
        "max_amount": float("nan"),
    }])
    result = _format_job_results(df)
    parsed = json.loads(result)
    assert parsed[0]["min_amount"] is None
    assert parsed[0]["max_amount"] is None


def test_valid_sites_list():
    assert "indeed" in VALID_SITES
    assert "linkedin" in VALID_SITES
    assert "glassdoor" in VALID_SITES
    assert "zip_recruiter" in VALID_SITES
    assert "google" in VALID_SITES
    assert "bayt" in VALID_SITES
    assert "naukri" in VALID_SITES
    assert "bdjobs" in VALID_SITES
    assert len(VALID_SITES) == 8


def test_valid_job_types():
    assert VALID_JOB_TYPES == ["fulltime", "parttime", "internship", "contract"]


def test_get_supported_sites():
    from job_server import get_supported_sites
    result = get_supported_sites()
    assert "## Supported Job Boards" in result
    for site in VALID_SITES:
        assert site in result


def test_get_search_tips():
    from job_server import get_search_tips
    result = get_search_tips()
    assert "## Job Search Tips" in result
    assert "Search terms" in result


if __name__ == "__main__":
    test_serialize_dates()
    test_format_job_results_empty()
    test_format_job_results_with_data()
    test_format_job_results_handles_nan()
    test_valid_sites_list()
    test_valid_job_types()
    test_get_supported_sites()
    test_get_search_tips()
    print("All tests passed!")
