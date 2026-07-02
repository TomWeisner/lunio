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
