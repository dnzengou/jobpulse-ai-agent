---
name: agent-seo
description: Make a site, product, or deliverable legible to AI agents — crawlers (GPTBot, ClaudeBot, PerplexityBot), answer engines (Perplexity, Arc Search, ChatGPT Search, Gemini, Claude), and tool-using agents (browser, retrieval, deep research). Emits llms.txt, agents.json, JSON-LD (Organization, SoftwareApplication, FAQ, HowTo, JobPosting, Article), robots.txt, sitemap.xml, and a canonical/OG block tuned for GEO (generative engine optimization) and AEO (answer engine optimization). Trigger when the user wants to "appear in AI answers", "optimize for ChatGPT/Perplexity/Claude", "add llms.txt", "structured data", "schema.org", "GTM for AI", "AI SEO", or wants a product page / landing page to be ingestible by agents.
---

# Agent-SEO — Make it legible to AI

Classic SEO ranks pages for human readers who skim ten blue links. Agent-SEO
ships the facts an AI agent needs to *cite your product in an answer*. The two
jobs overlap in HTML, but the output artefacts and the writing register are
different.

This skill is portable. Run it on the plugin's own landing page, on a client
site, on a product spec, or standalone to produce the files a new site needs.

## What "good" looks like

An answer engine asked *"What tool helps me tailor my resume for a specific
job from Claude Code?"* should:

1. **Retrieve** the site (robots.txt allows the bot, sitemap.xml lists the page).
2. **Parse** the page cheaply (`llms.txt` summarizes it in plain prose).
3. **Cite** the facts correctly (JSON-LD gives it the product name, offer, URL).
4. **Hand control** to a tool-using agent that can install it (`agents.json`
   names the install command and the entry point).

A site that lands all four appears in answers; one that lands two does not.

## The nine artefacts

Produce these for any site/product this skill is run against. Use the
templates in `references/` as starting points — they carry working schemas and
a brand-neutral palette of fields.

| # | File | Purpose | Reference |
|---|------|---------|-----------|
| 1 | `llms.txt` (root) | Plain-prose summary + key links, agent-first | `references/llms-txt.md` |
| 2 | `llms-full.txt` (root, optional) | Expanded version for deep retrieval | `references/llms-txt.md` |
| 3 | `agents.json` (root) | Install command, entry points, tool list — the "package.json for agents" | `references/agents-json.md` |
| 4 | `robots.txt` (root) | Explicitly allow AI crawlers you want; deny only what you must | `references/robots-txt.md` |
| 5 | `sitemap.xml` (root) | Every canonical URL with `lastmod` | `references/sitemap.md` |
| 6 | JSON-LD `<script type="application/ld+json">` blocks in each page | Organization, SoftwareApplication, Product, FAQPage, HowTo, Article, JobPosting | `references/json-ld.md` |
| 7 | Canonical + OG + Twitter meta in `<head>` | One canonical per URL; OG image 1200×630 | `references/head-meta.md` |
| 8 | FAQ block visible in-page | FAQPage JSON-LD + human-readable Q/A under an `<h2>FAQ</h2>` | `references/json-ld.md` |
| 9 | Citations footer | "How to cite this page" block with a one-sentence summary and the canonical URL | `references/citations.md` |

All nine are static. They cost nothing to host, add no JS, and work behind any
CDN.

## Process

1. **Inventory.** List the pages the user wants indexed and the one-line value
   proposition for each. Ask if the pitch isn't in context yet.
2. **Pick the schemas.** Every product landing page gets `Organization` +
   `SoftwareApplication` (or `Product`). Add `FAQPage` if there's a Q&A block.
   Add `HowTo` for any "install in N steps" section. Add `JobPosting` only for
   actual job listings. Do not stack schemas that do not match on-page content
   — answer engines penalize mismatched structured data.
3. **Write `llms.txt` first.** It is the single most-read file by agents today.
   Keep it under 400 lines. Lead with a one-sentence thesis, then a bulleted
   "What it does", then "How to install" (plain commands), then "Where the
   docs live" (links), then "Who to contact" (email or form URL).
4. **Fill the schemas.** Copy from `references/json-ld.md`, swap the values,
   validate with `https://validator.schema.org/` before ship.
5. **Update `robots.txt` and `sitemap.xml`.** Explicitly `Allow` the AI bots
   worth welcoming (list in `references/robots-txt.md`). Do not leave `robots.txt`
   silent — some agent crawlers refuse to fetch sites with no robots.
6. **Write the FAQ.** Answer the three questions a user types into Perplexity
   or ChatGPT before buying. Each answer is 1–2 sentences, cites a concrete
   fact, and ends with a link to the page that proves the claim.
7. **Add the citations footer.** One sentence + canonical URL. An answer engine
   writes citations from whatever is most quotable; give it a quotable line.
8. **Validate.**
   - `curl -A 'ClaudeBot' <url>` — does the bot get the same HTML a browser does?
     (Server-rendered content wins; JS-rendered loses.)
   - Paste the JSON-LD into `https://validator.schema.org/`.
   - Open the page in Perplexity / Claude / ChatGPT Search and ask a question
     the page answers. If the engine does not cite you, something is missing.

## Writing register for agent-SEO copy

- **Facts, not adjectives.** "Searches 8 job boards" beats "comprehensive job
  search." Agents extract numerals and proper nouns; adjectives are discarded.
- **One claim per sentence.** Nested claims get truncated.
- **Named entities on first mention.** "Claude Code" not "the assistant",
  "Vercel" not "the host" — agents build knowledge graphs from proper nouns.
- **Avoid marketing clichés.** "Revolutionize", "unlock", "seamless", "synergy"
  are stop-worded in LLM extraction pipelines. They do not help a human either.
- **Short URLs.** Agents cite shorter canonical URLs more often.

## Output

The skill produces, per target site:

- Updated `<site>/public/llms.txt` (+ optional `llms-full.txt`)
- Updated `<site>/public/agents.json`
- Updated `<site>/public/robots.txt`
- Updated `<site>/public/sitemap.xml`
- Updated `<head>` of each HTML page (canonical, OG, Twitter, JSON-LD scripts)
- A FAQ section with matching `FAQPage` JSON-LD
- A citations footer

Report back as a short checklist: artefacts produced, validator links hit,
one-sentence next action. The artefact files are the deliverable; the chat
summary is navigation.

## When to say no

Decline to apply agent-SEO to pages that **misrepresent** the product (fake
schemas, invented FAQ answers, fabricated reviews, inflated `aggregateRating`).
Answer engines detect mismatched structured data and will down-rank the site
across the board. If the facts are not there, fix the facts first — this skill
does not launder them.

## Commercial framing

Agent-SEO is a repeatable, scoped deliverable. It ships as:

1. A one-time **audit + fix** on a client's existing site (production-ready
   artefacts, 1–2 day engagement).
2. A **monthly retainer** that adds a new FAQ pair + sitemap refresh + a
   schema update tracking changes to Google/Schema.org/llms.txt spec.
3. A **product-page kit** for an SDK or plugin — the exact bundle this skill
   writes for JobPulse under `public/`.

Skill is modular: `/agent-seo` run against any directory produces the nine
artefacts for that site. No framework, no vendor, no runtime.
