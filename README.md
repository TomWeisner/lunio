# lunio

Lunio coding challenge.

## Setup

### Installs

```bash
poetry env use python3.13
poetry install
```

### Enable the virtual environment

```bash
source .venv/bin/activate
```

### Enable pre-commit

This project already includes `pre-commit`, so after `poetry install` you can enable the Git hook with:

```bash
pre-commit install
```

### Checks

```bash
nox -s <sessions>
```
## Use

### Generate Data

```bash
poetry run python -m lunio.data.processing.clean
```
Outputs are written to `data/clean`.

### EDA

```bash
poetry run python -m lunio.data.analysis.eda
```
Outputs are written to `reports/`.

### Rules model

```bash
poetry run python -m lunio.models.rules_based.run_scoring
```

To see the architecture of the scoring, see
[`src/lunio/models/rules_based/README.md`](src/lunio/models/rules_based/README.md).

### LLM Extension

For more info about the LLM-based placement safety judge, see
[`src/lunio/models/extensions/llm/README.md`](src/lunio/models/extensions/llm/README.md).

## Outputs

- [`reports/deck_base_plan.md`](reports/deck_base_plan.md): base content for a slide deck.
- [`reports/eda_full_data_summary.md`](reports/eda_full_data_summary.md): eda report.
- [`reports/llm_vs_rules_report.html`](reports/llm_vs_rules_report.html): report summarising rule-vs-LLM predictions.
