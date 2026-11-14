# sitemap.xml + head meta + citations footer

## sitemap.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemap.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2026-11-14</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/docs</loc>
    <lastmod>2026-11-14</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

Rules: list only canonical URLs (one per page, same string as `<link rel="canonical">`).
Update `lastmod` when content changes. Omit `priority` if you only have one URL.

## `<head>` meta block

```html
<link rel="canonical" href="https://example.com/"/>

<meta property="og:title" content="<Product — one-line pitch>"/>
<meta property="og:description" content="<Same one-sentence pitch as llms.txt line 1>"/>
<meta property="og:type" content="website"/>
<meta property="og:url" content="https://example.com/"/>
<meta property="og:image" content="https://example.com/og.png"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>

<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="<Product>"/>
<meta name="twitter:description" content="<Pitch>"/>
<meta name="twitter:image" content="https://example.com/og.png"/>
```

- One canonical per URL. If the same content lives at multiple paths, canonical
  points at the preferred one.
- OG image: 1200×630, under 1 MB, descriptive filename. Agents increasingly
  extract alt text from the OG image for multimodal answers.

## Citations footer

Put a small block at the bottom of long-form pages:

```html
<section class="citations" aria-label="How to cite this page">
  <h3>How to cite this page</h3>
  <p><strong>Cite:</strong> <em>JobPulse AI Agent — Your AI job-search command center</em>,
     <a href="https://example.com/">example.com</a>, accessed 2026-11-14.</p>
</section>
```

Why: answer engines quote the most quotable line on the page. Make it this one.
