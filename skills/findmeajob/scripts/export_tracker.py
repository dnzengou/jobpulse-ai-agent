#!/usr/bin/env python3
"""
export_tracker.py — roll up all company folders under job-search/ into a
portable pipeline tracker (CSV + markdown dashboard).

Why: the per-company artefacts are the product; the pipeline view is the
commercial surface — the thing users paste into Notion, share with a
mentor, or export for a recruiter.

Standard library only — no new dependencies.

Usage:
    python export_tracker.py \\
        --root job-search \\
        --out  job-search/pipeline

Outputs:
    <out>.csv — one row per company folder
    <out>.md  — status dashboard grouped by status
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


STATUS_KEYWORDS = {
    # ordered: most advanced first wins when multiple appear
    "offer":        ["offer received", "offer letter", "accepted", "signed"],
    "final":        ["final round", "final interview", "exec interview", "onsite complete"],
    "interview":    ["interview scheduled", "interview on", "screening scheduled", "phone screen"],
    "applied":      ["applied on", "submitted on", "application sent", "applied"],
    "drafted":      ["draft", "to apply", "not applied"],
    "rejected":     ["rejected", "declined", "withdrew", "closed"],
}
STATUS_ORDER = ["offer", "final", "interview", "applied", "drafted", "rejected"]


@dataclass
class Row:
    company:    str
    role:       str = ""
    apply_url:  str = ""
    status:     str = "drafted"
    applied_on: str = ""
    has_research: bool = False
    has_resume:   bool = False
    has_cover:    bool = False
    has_prep:     bool = False
    notes:        str = ""


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _first_h1(text: str) -> str:
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return ""


def _match_role(text: str) -> str:
    # Heuristics: "**Role:** Senior AI Engineer" or "Position: X" or the h1
    m = re.search(r"(?mi)^\s*\*{0,2}(role|position|title)\*{0,2}\s*:\s*(.+)$", text)
    if m:
        return m.group(2).strip().strip("*").strip()
    return _first_h1(text)


def _match_apply_url(text: str) -> str:
    # Look for apply URLs in common shapes
    patterns = [
        r"(?mi)^\s*\*{0,2}apply\s*(url|link)\*{0,2}\s*:\s*(https?://\S+)",
        r"(?mi)^\s*apply:\s*(https?://\S+)",
        r"\[apply[^\]]*\]\((https?://[^\)]+)\)",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(m.lastindex).rstrip(")").rstrip(".")
    # Fallback: any URL on an "apply" line
    for line in text.splitlines():
        if "apply" in line.lower():
            m = re.search(r"https?://\S+", line)
            if m:
                return m.group(0).rstrip(").,")
    return ""


def _match_status(text: str) -> tuple[str, str]:
    """Return (status, applied_on_date)."""
    low = text.lower()
    applied_on = ""
    m = re.search(r"(?:applied|submitted)[^\n]{0,20}?(\d{4}-\d{2}-\d{2})", low)
    if m:
        applied_on = m.group(1)
    for key in STATUS_ORDER:
        for kw in STATUS_KEYWORDS[key]:
            if kw in low:
                return key, applied_on
    # If an apply_url is present but no keyword matched, treat as "applied"
    return "drafted", applied_on


def _notes(text: str) -> str:
    m = re.search(r"(?mi)^\s*\*{0,2}notes?\*{0,2}\s*:\s*(.+)$", text)
    if m:
        return m.group(1).strip().strip("*")
    return ""


def scan(root: Path) -> list[Row]:
    rows: list[Row] = []
    if not root.exists():
        return rows
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        # Skip non-company folders at job-search/ root
        if entry.name in {"__pycache__", ".git"} or entry.name.startswith("."):
            continue
        apply_md   = entry / "apply-link.md"
        research   = entry / "research.md"
        cover      = entry / "cover-letter.md"
        prep       = entry / "interview-prep.md"
        resumes    = list(entry.glob("*resume*"))

        if not any([apply_md.exists(), research.exists(), cover.exists(), prep.exists(), resumes]):
            continue

        text = _read(apply_md) + "\n" + _read(research)
        status, applied_on = _match_status(text)
        row = Row(
            company      = entry.name.replace("-", " ").title(),
            role         = _match_role(text),
            apply_url    = _match_apply_url(text),
            status       = status,
            applied_on   = applied_on,
            has_research = research.exists(),
            has_resume   = bool(resumes),
            has_cover    = cover.exists(),
            has_prep     = prep.exists(),
            notes        = _notes(text),
        )
        rows.append(row)
    return rows


def write_csv(rows: list[Row], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "company", "role", "status", "applied_on", "apply_url",
            "has_research", "has_resume", "has_cover", "has_prep", "notes",
        ])
        for r in rows:
            w.writerow([
                r.company, r.role, r.status, r.applied_on, r.apply_url,
                "Y" if r.has_research else "",
                "Y" if r.has_resume   else "",
                "Y" if r.has_cover    else "",
                "Y" if r.has_prep     else "",
                r.notes,
            ])


STATUS_EMOJI = {
    "offer":     "🟢 Offer",
    "final":     "🟣 Final round",
    "interview": "🔵 Interview",
    "applied":   "🟡 Applied",
    "drafted":   "⚪ Drafted",
    "rejected":  "🔴 Closed",
}


def write_md(rows: list[Row], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out = [
        "# Job-Search Pipeline",
        "",
        f"_Generated {today} · {len(rows)} companies tracked_",
        "",
    ]
    for key in STATUS_ORDER:
        bucket = [r for r in rows if r.status == key]
        if not bucket:
            continue
        out.append(f"## {STATUS_EMOJI[key]} — {len(bucket)}")
        out.append("")
        out.append("| Company | Role | Applied | Packages | Apply |")
        out.append("|---------|------|---------|----------|-------|")
        for r in bucket:
            pkg = "".join([
                "R" if r.has_research else "·",
                "r" if r.has_resume   else "·",
                "c" if r.has_cover    else "·",
                "i" if r.has_prep     else "·",
            ])
            link = f"[open]({r.apply_url})" if r.apply_url else "—"
            out.append(f"| {r.company} | {r.role or '—'} | {r.applied_on or '—'} | `{pkg}` | {link} |")
        out.append("")
    out += [
        "---",
        "",
        "Legend: `R`esearch · `r`esume · `c`over letter · `i`nterview prep.",
        "Edit `apply-link.md` in a company folder to change status (lines like",
        "`Status: interview scheduled` or `Applied on: 2026-11-05`).",
        "",
    ]
    path.write_text("\n".join(out), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="job-search", help="root folder (default: job-search)")
    ap.add_argument("--out",  default="job-search/pipeline", help="output base path without extension")
    args = ap.parse_args()

    root = Path(args.root)
    out  = Path(args.out)
    rows = scan(root)
    if not rows:
        print(f"No company folders found under {root}/ — nothing to export.")
        return 0

    csv_path = out.with_suffix(".csv")
    md_path  = out.with_suffix(".md")
    write_csv(rows, csv_path)
    write_md(rows, md_path)

    by_status = {k: 0 for k in STATUS_ORDER}
    for r in rows:
        by_status[r.status] = by_status.get(r.status, 0) + 1

    print(f"Exported {len(rows)} companies.")
    print(f"  CSV:       {csv_path}")
    print(f"  Dashboard: {md_path}")
    print("  By status:")
    for k in STATUS_ORDER:
        if by_status.get(k):
            print(f"    - {STATUS_EMOJI[k]}: {by_status[k]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
