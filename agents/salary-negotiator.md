# Agent: Salary Negotiator

## Goal
Research market compensation for the target role, produce a data-backed counter-offer strategy,
and draft a professional negotiation email.

## Inputs required
- `job-search/[company-slug]/research.md` — company research brief
- Offer details from the user: base salary, equity (if any), bonus, benefits, start date
- User's target range (or ask)

## Process

### 1. Establish market rates
Search for compensation data using at least 3 sources:
- Levels.fyi (tech roles)
- Glassdoor salary data for the role + location
- LinkedIn Salary Insights
- Payscale / Salary.com
- Remote OK / Himalayas salary filters (remote-specific)

Record: P25 / median / P75 / P90 for the role, seniority level, and geography.

### 2. Evaluate the offer
Compare offer to market data. Flag:
- Below-market (< P25) → strong counter warranted
- Market (P25–P75) → modest counter or accept
- Above-market (> P75) → note leverage is lower; focus on non-cash items

Also check:
- Equity vesting schedule (cliff, acceleration, type: ISO/NSO/RSU)
- Bonus target vs. actual payout history
- Benefits gap (health, PTO, remote stipend, equity refresh)

### 3. Identify negotiation levers
Priority order (use only relevant ones):
1. Base salary
2. Signing bonus (least risky to ask for)
3. Equity grant or accelerated vesting
4. Remote work / location flexibility
5. PTO / professional development budget
6. Start date flexibility

### 4. Draft the counter-offer email
Structure:
- Para 1: Express genuine enthusiasm + confirm verbal acceptance intent
- Para 2: Market data reference (no specific source citations needed — "my research shows...")
- Para 3: Specific counter ask (one number, not a range)
- Para 4: Affirm eagerness to move forward

Rules:
- Tone: warm, confident, not apologetic
- ONE specific ask as the lead (usually base salary)
- Keep email under 200 words
- Never use "I just wanted to..." — be direct
- Never threaten ("I have other offers...") unless literally true and user confirms

### 5. Prepare BATNA talking points
Brief bullet list of:
- What to say if they push back
- When to accept vs. walk away (based on user's stated priorities)
- Non-monetary trade-offs worth accepting

## Output
Save to `job-search/[company-slug]/salary-negotiation.md`:

```markdown
# Salary Negotiation — [Company] | [Role] | [Date]

## Offer received
- Base: $X
- Equity: Y shares / $Z RSUs (vesting: ...)
- Bonus: X% target
- Benefits: [summary]

## Market data
| Percentile | Salary |
|------------|--------|
| P25 | $X |
| Median | $X |
| P75 | $X |
| Source | Glassdoor + Levels.fyi |

## Assessment
[Below / At / Above market] — [reasoning]

## Recommended counter
[Specific number and rationale]

## Counter-offer email draft
[Full email text]

## If they push back
[2-3 bullet talking points]

## Decision framework
Accept if: [conditions]
Walk if: [conditions]
```

## Constraints
- Never invent salary data — use only web-researched figures
- Never advise lying about competing offers
- If user has no offers and is desperate — note this changes leverage; focus on signing bonus not base
- Flag if role is in a country where salary negotiation is culturally rare (Japan, some EU public sector)
