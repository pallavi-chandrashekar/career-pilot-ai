# CareerPilot AI

CareerPilot AI is a human-in-the-loop AI job-search platform that helps a candidate discover, evaluate, prepare, and track real job applications without fabricating experience or taking external actions without approval.

## Current status

Completed foundations:

- Modular Next.js and FastAPI monorepo with Docker Compose and GitHub Actions
- PostgreSQL/pgvector, Temporal, and Temporal UI local services
- Alembic-managed PostgreSQL schema with a user identity model
- Bearer-token registration, login, and authenticated identity API
- Secure, owner-scoped PDF/DOCX upload with checksum deduplication and MinIO storage
- Backend/frontend quality checks and live Compose integration coverage

Candidate claims, AI generation, integrations, and external actions are not yet implemented.

## Local development

Use only synthetic data and non-secret development values.

```bash
cp .env.example .env
docker compose up --build
```

The migration service applies the current Alembic revision before the API starts.

| Service | Address |
| --- | --- |
| Web | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs (development) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| MinIO API | http://localhost:9000 |
| MinIO Console | http://localhost:9001 |
| Temporal | localhost:7233 |
| Temporal UI | http://localhost:8080 |

Verify the stack:

```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
curl http://localhost:3000/health
```

To run host-based checks, install Python 3.12 and Node.js 22 or later:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e "apps/api[dev]"
npm install
make check
make integration-test
```

`make check` uses the project virtual environment when it exists and otherwise
uses `python3.12`, matching CI. `make integration-test` requires Docker and
checks the published API and web health endpoints.

## Authentication API

All application resources will be scoped to the authenticated user. The current
API uses short-lived bearer access tokens:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/auth/register` | Create a user and return an access token |
| `POST` | `/api/v1/auth/login` | Authenticate and return an access token |
| `GET` | `/api/v1/auth/me` | Return the current user; requires `Authorization: Bearer <token>` |

Passwords are stored as PBKDF2 hashes. Tokens, passwords, resumes, email data,
and private configuration must never be committed or logged.

## Documents API

Document endpoints require a bearer access token and accept only PDF or DOCX
files up to 10 MiB. Document bytes are retained only in object storage; API
responses expose metadata and status, never object-storage keys.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/documents` | Upload a document or return its existing per-user duplicate |
| `GET` | `/api/v1/documents/{id}/status` | Return owner-scoped upload status |

## Core capabilities

- Build a verified candidate profile from resumes, projects, and approved claims
- Create multiple configurable job-search profiles
- Ingest jobs from pasted descriptions, URLs, CSV files, email alerts, and approved providers
- Apply deterministic hard filters for sponsorship, location, clearance, compensation, and seniority
- Produce explainable 0–100 job-match scores backed by candidate evidence
- Generate truthful tailored resumes, cover letters, recruiter messages, referral requests, and screening answers
- Track application stages, communications, interviews, and follow-ups
- Integrate Gmail, Calendar, GitHub, and document generation through MCP-compatible tools
- Run durable workflows with Temporal
- Evaluate factuality, scoring quality, and prompt regressions

## Recommended stack

- Frontend: Next.js, TypeScript, Material UI, React Query
- Backend: Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic
- Storage: PostgreSQL, pgvector, S3-compatible object storage
- Orchestration: Temporal
- AI orchestration: lightweight internal graph or LangGraph
- Integrations: MCP servers and typed clients
- Observability: OpenTelemetry, Langfuse, Prometheus, Grafana, Sentry
- Testing: Pytest, Testcontainers, Playwright, Vitest

## Development order

1. Candidate profile and verified claims
2. Configurable search profiles
3. Job ingestion and scoring
4. Tailored application package
5. Application tracking
6. Gmail, Calendar, and GitHub integrations
7. Scheduled discovery
8. Evaluations, observability, deployment, and demo

## Development workflow

Review these files in order before starting a bounded implementation task:

1. `AGENTS.md`
2. `docs/PRODUCT_REQUIREMENTS.md`
3. `docs/ARCHITECTURE.md`
4. `docs/DATA_MODEL.md`
5. `docs/API_SPECIFICATION.md`
6. `docs/SECURITY.md`
7. `docs/EVALUATION_PLAN.md`
8. The relevant file in `tasks/`

Do not attempt the entire system in one change. Implement one task at a time.

See [MANIFEST.md](MANIFEST.md) for the full documentation inventory.
