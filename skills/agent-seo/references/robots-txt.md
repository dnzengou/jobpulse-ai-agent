# robots.txt for agent-SEO

Default stance: **welcome the crawlers you want to be cited by; block only
what you must.** Silence is read as "no answer" by some agent crawlers,
which then skip the site.

## Template

```
# Search engines
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: DuckDuckBot
Allow: /

# AI answer engines — allow unless you have a licensing reason not to
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: Applebot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Bytespider
Allow: /

User-agent: CCBot
Allow: /

User-agent: Meta-ExternalAgent
Allow: /

User-agent: cohere-ai
Allow: /

User-agent: FacebookExternalHit
Allow: /

User-agent: Twitterbot
Allow: /

# Catch-all
User-agent: *
Allow: /
Disallow: /drafts/
Disallow: /private/

Sitemap: https://example.com/sitemap.xml
```

## Rules

1. **List each AI crawler explicitly.** A wildcard `User-agent: *` works, but
   some crawlers only honor their named section and ignore the wildcard.
2. **Point to sitemap.xml at the bottom.** All known crawlers read this
   directive from robots.txt.
3. **Do not use `Crawl-delay` on agent crawlers.** Many ignore it; the ones
   that honor it slow retrieval, which matters when answers are being written
   live.
4. **Block drafts or staging paths explicitly.** Do not rely on noindex meta
   tags — agent crawlers may not parse them.

## Opting out

If a client wants to withhold training data but still appear in retrieval-time
answers, use `Google-Extended: Disallow: /` and `Applebot-Extended: Disallow: /`
while leaving the retrieval-time bots (`ChatGPT-User`, `Perplexity-User`,
`ClaudeBot`) allowed. Note: `Perplexity-User` is Perplexity's user-triggered
fetch — blocking it reduces citation coverage.
