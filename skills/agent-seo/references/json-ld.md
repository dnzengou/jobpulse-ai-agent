# JSON-LD templates

Paste as `<script type="application/ld+json">…</script>` in the `<head>`.
Validate at <https://validator.schema.org/>. One schema per block; multiple
blocks per page are fine.

## Organization

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://example.com/#org",
  "name": "<Legal or product org name>",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": [
    "https://github.com/<org>",
    "https://x.com/<handle>",
    "https://www.linkedin.com/company/<slug>"
  ]
}
```

## SoftwareApplication (for a plugin, CLI, SDK, or app)

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "<Product name>",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "macOS, Linux, Windows",
  "description": "<One-sentence pitch — the same line that's at the top of llms.txt.>",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "softwareVersion": "0.4.0",
  "url": "https://example.com",
  "downloadUrl": "https://github.com/<owner>/<repo>",
  "author": { "@id": "https://example.com/#org" }
}
```

Omit `aggregateRating`/`review` unless you have real reviews to point at. A
fabricated rating is a flag.

## FAQPage

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "<The question a user actually types into Perplexity or ChatGPT>",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "<1–2 sentences. Fact, number, and a link.>"
      }
    }
  ]
}
```

Rule: every question in the JSON-LD must also appear as visible text on the
page (under an `<h2>FAQ</h2>` or similar). Mismatch between JSON-LD and
rendered HTML triggers spam heuristics.

## HowTo (for install steps)

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "Install <product>",
  "totalTime": "PT1M",
  "step": [
    { "@type": "HowToStep", "position": 1, "name": "Install", "text": "Run `/plugin marketplace add <path>`" },
    { "@type": "HowToStep", "position": 2, "name": "Restart", "text": "Restart Claude Code." },
    { "@type": "HowToStep", "position": 3, "name": "Use",     "text": "Run `/findmeajob`." }
  ]
}
```

## JobPosting (only for actual postings)

```json
{
  "@context": "https://schema.org",
  "@type": "JobPosting",
  "title": "<Role>",
  "description": "<Full JD HTML or plain text>",
  "datePosted": "2026-11-01",
  "validThrough": "2027-01-01",
  "employmentType": "FULL_TIME",
  "hiringOrganization": { "@type": "Organization", "name": "<Company>", "sameAs": "https://company.com" },
  "jobLocation": { "@type": "Place", "address": { "@type": "PostalAddress", "addressLocality": "San Francisco", "addressRegion": "CA", "addressCountry": "US" } },
  "baseSalary": { "@type": "MonetaryAmount", "currency": "USD", "value": { "@type": "QuantitativeValue", "minValue": 150000, "maxValue": 220000, "unitText": "YEAR" } }
}
```

Never emit this for a page that is not a real, active job listing. Google
will remove the whole domain from `JobPosting` eligibility if it sees fakes.

## Article (for blog posts)

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "<Title>",
  "datePublished": "2026-11-14",
  "dateModified": "2026-11-14",
  "author": { "@type": "Person", "name": "<Author>" },
  "publisher": { "@id": "https://example.com/#org" },
  "mainEntityOfPage": "https://example.com/blog/<slug>"
}
```

## BreadcrumbList (for nested pages)

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home",     "item": "https://example.com" },
    { "@type": "ListItem", "position": 2, "name": "Docs",     "item": "https://example.com/docs" },
    { "@type": "ListItem", "position": 3, "name": "Install",  "item": "https://example.com/docs/install" }
  ]
}
```
