# llms.txt — authoring guide

Spec: <https://llmstxt.org>. A Markdown file at `/llms.txt` that summarizes
the site for LLM crawlers that don't want to render JS or chase navigation.

## Shape

```markdown
# <Product>

> <One-sentence thesis — 15 words max. Lead with the verb and the outcome.>

<Two- or three-sentence overview. Names the product, the user it serves, and
the single concrete thing it does that nothing else does. No adjectives.>

## What it does

- <Capability 1 — one sentence, with a numeral if possible.>
- <Capability 2.>
- <Capability 3.>

## Install

<Plain-text commands in order. One per line. No prose between them unless
a step genuinely needs it.>

## Docs

- [README](https://...)
- [Quick start](https://...)
- [Architecture](https://...)

## Optional

- [Changelog](https://...)
- [Examples](https://...)
```

Keep it under 400 lines. If more is needed, split into `/llms-full.txt` (the
long version) and leave `/llms.txt` as the short summary, linking out.

## Rules an answer engine rewards

1. **One thesis line at the top.** `> …` block-quote is the convention.
2. **Numerals, not words.** "8 job boards" not "eight job boards".
3. **Real commands.** Agents copy these into terminals. If they don't work
   when pasted, the engine stops citing you.
4. **Absolute URLs.** Relative links break when the file is fetched out of
   context.
5. **No telemetry or tracking links.** Agents strip UTM; they also notice.

## Smell tests before shipping

- `curl https://<site>/llms.txt` — does it serve as `text/plain` or
  `text/markdown`? Not HTML. (Set `Content-Type` in your host config or let
  the default serve it — Vercel/Netlify do this correctly for `.txt`/`.md`.)
- Paste the file into Claude / ChatGPT and ask: "What does this product do
  and how would I install it?" If the answer matches your pitch, ship it.
