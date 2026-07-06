# LLM Extension

This directory contains the optional LLM-based placement safety judge. It is kept
outside `lunio.models.rules_based` because the core rules-based package is a
deterministic, non-LLM baseline.

## Prerequisites

The LLM scorer needs an OpenAI API key. To get one:

1. Create or sign in to the OpenAI API site: https://openai.com/index/openai-api/
2. Make sure the account has billing enabled and available API credits.
3. Open the API keys page in the OpenAI dashboard.
4. Create a new secret key and keep it somewhere secure.
5. Export it in your shell as `OPENAI_API_KEY`.

For example:

```bash
export OPENAI_API_KEY=sk-...
```

Then pass it to the commands in this README with the `OPENAI_API_KEY`
environment variable:

```bash
OPENAI_API_KEY=$OPENAI_API_KEY poetry run python -m lunio.models.extensions.llm.score_full_data --limit 5
```

## Files

- `judge.py`: builds the advertiser-specific prompt and defines the expected
  JSON response schema.
- `score_placement.py`: sends one placement prompt to OpenAI's Responses API
  and parses the JSON decision.
- `score_full_data.py`: loops over `data/clean/full_data.csv` and writes LLM
  decisions for every row.
- `compare.py`: compares the LLM decisions with the rule-based output from
  `reports/scored_full_data.csv`.

## Running

The normal workflow uses `full_data.csv`.

First make sure the rule-based output exists:

```bash
poetry run python -m lunio.models.rules_based.run_scoring
```

Then run the LLM judge over the enriched full dataset:

```bash
OPENAI_API_KEY=... poetry run python -m lunio.models.extensions.llm.score_full_data
```

This writes:

```text
reports/llm_scored_full_data.csv
```

For a cheap smoke test before running every row, use `--limit`:

```bash
OPENAI_API_KEY=... poetry run python -m lunio.models.extensions.llm.score_full_data --limit 5
```

Then compare the LLM outputs with the rule-based outputs:

```bash
poetry run python -m lunio.models.extensions.llm.compare
```

This writes:

```text
reports/llm_vs_rules_comparison.csv
reports/llm_vs_rules_report.html
```

`score_placement.py` runs a single entry through the LLM judge code, so we can
debug. It requires a `placement.json` in the project root. Create this with:

```bash
cat > placement.json <<'JSON'
{
  "company_name": "Jet3 Holidays",
  "url": "https://example.com/flight-crash",
  "title": "Flight crash investigation",
  "topic": "Flight disasters (investigations)",
  "channel_type": "Display",
  "clicks": 1000,
  "invalid_clicks": 120
}
JSON
```

Then run:

```bash
OPENAI_API_KEY=... poetry run python -m lunio.models.extensions.llm.score_placement placement.json
```

The command prints the model's parsed JSON decision to the terminal.

## Scaling for Real-Time Traffic Decisions

This implementation is not designed to sit directly in the page-load path for
real-time traffic classification. Each row makes a synchronous API call to an
external LLM provider, so latency, rate limits, provider availability, and cost
would all affect the customer experience if this were used while a page is
loading. For fast ad or web traffic decisions, the serving path should normally
use deterministic rules, cached features, and precomputed risk signals so it can
return in milliseconds.

A more scalable production shape would keep the LLM out of the hot path:

- Run offline crawlers or scrapers to fetch page content for known domains,
  URLs, channels, and topics.
- Summarise scraped pages offline with an LLM and store compact safety signals,
  categories, and rationales keyed by URL, domain, advertiser, or topic.
- Refresh those summaries on a schedule or when a URL/topic changes, rather than
  during a customer request.
- Use the real-time service to look up cached safety decisions and fall back to
  fast rules when there is no cached LLM signal.
- Send uncertain, new, or high-value placements to an asynchronous review queue
  for LLM scoring after the request has completed.

That architecture keeps page loading fast while still using the LLM where it is
most useful: handling ambiguous content, creating richer explanations, and
improving policy coverage over time. The rule-based scorer can remain the
low-latency default, with LLM outputs used as offline enrichment, QA, monitoring,
or a source of candidates for new deterministic rules.
