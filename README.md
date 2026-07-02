# lunio

Lunio coding challenge.

## Setup

```bash
poetry env use python3.13
poetry install
```

## Enable the virtual environment

```bash
source .venv/bin/activate
```

## Add pre-commit

```bash
poetry add --group dev pre-commit
```

This project already includes `pre-commit`, so after `poetry install` you can enable the Git hook with:

```bash
pre-commit install
```

## Checks

```bash
nox -s <sessions>
```

## Generate Data and Reports

```bash
poetry run python -m lunio.data.processing.clean
poetry run python -m lunio.data.analysis.eda
poetry run python -m lunio.models.rules_based.run_scoring
```

Outputs are written to `data/clean/` and `reports/`.
