"""Deep job search processor.

Takes raw search_jobs / search_jobs_batch result files, dedupes,
filters out wrong-domain titles and contract-only listings, scores by
fit signals from the user's preferences and resume, and writes a ranked
JSON shortlist consumed by the rest of the findmeajob workflow.

Usage:
  python process_jobs.py \
    --input file1.txt file2.txt ... \
    --profile  job-search/preferences.md \
    --resume   job-search/jane-doe-resume.md \
    --output   job-search/jobs-final.json \
    [--include-hybrid] \
    [--min-score 5]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any


# ---------------------------------------------------------------------------
# Title patterns
# ---------------------------------------------------------------------------

RELEVANT_TITLE = re.compile(
    r"software|developer|engineer|backend|frontend|full.?stack|sre|devops|"
    r"site reliability|platform|cloud|machine learning|deep learning|"
    r"\bllm\b|\bml\b|\bai\b|applied (ml|ai)|mlops|ai engineer|"
    r"data engineer|analytics engineer|data scientist|"
    r"principal engineer|staff engineer|senior engineer|"
    r"architect|infrastructure|reliability",
    re.I,
)

EXCLUDE_TITLE = re.compile(
    r"mechanical|civil|aerospace|biomedical|chemical|petroleum|optical|hvac|"
    r"maintenance|conveyance|sensing|service engineer|technician|nurse|"
    r"construction|sales engineer|pre.?sales|electrical eng|environmental eng|"
    r"field engineer|process engineer$|safety eng|"
    r"hardware engineer|firmware|embedded|robotics engineer$|qa engineer$|"
    r"quality eng|manufacturing|industrial eng|production eng|optical eng|"
    r"controls engineer|automation technician|network engineer$|"
    r"telecommunications|radio frequency|\brf engineer",
    re.I,
)

PM_PATTERN = re.compile(
    r"product manager|program manager|technical program manager|"
    r"project manager|scrum master",
    re.I,
)

CONTRACT_PATTERN = re.compile(
    r"\bcontract\b|\bc2c\b|w2/1099|corp.?to.?corp|long.?term contract|"
    r"contract opportunity|contract role|contract position|"
    r"1099|independent contractor",
    re.I,
)

HYBRID_PATTERN = re.compile(r"\bhybrid\b", re.I)

# ---------------------------------------------------------------------------
# Scoring signals
# ---------------------------------------------------------------------------

DEFAULT_AI_KW = [
    "ai engineer", "llm", "genai", "gen ai", "rag", "vector db",
    "embeddings", "mcp", "claude", "openai", "anthropic", "agent",
    "foundation model", "fine.?tun", "inference",
]
DEFAULT_ML_KW = ["machine learning", "deep learning", "artificial intelligence"]
DEFAULT_STACK_KW = ["typescript", "python", "react", "node.js", "next.js"]
DEFAULT_PENALTY_KW = [
    "cobol", "mainframe", "mumps", "vb.net", "powerbuilder",
    "salesforce developer", "apex developer", "sharepoint", "sap abap",
    "pl/sql developer",
]


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_jobs_from_path(path: str) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        raw = f.read().strip()
    data = json.loads(raw)

    # Raw JSON array
    if isinstance(data, list):
        return data

    # MCP tool-result wrapper: {"result": "<json-string>"}
    if isinstance(data, dict) and "result" in data:
        inner = data["result"]
        if isinstance(inner, str):
            inner = json.loads(inner)
        if isinstance(inner, list):
            return inner
        if isinstance(inner, dict):
            return inner.get("results") or []

    # search_jobs / search_jobs_batch native shape: {"count":N, "results":[...]}
    if isinstance(data, dict) and "results" in data:
        return data["results"] or []

    raise ValueError(f"Unexpected JSON shape in {path}")


def slim(j: dict[str, Any]) -> dict[str, Any]:
    return {
        "title":       j.get("title"),
        "company":     j.get("company"),
        "location":    j.get("location"),
        "date_posted": j.get("date_posted"),
        "job_url":     j.get("job_url"),
        "job_type":    j.get("job_type"),
        "is_remote":   j.get("is_remote"),
        "min_amount":  j.get("min_amount"),
        "max_amount":  j.get("max_amount"),
        "currency":    j.get("currency"),
        "interval":    j.get("interval"),
        "site":        j.get("site"),
        "desc_preview": (j.get("description") or "")[:1200],
    }


def dedupe(jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set = set()
    out = []
    for j in jobs:
        key = j.get("job_url") or f"{j.get('title')}||{j.get('company')}"
        if key in seen:
            continue
        seen.add(key)
        out.append(j)
    return out


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

def passes_filters(
    j: dict[str, Any],
    allow_hybrid: bool = False,
    allow_onsite: bool = False,
) -> bool:
    title = j.get("title") or ""
    desc = (j.get("desc_preview") or "")[:300]
    combined = title + " " + desc

    if not RELEVANT_TITLE.search(title):
        return False
    if EXCLUDE_TITLE.search(title):
        return False
    if PM_PATTERN.search(title):
        return False
    if CONTRACT_PATTERN.search(combined):
        return False

    is_remote = bool(j.get("is_remote"))
    is_hybrid = HYBRID_PATTERN.search(combined) is not None

    if allow_onsite:
        return True
    if allow_hybrid and (is_remote or is_hybrid):
        return True
    if is_remote:
        return True
    return False


# ---------------------------------------------------------------------------
# Resume keyword extraction
# ---------------------------------------------------------------------------

STACK_CANDIDATES = [
    "typescript", "javascript", "python", "react", "node.js", "next.js",
    "go", "golang", "rust", "c++", "c#", "java", "kotlin", "ruby", "rails",
    "django", "fastapi", "flask", "aws", "gcp", "azure", "kubernetes",
    "docker", "terraform", "postgres", "postgresql", "mongodb", "redis",
    "graphql", "grpc", "kafka", "spark", "pytorch", "tensorflow", "langchain",
    "dbt", "airflow", "snowflake", "databricks", "elasticsearch",
]


def extract_resume_keywords(resume_path: str | None) -> list[str]:
    if not resume_path or not os.path.exists(resume_path):
        return DEFAULT_STACK_KW
    with open(resume_path, encoding="utf-8") as f:
        text = f.read().lower()
    found = [k for k in STACK_CANDIDATES if k in text]
    return found or DEFAULT_STACK_KW


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score(j: dict[str, Any], stack_kw: list[str]) -> int:
    title = (j.get("title") or "").lower()
    desc = (j.get("desc_preview") or "").lower()
    text = title + " " + desc
    s = 0

    for kw in DEFAULT_AI_KW:
        if re.search(kw, text):
            s += 5
    for kw in DEFAULT_ML_KW:
        if kw in text:
            s += 3
    for kw in stack_kw:
        if kw in text:
            s += 2

    if "senior" in title:
        s += 2
    if "staff" in title or "principal" in title:
        s += 3
    if "lead" in title:
        s += 1
    if j.get("is_remote"):
        s += 2

    min_amt = j.get("min_amount") or 0
    if min_amt:
        s += 1
    if min_amt >= 100_000:
        s += 2
    if min_amt >= 150_000:
        s += 2
    if min_amt >= 200_000:
        s += 2

    for kw in DEFAULT_PENALTY_KW:
        if kw in text:
            s -= 4

    return s


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Dedupe, filter, score job results.")
    ap.add_argument("--input", nargs="+", required=True,
                    help="search_jobs result files (raw JSON or MCP tool-result wrapper)")
    ap.add_argument("--profile", help="Path to preferences.md (optional)")
    ap.add_argument("--resume", help="Path to base resume markdown (optional)")
    ap.add_argument("--output", required=True, help="Output path for ranked JSON")
    ap.add_argument("--include-hybrid", action="store_true",
                    help="Include hybrid roles (default: remote-only)")
    ap.add_argument("--include-onsite", action="store_true",
                    help="Include all locations (drops remote filter entirely)")
    ap.add_argument("--min-score", type=int, default=0,
                    help="Drop jobs with score below this threshold (default: 0)")
    args = ap.parse_args()

    raw: list[dict[str, Any]] = []
    for path in args.input:
        try:
            jobs = load_jobs_from_path(path)
            raw.extend(jobs)
            print(f"[info] loaded {len(jobs)} jobs from {path}")
        except Exception as exc:
            print(f"[warn] could not load {path}: {exc}", file=sys.stderr)

    print(f"[info] {len(raw)} total raw jobs")

    slimmed = [slim(j) for j in raw]
    deduped = dedupe(slimmed)
    print(f"[info] {len(deduped)} unique after dedupe")

    filtered = [
        j for j in deduped
        if passes_filters(j, allow_hybrid=args.include_hybrid, allow_onsite=args.include_onsite)
    ]
    print(f"[info] {len(filtered)} after title/remote/contract filters")

    stack_kw = extract_resume_keywords(args.resume)
    if args.resume and os.path.exists(args.resume):
        print(f"[info] stack keywords from resume: {stack_kw}")

    for j in filtered:
        j["_score"] = score(j, stack_kw)

    if args.min_score:
        before = len(filtered)
        filtered = [j for j in filtered if j["_score"] >= args.min_score]
        print(f"[info] {len(filtered)} after min-score={args.min_score} (dropped {before - len(filtered)})")

    filtered.sort(key=lambda x: -x["_score"])

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2)

    print(f"[done] wrote {len(filtered)} ranked jobs → {args.output}")
    print()
    print("Top 10 preview:")
    for i, j in enumerate(filtered[:10], 1):
        min_a = j.get("min_amount")
        max_a = j.get("max_amount")
        if min_a and max_a:
            salary = f"${min_a:,.0f}–${max_a:,.0f}"
        elif min_a:
            salary = f"${min_a:,.0f}+"
        else:
            salary = "no salary"
        remote = "remote" if j.get("is_remote") else "onsite/hybrid"
        print(f"  {i:>2}. [{j['_score']:>3}] {j['title']} @ {j['company']} | {salary} | {remote}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
