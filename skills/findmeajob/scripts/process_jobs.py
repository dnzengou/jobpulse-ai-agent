"""Deep job search processor.

Takes raw search_jobs / search_jobs_batch result files, dedupes,
filters by track-specific rules, scores by fit signals from the user's
preferences and resume, and writes a ranked JSON shortlist consumed by
the rest of the findmeajob workflow.

Supports multiple role tracks (tech, product, sales-bd, ops, design,
any). Default is `any` — no title filter — so non-tech roles aren't
silently dropped, which was the case in v0.4.0.

Usage:
  python process_jobs.py \\
    --input file1.txt file2.txt ... \\
    --profile  job-search/preferences.md \\
    --resume   job-search/jane-doe-resume.md \\
    --output   job-search/jobs-final.json \\
    [--track tech|product|sales-bd|ops|design|any] \\
    [--include-hybrid] [--include-onsite] \\
    [--min-score 5]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Shared patterns
# ---------------------------------------------------------------------------

CONTRACT_PATTERN = re.compile(
    r"\bcontract\b|\bc2c\b|w2/1099|corp.?to.?corp|long.?term contract|"
    r"contract opportunity|contract role|contract position|"
    r"1099|independent contractor",
    re.I,
)

HYBRID_PATTERN = re.compile(r"\bhybrid\b", re.I)

SENIOR_TITLE = re.compile(r"\bsenior\b", re.I)
STAFF_TITLE = re.compile(r"\b(staff|principal)\b", re.I)
LEAD_TITLE = re.compile(r"\blead\b|\bhead of\b", re.I)
MANAGER_TITLE = re.compile(r"\b(manager|director|vp|vice president)\b", re.I)

# ---------------------------------------------------------------------------
# Tracks — one definition per target role family.
#
# `include` gates admission (match ⇒ keep). None = no include filter.
# `exclude` discards wrong-domain titles. None = no exclude filter.
# Keyword lists feed the scorer with weights set below.
# ---------------------------------------------------------------------------


@dataclass
class Track:
    name: str
    include: re.Pattern | None = None
    exclude: re.Pattern | None = None
    high_kw: list[str] = field(default_factory=list)   # +5 each
    medium_kw: list[str] = field(default_factory=list) # +3 each
    stack_kw: list[str] = field(default_factory=list)  # +2 each (also pulled from resume for tech)
    penalty_kw: list[str] = field(default_factory=list)


TECH = Track(
    name="tech",
    include=re.compile(
        r"software|developer|engineer|backend|frontend|full.?stack|sre|devops|"
        r"site reliability|platform|cloud|machine learning|deep learning|"
        r"\bllm\b|\bml\b|\bai\b|applied (ml|ai)|mlops|ai engineer|"
        r"data engineer|analytics engineer|data scientist|"
        r"principal engineer|staff engineer|senior engineer|"
        r"architect|infrastructure|reliability",
        re.I,
    ),
    exclude=re.compile(
        r"mechanical|civil|biomedical|chemical|petroleum|hvac|"
        r"maintenance|conveyance|service engineer|technician|nurse|"
        r"construction|electrical eng|environmental eng|"
        r"field engineer|process engineer$|safety eng|"
        r"\bqa engineer$|quality eng|manufacturing|industrial eng|"
        r"production eng|controls engineer|automation technician|"
        r"telecommunications|product manager|program manager|project manager|"
        r"scrum master",
        re.I,
    ),
    high_kw=[
        "ai engineer", "llm", "genai", "gen ai", "rag", "vector db",
        "embeddings", "mcp", "claude", "openai", "anthropic", "agent",
        "foundation model", "fine.?tun", "inference",
    ],
    medium_kw=["machine learning", "deep learning", "artificial intelligence"],
    stack_kw=["typescript", "python", "react", "node.js", "next.js"],
    penalty_kw=[
        "cobol", "mainframe", "mumps", "vb.net", "powerbuilder",
        "salesforce developer", "apex developer", "sharepoint", "sap abap",
        "pl/sql developer",
    ],
)

PRODUCT = Track(
    name="product",
    include=re.compile(
        r"product manager|product owner|product lead|head of product|"
        r"vp product|vp of product|chief product|director of product|"
        r"group product|principal pm|staff pm|senior pm|product strategist|"
        r"product designer|product marketing",
        re.I,
    ),
    exclude=re.compile(
        r"product engineer|product tester|product specialist $|"
        r"warehouse|retail associate",
        re.I,
    ),
    high_kw=[
        "roadmap", "product strategy", "zero to one", "product-led",
        "user research", "north star", "okrs", "mvp", "experimentation",
        "prd", "jobs to be done", "jtbd",
    ],
    medium_kw=[
        "stakeholder", "cross-functional", "go-to-market", "metrics",
        "analytics", "a/b test", "customer discovery",
    ],
    stack_kw=["sql", "amplitude", "mixpanel", "looker", "tableau", "figma"],
    penalty_kw=["associate product manager", "junior product"],
)

SALES_BD = Track(
    name="sales-bd",
    include=re.compile(
        r"business development|partnerships?|account executive|\bae\b|"
        r"\bbdr\b|\bsdr\b|sales manager|sales lead|head of sales|vp sales|"
        r"vp of sales|director of sales|growth manager|growth lead|"
        r"enterprise sales|strategic partnerships|channel",
        re.I,
    ),
    # Nothing to hard-exclude — sales titles are usually well-labelled.
    exclude=None,
    high_kw=[
        "quota", "pipeline", "closed-won", "enterprise", "saas sales",
        "arr", "mrr", "net new", "channel partners", "go-to-market",
    ],
    medium_kw=[
        "crm", "salesforce", "hubspot", "outbound", "inbound",
        "lead generation", "deal cycle",
    ],
    stack_kw=["salesforce", "hubspot", "outreach", "gong", "linkedin sales navigator"],
    penalty_kw=["door-to-door", "mlm", "cold calling only"],
)

OPS = Track(
    name="ops",
    include=re.compile(
        r"operations|coo|chief of staff|business operations|revops|rev ops|"
        r"finance operations|people operations|hrbp|hr manager|"
        r"supply chain|logistics|program ops|strategy manager|strategy lead",
        re.I,
    ),
    exclude=re.compile(r"warehouse operator|machine operator|forklift", re.I),
    high_kw=[
        "process improvement", "operational excellence", "scaling",
        "systems thinking", "org design", "p&l", "forecasting",
    ],
    medium_kw=[
        "cross-functional", "stakeholder", "sop", "kpis", "dashboarding",
        "financial modeling",
    ],
    stack_kw=["sql", "excel", "google sheets", "looker", "tableau", "notion"],
    penalty_kw=[],
)

DESIGN = Track(
    name="design",
    include=re.compile(
        r"designer|design lead|design manager|design director|ux|ui|"
        r"product design|brand design|graphic design|motion design|"
        r"design systems",
        re.I,
    ),
    exclude=re.compile(r"interior design|fashion design|floral", re.I),
    high_kw=[
        "design systems", "prototyping", "figma", "user research",
        "accessibility", "wcag", "interaction design", "visual design",
    ],
    medium_kw=["ui", "ux", "wireframing", "usability", "critique"],
    stack_kw=["figma", "sketch", "framer", "principle", "after effects"],
    penalty_kw=[],
)

ANY = Track(
    name="any",
    # No include filter, no exclude filter.
    # Contract filter still runs and scoring still applies.
    high_kw=[],
    medium_kw=[],
    stack_kw=[],
    penalty_kw=[],
)

TRACKS: dict[str, Track] = {
    "tech": TECH,
    "product": PRODUCT,
    "sales-bd": SALES_BD,
    "ops": OPS,
    "design": DESIGN,
    "any": ANY,
}


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_jobs_from_path(path: str) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        raw = f.read().strip()
    data = json.loads(raw)

    if isinstance(data, list):
        return data

    if isinstance(data, dict) and "result" in data:
        inner = data["result"]
        if isinstance(inner, str):
            inner = json.loads(inner)
        if isinstance(inner, list):
            return inner
        if isinstance(inner, dict):
            return inner.get("results") or []

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
# Filter and score
# ---------------------------------------------------------------------------

def passes_filters(
    j: dict[str, Any],
    track: Track,
    allow_hybrid: bool = False,
    allow_onsite: bool = False,
) -> bool:
    title = j.get("title") or ""
    desc = (j.get("desc_preview") or "")[:300]
    combined = title + " " + desc

    if track.include is not None and not track.include.search(title):
        return False
    if track.exclude is not None and track.exclude.search(title):
        return False
    if CONTRACT_PATTERN.search(combined):
        return False

    is_remote = bool(j.get("is_remote"))
    is_hybrid = HYBRID_PATTERN.search(combined) is not None

    if allow_onsite:
        return True
    if allow_hybrid and (is_remote or is_hybrid):
        return True
    return bool(is_remote)


def score(j: dict[str, Any], track: Track, stack_kw: list[str]) -> int:
    title = (j.get("title") or "").lower()
    desc = (j.get("desc_preview") or "").lower()
    text = title + " " + desc
    s = 0

    for kw in track.high_kw:
        if re.search(kw, text):
            s += 5
    for kw in track.medium_kw:
        if kw in text:
            s += 3
    for kw in stack_kw:
        if kw in text:
            s += 2

    if SENIOR_TITLE.search(title):
        s += 2
    if STAFF_TITLE.search(title):
        s += 3
    if LEAD_TITLE.search(title):
        s += 2
    if MANAGER_TITLE.search(title) and track.name != "tech":
        s += 2
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

    for kw in track.penalty_kw:
        if kw in text:
            s -= 4

    return s


# ---------------------------------------------------------------------------
# Resume keyword extraction (tech track only — other tracks ignore the resume
# for stack-level boosts since their keyword vocabulary is different)
# ---------------------------------------------------------------------------

_STACK_CANDIDATES = [
    "typescript", "javascript", "python", "react", "node.js", "next.js",
    "go", "golang", "rust", "c++", "c#", "java", "kotlin", "ruby", "rails",
    "django", "fastapi", "flask", "aws", "gcp", "azure", "kubernetes",
    "docker", "terraform", "postgres", "postgresql", "mongodb", "redis",
    "graphql", "grpc", "kafka", "spark", "pytorch", "tensorflow", "langchain",
    "dbt", "airflow", "snowflake", "databricks", "elasticsearch",
]


def extract_stack_keywords(resume_path: str | None, track: Track) -> list[str]:
    if track.name != "tech" or not resume_path or not os.path.exists(resume_path):
        return track.stack_kw
    with open(resume_path, encoding="utf-8") as f:
        text = f.read().lower()
    found = [k for k in _STACK_CANDIDATES if k in text]
    return found or track.stack_kw


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
    ap.add_argument("--track", choices=sorted(TRACKS.keys()), default="any",
                    help="Role track for filter + scoring (default: any — no title filter)")
    ap.add_argument("--include-hybrid", action="store_true",
                    help="Include hybrid roles (default: remote-only)")
    ap.add_argument("--include-onsite", action="store_true",
                    help="Include all locations (drops remote filter entirely)")
    ap.add_argument("--min-score", type=int, default=0,
                    help="Drop jobs with score below this threshold (default: 0)")
    args = ap.parse_args()

    track = TRACKS[args.track]

    raw: list[dict[str, Any]] = []
    for path in args.input:
        try:
            jobs = load_jobs_from_path(path)
            raw.extend(jobs)
            print(f"[info] loaded {len(jobs)} jobs from {path}")
        except Exception as exc:
            print(f"[warn] could not load {path}: {exc}", file=sys.stderr)

    print(f"[info] {len(raw)} total raw jobs · track={track.name}")

    slimmed = [slim(j) for j in raw]
    deduped = dedupe(slimmed)
    print(f"[info] {len(deduped)} unique after dedupe")

    filtered = [
        j for j in deduped
        if passes_filters(j, track,
                          allow_hybrid=args.include_hybrid,
                          allow_onsite=args.include_onsite)
    ]
    print(f"[info] {len(filtered)} after track/remote/contract filters")

    stack_kw = extract_stack_keywords(args.resume, track)
    if args.resume and os.path.exists(args.resume) and track.name == "tech":
        print(f"[info] stack keywords from resume: {stack_kw}")

    for j in filtered:
        j["_score"] = score(j, track, stack_kw)
        j["_track"] = track.name

    if args.min_score:
        before = len(filtered)
        filtered = [j for j in filtered if j["_score"] >= args.min_score]
        print(f"[info] {len(filtered)} after min-score={args.min_score} (dropped {before - len(filtered)})")

    filtered.sort(key=lambda x: -x["_score"])

    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
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
