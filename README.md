# CareerPilot AI

CareerPilot AI is a human-in-the-loop AI job-search platform that helps a candidate discover, evaluate, prepare, and track real job applications without fabricating experience or taking external actions without approval.

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

## Start here

Codex should read these files in order:

1. `AGENTS.md`
2. `docs/PRODUCT_REQUIREMENTS.md`
3. `docs/ARCHITECTURE.md`
4. `docs/DATA_MODEL.md`
5. `docs/API_SPECIFICATION.md`
6. `docs/SECURITY.md`
7. `docs/EVALUATION_PLAN.md`
8. The relevant file in `tasks/`

Do not attempt the entire system in one change. Implement one task at a time.
