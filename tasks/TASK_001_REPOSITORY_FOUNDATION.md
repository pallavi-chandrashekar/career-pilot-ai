# Task 001 — Repository Foundation

## Goal

Create the initial modular monorepo, local development environment, continuous integration pipeline, health checks, formatting, linting, and type-checking configuration.

## Required reading

- `AGENTS.md`
- `README.md`
- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/ARCHITECTURE.md`

## Scope

Create:

- `apps/api` using Python 3.12 and FastAPI
- `apps/web` using Next.js and TypeScript
- Shared repository configuration
- Dockerfiles for API and web
- Docker Compose with API, web, PostgreSQL with pgvector, Temporal, and Temporal UI
- API and web health endpoints
- Environment-variable validation
- `.env.example` with safe placeholder values
- Python formatting, linting, and type checking
- TypeScript formatting, linting, and type checking
- GitHub Actions CI
- Basic unit tests for both applications
- Root developer commands and documentation

## Recommended structure

```text
apps/
  api/
  web/
packages/
services/
workflows/
mcp-servers/
infrastructure/
evaluations/
docs/
tasks/
```

Do not create empty placeholder directories unless they contain a `.gitkeep` and are documented as intentional.

## API requirements

The API must expose:

```http
GET /health/live
GET /health/ready
```

`live` verifies that the process is running. `ready` verifies required dependencies such as the database.

## Web requirements

The initial web page must display:

- Project name
- Current development status
- API connectivity result
- Links to repository documentation

This is a foundation screen, not the final dashboard.

## Docker Compose requirements

The local environment must support one documented command to start all required services.

Services:

- `api`
- `web`
- `postgres`
- `temporal`
- `temporal-ui`

Requirements:

- Health checks
- Named volumes
- Non-secret development defaults
- Deterministic service names
- Documented ports
- PostgreSQL pgvector support

## CI requirements

CI must run on pull requests and main-branch pushes.

Required checks:

- Python formatting
- Python linting
- Python type checking
- Python unit tests
- TypeScript formatting or linting
- TypeScript type checking
- Frontend unit tests
- Docker build validation

## Security requirements

- No credentials or API keys in source control
- `.env` files ignored
- `.env.example` contains placeholders only
- Containers must not require privileged mode
- Dependency versions must be pinned or constrained
- Sensitive environment variables must not appear in logs

## Non-goals

Do not implement:

- Resume upload
- Candidate profiles
- LLM integrations
- Job ingestion
- Search profiles
- Temporal business workflows
- Gmail, Calendar, or GitHub integrations
- Kubernetes deployment

## Acceptance criteria

- A developer can clone the repository and start the stack using the documented command.
- API and web health checks succeed.
- PostgreSQL is reachable from the API.
- Temporal and Temporal UI start successfully.
- Frontend can call the API health endpoint.
- Formatting, linting, type checks, and tests pass locally and in CI.
- The README contains accurate local-development instructions.
- No secrets are committed.

## Definition of done

Codex must report:

1. Files changed
2. Commands run
3. Test results
4. Assumptions
5. Known limitations
6. Security considerations
7. Recommended next task
