.DEFAULT_GOAL := help

.PHONY: help up down api-test web-test integration-test check

help: ## List developer commands.
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "%-12s %s\\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Build and start the local stack.
	docker compose up --build

down: ## Stop the local stack.
	docker compose down

api-test: ## Run API tests in the project virtual environment.
	.venv/bin/python -m pytest -c apps/api/pyproject.toml apps/api/tests

web-test: ## Run web unit tests.
	npm run web:test

integration-test: ## Build the local stack and verify its published health endpoints.
	docker compose up --build --detach --wait
	E2E_API_BASE_URL=http://localhost:8000 E2E_WEB_BASE_URL=http://localhost:3000 .venv/bin/python -m pytest -c apps/api/pyproject.toml apps/api/tests/test_stack_e2e.py

check: ## Run formatting, linting, type checks, and unit tests.
	cd apps/api && ../../.venv/bin/python -m ruff format --check . && ../../.venv/bin/python -m ruff check . && ../../.venv/bin/python -m mypy && ../../.venv/bin/python -m pytest
	npm run web:format && npm run web:lint && npm run web:typecheck && npm run web:test
