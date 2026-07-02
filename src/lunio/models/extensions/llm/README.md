# LLM Extension

This directory contains the optional LLM-based placement safety judge. It is kept
outside `lunio.models.rules_based` because the core rules-based package is a
deterministic, non-LLM baseline.

## Files

- `judge.py`: builds the advertiser-specific prompt and defines the expected
  JSON response schema.
- `runner.py`: sends one placement prompt to OpenAI's Responses API and parses
  the JSON decision.
- `batch.py`: loops over `data/clean/full_data.csv` and writes LLM decisions for
  every row.
- `compare.py`: compares the LLM decisions with the rule-based output from
  `reports/scored_full_data.csv`.

## Running

The normal workflow uses `full_data.csv`; you do not need to save a manual
`placement.json` file. First make sure the rule-based output exists:

```bash
poetry run python -m lunio.models.rules_based.run_scoring
```

Then run the LLM judge over the enriched full dataset:

```bash
OPENAI_API_KEY=... poetry run python -m lunio.models.extensions.llm.batch
```

This writes:

```text
reports/llm_scored_full_data.csv
```

For a cheap smoke test before running every row, use `--limit`:

```bash
OPENAI_API_KEY=... poetry run python -m lunio.models.extensions.llm.batch --limit 5
```

Then compare the LLM outputs with the rule-based outputs:

```bash
poetry run python -m lunio.models.extensions.llm.compare
```

This writes:

```text
reports/llm_vs_rules_comparison.csv
reports/llm_vs_rules_summary.md
```

`runner.py` can still run a single placement if you want to debug one prompt.
Create `placement.json` from the project root with:

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
OPENAI_API_KEY=... poetry run python -m lunio.models.extensions.llm.runner placement.json
```

The command prints the model's parsed JSON decision. Treat this as an extension
for experiments or ambiguous placements, not as a replacement for the rule-based
safety scorer without evaluation against human-labelled examples.
