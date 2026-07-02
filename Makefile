.PHONY: format

format:
	poetry run ruff format src tests
