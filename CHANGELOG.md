# Changelog

All notable changes to JobPulse AI Agent are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The source of truth for the current version is [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) → `"version"`.

## [Unreleased]

### Added
- `FACTS.md` — every public claim mapped to the code or doc that proves it.
- `llms.txt` and `ai.txt` at the repo root and under `public/` for AI-agent discoverability (per [llmstxt.org](https://llmstxt.org)).
- `CHANGELOG.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CITATION.cff`.
- `INTEGRATE.md` — how other agents, SDKs, apps, and CI call the MCP server.
- `/track` skill and `log_outcome` MCP tool — local JSONL application tracker (`job-search/outcomes.jsonl`) that doubles as the trajectory data for future skill evolution.
- Landing page: JSON-LD structured data (SoftwareApplication, FAQPage, HowTo), `robots.txt`, `sitemap.xml`, copy-to-clipboard on install commands, Twitter card meta, canonical URL.

### Fixed
- `mcp/test_server.py` imported function names that don't exist in `job_server.py`. Tests now import the real helpers (`_serialize`, `_format_results`, `_normalize_salary`, `_validate_sites`) and assert on the actual `{count, results}` return shape. Added coverage for salary annualization and site validation.
- `.claude-plugin/plugin.json` — `name`, `author`, `homepage`, `repository`, and `version` now match the real repository (`dnzengou/jobpulse-ai-agent`, `v0.4.0`).
- `README.md` — install instructions pointed at the wrong marketplace path and an outdated version badge.

## [0.4.0] — 2026-05-21

### Added
- Generalized scoring so non-tech roles (product, BD, sales, niche specialists, career changers) get useful rankings, not just software engineering.
- `salary-negotiator` and `linkedin-optimizer` agents.
- Jobs Radar positioning prior (`positioning-prior.md`) consumed by the resume customizer and cover-letter writer for consistent voice.
- Deployed landing page (`public/index.html`) via Vercel.

See [`BLUEPRINT.md`](BLUEPRINT.md) for the full v0.4.0 architecture.

## [0.3.2] — earlier 2026

### Added
- Onboarding UX redesign (one question at a time, not a form).
- Sweden all-tracks search results added to the blueprint.

## [0.3.1] — earlier 2026

### Added
- First production build. Three skills, six agents, one MCP server exposing five tools over 8 job boards.
- Browser-assisted apply skill — guided form-fill that never auto-submits.

## [0.3.0] — initial public commit

Initial import of the plugin scaffold.
