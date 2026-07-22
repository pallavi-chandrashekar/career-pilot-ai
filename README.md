# CareerPilot AI

> A human-in-the-loop AI job-search agent that discovers and evaluates opportunities, generates truthful application materials, and tracks recruiting workflows using verified candidate evidence.

## Local development

Task 001 provides the repository foundation only: health checks, local services,
quality tooling, and a foundation screen. It does not ingest candidate data or
perform external actions.

```bash
cp .env.example .env
docker compose up --build
```

After startup, the web app is at http://localhost:3000, the API liveness check
is at http://localhost:8000/health/live, and readiness is at
http://localhost:8000/health/ready. PostgreSQL (with pgvector), Temporal, and
Temporal UI run locally on ports 5432, 7233, and 8080 respectively.

For host quality checks, use Python 3.12 and Node 22+:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e "apps/api[dev]"
npm install
make check
make integration-test
```

Use non-secret development values only. `.env` is ignored and real resumes,
email data, OAuth tokens, and other sensitive information must never be added
to the repository.

## Overview

CareerPilot AI is designed as both a practical job-application assistant and a portfolio-quality enterprise agent platform. It combines configurable search profiles, deterministic policy checks, evidence-backed retrieval, durable workflows, MCP integrations, and explicit human approval before external actions.

The system is intentionally not a mass-application bot. It helps a candidate make better decisions and prepare higher-quality applications while preserving accuracy, privacy, and control.

## Core capabilities

- Build a verified candidate profile from resumes, projects, and approved claims
- Create multiple configurable job-search profiles
- Ingest jobs from pasted descriptions, URLs, CSV files, email alerts, and approved providers
- Apply deterministic hard filters for sponsorship, location, clearance, compensation, and seniority
- Produce explainable 0–100 job-match scores backed by candidate evidence
- Generate truthful tailored resumes, cover letters, recruiter messages, referral requests, and screening answers
- Track applications, communications, interviews, follow-ups, and outcomes
- Integrate Gmail, Google Calendar, GitHub, job sources, and document tools through MCP-compatible interfaces
- Run durable long-running workflows with Temporal
- Evaluate factuality, scoring quality, prompt regressions, and approval safety

## Product flow

```text
Upload resume
→ Extract candidate claims
→ Review and approve evidence
→ Configure search profiles
→ Ingest jobs
→ Normalize and deduplicate
→ Apply hard filters
→ Score against verified evidence
→ Generate tailored application materials
→ Validate factuality
→ Review and approve
→ Export and track
→ Detect recruiting events
→ Prepare for interviews
→ Analyze outcomes
```

## Architecture

```text
Next.js Web App
    |
FastAPI API
    |
Domain Services
    |-- Candidate Profile
    |-- Search Profiles
    |-- Job Intelligence
    |-- Match Scoring
    |-- Application Packages
    |-- Approvals
    |-- Tracking and Analytics
    |
Agent Orchestrator
    |
Temporal Workflows
    |
MCP Integration Gateway
    |-- Gmail
    |-- Calendar
    |-- GitHub
    |-- Job Sources
    |-- Document Renderer
    |
PostgreSQL + pgvector + Object Storage
```

## Recommended technology stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, TypeScript, Material UI, React Query |
| Backend | Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic |
| Database | PostgreSQL, pgvector |
| Workflow orchestration | Temporal |
| Agent orchestration | Controlled graph or LangGraph |
| Integrations | MCP-compatible servers and typed clients |
| Storage | S3-compatible object storage |
| Observability | OpenTelemetry, Langfuse, Prometheus, Grafana, Sentry |
| Testing | Pytest, Testcontainers, Vitest, Playwright |

## Safety principles

1. Generated content may use only approved candidate claims.
2. Every generated claim must be traceable to evidence.
3. Hard constraints are evaluated deterministically.
4. Missing information produces review, not an unsupported assumption.
5. Email sending, calendar writes, application submission, and other external actions require explicit approval.
6. Job descriptions and emails are treated as untrusted input.
7. Real resumes, email content, immigration details, and secrets are never committed to the public repository.
8. Demo environments use fictional candidates and synthetic data.

## Configurable search profiles

Users can create profiles such as:

- Senior AI Platform Engineer — Remote US
- Senior Backend Engineer — Orange County
- Staff Engineer — Selective Applications
- Engineering Manager — Southern California

Each profile can configure:

- Target and excluded roles
- Seniority range
- Preferred, acceptable, and excluded locations
- Remote, hybrid, and onsite rules
- Sponsorship and security-clearance policies
- Compensation thresholds
- Required, preferred, learning, and excluded skills
- Company and industry preferences
- Scoring weights
- Recommendation thresholds
- Notification behavior

Constraints support these policy types:

```text
HARD_REQUIREMENT
STRONG_PREFERENCE
SOFT_PREFERENCE
INFORMATIONAL
IGNORE
```

## Explainable scoring

The default scoring model includes:

| Category | Default weight |
|---|---:|
| Core technical skills | 20 |
| Distributed systems and architecture | 15 |
| AI, LLM, RAG, and agent alignment | 15 |
| Domain alignment | 10 |
| Seniority alignment | 10 |
| Leadership and ownership | 10 |
| Location and work arrangement | 8 |
| Sponsorship confidence | 7 |
| Compensation alignment | 3 |
| Company preference | 2 |

Every result includes category scores, supporting evidence, strengths, gaps, risks, missing information, confidence, recommendation, and suggested next action.

## Human approval model

Approval is required before:

- Final application-package export
- Sending email
- Scheduling calendar events
- Applying job-specific policy overrides
- Updating uncertain application statuses
- Executing any external write action

Approvals are tied to an exact payload hash. If the payload changes, approval is invalidated.

## Repository documentation

- `AGENTS.md` — instructions for Codex and coding agents
- `docs/PRODUCT_REQUIREMENTS.md` — end-to-end product requirements
- `docs/ARCHITECTURE.md` — system boundaries and design
- `docs/DATA_MODEL.md` — core persistence model
- `docs/API_SPECIFICATION.md` — planned REST API
- `docs/SECURITY.md` — privacy and security requirements
- `docs/EVALUATION_PLAN.md` — benchmarks and release gates
- `docs/IMPLEMENTATION_PLAN.md` — milestone plan
- `tasks/` — bounded implementation tasks for Codex

## Initial implementation milestone

The first vertical slice is:

```text
Upload resume
→ Extract draft claims
→ Review and approve claims
→ Paste one job description
→ Evaluate hard constraints
→ Produce evidence-backed match score
→ Generate tailored resume
→ Validate factuality
→ Export DOCX/PDF after approval
```

## Development approach

Do not attempt the entire platform in one change. Build one bounded task at a time and require each task to include implementation, tests, documentation, and a completion report.

Codex should begin with:

```text
Read AGENTS.md, README.md, docs/PRODUCT_REQUIREMENTS.md,
docs/ARCHITECTURE.md, docs/DATA_MODEL.md, and
tasks/TASK_001_REPOSITORY_FOUNDATION.md.

Create a concrete implementation plan before changing code.
Then implement only TASK_001.

Run formatting, type checks, and tests. Report:
- files changed
- commands run
- test results
- assumptions
- limitations
- recommended next task
```

## Project status

Planning and architecture phase. The repository is being implemented incrementally through reviewable Codex tasks.

## License

A license will be selected before the first public release.
