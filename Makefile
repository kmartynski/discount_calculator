.PHONY: install lint format test check

install:
	uv sync

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

test:
	uv run pytest

check: lint test
