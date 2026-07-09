# Lunio Placement Safety: Methodology and Results

## 1. Problem Framing

Placement safety is advertiser-specific. A page about an aircraft incident can be
brand-safe for a coffee advertiser but unsafe for a holiday advertiser. The task is
therefore not a single global classification problem.

## 2. Working Definition of Safety

A placement is safe when the page context is unlikely to harm the advertiser's brand,
conflict with the advertiser's product category, or indicate poor traffic quality.

The MVP uses three decisions:

- `safe`: no configured risk signal found
- `review`: sensitive or low-confidence content requiring human/policy review
- `unsafe`: high-risk content or advertiser-specific hard exclusion

## 3. Data Assumptions

The `raw_data` sheet represents decision-time inputs. The `full_data` sheet includes
`topic` and `title`, which are treated as examples of a production enrichment layer,
not as guaranteed raw inputs.

Production flow:

```text
URL
  -> canonicalise URL and derive domain/path signals
  -> fetch title, metadata and page text where possible
  -> classify page topic/risk
  -> apply advertiser-specific policy
  -> output decision, confidence and rationale
```

## 4. MVP System

The implemented MVP has two scoring modes:

- raw mode: uses URL-derived signals plus click-quality signals
- enriched mode: additionally uses `topic` and `title`

Each decision includes:

- placement safety decision
- confidence
- matched risk categories
- matched signals
- human-readable rationale

## 5. Advertiser Policies

- Jet3 Holidays: highly sensitive to aviation incidents, war, terrorism and travel-adjacent disasters
- Jen & Berry's Ice Cream: family-friendly; sensitive to tobacco/nicotine, adult themes, weapons and extremism
- Moonbucks Coffee: broad-reach; mainly blocks universal high-risk content
- Plush Cosmetics: sensitive to wellbeing harms, divisive politics, tobacco, sexual, violent and extremist content

## 6. Why Not Just URL Keywords?

Some URLs are useful, but many are not. Opaque article IDs, redirects, PDFs, homepages,
paywalls and JavaScript-rendered pages can hide the real page context. URL-only scoring
is therefore a cheap first pass, not a sufficient production solution.

## 7. GenAI Extension

An LLM is useful as a constrained judge for ambiguous placements, not as an unchecked
oracle. A production prompt should include:

- advertiser profile
- page title/topic/body summary
- explicit risk taxonomy
- required structured JSON output
- instruction to return `review` when evidence is weak

The LLM layer can be evaluated against human review labels and monitored for policy drift.

## 8. Evaluation Plan

There is no ground-truth safety label in the provided data. Evaluation should therefore use:

- manually labelled review set sampled across advertisers and topics
- false-negative analysis on unsafe placements
- agreement between rule baseline, LLM judge and human labels
- slice metrics by advertiser, topic, channel and domain

## 9. Production Next Steps

- Build resilient URL enrichment with caching and retry logic
- Add domain reputation and publisher taxonomy signals
- Use embeddings or a lightweight supervised model once labels exist
- Route low-confidence/high-value placements to human review
- Monitor drift in topic distribution, unsafe rate and invalid-click rate
- Keep advertiser policies versioned and auditable
