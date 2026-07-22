.DEFAULT_GOAL := help

PYTHON ?= $(if $(wildcard .venv/bin/python),$(abspath .venv/bin/python),python3.12)

.PHONY: help up down api-test web-test integration-test check

help: ## List developer commands.
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "%-12s %s\\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Build and start the local stack.
	docker compose up --build

down: ## Stop the local stack.
	docker compose down

api-test: ## Run API tests with the configured Python executable.
	$(PYTHON) -m pytest -c apps/api/pyproject.toml apps/api/tests

web-test: ## Run web unit tests.
	npm run web:test

integration-test: ## Build the local stack and verify its published health endpoints.
	docker compose up --build --detach --wait
	E2E_API_BASE_URL=http://localhost:8000 E2E_WEB_BASE_URL=http://localhost:3000 $(PYTHON) -m pytest -c apps/api/pyproject.toml apps/api/tests/test_stack_e2e.py

check: ## Run formatting, linting, type checks, and unit tests.
	cd apps/api && $(PYTHON) -m ruff format --check . && $(PYTHON) -m ruff check . && $(PYTHON) -m mypy && $(PYTHON) -m pytest
	npm run web:format && npm run web:lint && npm run web:typecheck && npm run web:test
