.PHONY: install lint format test build clean docs docs-serve release test-release

install:
	uv sync

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

test:
	uv run pytest

build: clean
	uv build

clean:
	rm -rf dist build *.egg-info

docs-serve:
	uv run --group docs mkdocs serve

docs:
	uv run --group docs mkdocs gh-deploy

test-release: build
	uv publish --index testpypi

release: build
	uv publish
