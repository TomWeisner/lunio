.PHONY: install lint format test ci
install:
	poetry install

lint:
	poetry run ruff check src tests

format:
	poetry run ruff format src tests

test:
	poetry run pytest

ci: lint test
