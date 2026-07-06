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

## Comparison report

The rule-based and LLM-based models have now been compared. You can read the
results in the HTML report at:

```text
reports/llm_vs_rules_report.html
```

