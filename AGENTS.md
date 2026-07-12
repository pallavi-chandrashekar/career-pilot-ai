# CareerPilot AI — Codex Instructions

## Product objective

Build a production-minded, human-in-the-loop AI job-search agent that can be used for real job applications and demonstrated as an enterprise AI portfolio project.

## Non-negotiable rules

1. Never fabricate candidate experience, skills, dates, titles, metrics, employers, degrees, certifications, publications, patents, awards, or responsibilities.
2. Generated application content may use only approved candidate claims.
3. Every generated claim must be traceable to one or more approved evidence records.
4. Never send an email, schedule an event, submit an application, or alter an external system without explicit approval.
5. Do not implement unauthorized LinkedIn scraping, CAPTCHA bypassing, anti-bot circumvention, or mass autonomous applications.
6. Hard constraints must be deterministic and must not depend solely on an LLM.
7. Real resumes, email data, immigration details, tokens, and private configuration must not be committed to the public repository.
8. Use fictional demo data in tests, examples, screenshots, and seeded environments.
9. Do not log resume contents, email bodies, OAuth tokens, or sensitive personal fields.
10. Add tests for every significant behavior.

## Architecture constraints

- Modular monorepo
- Python 3.12 backend with FastAPI
- Next.js and TypeScript frontend
- PostgreSQL with pgvector
- Alembic migrations
- Temporal for durable workflows
- MCP-compatible integrations
- Object storage for generated documents
- Provider abstraction for LLMs
- Structured logging and OpenTelemetry traces

## Engineering standards

- Prefer small, reviewable changes.
- Do not modify unrelated files.
- Use typed interfaces.
- Validate API payloads with Pydantic and Zod.
- Keep deterministic policy logic separate from LLM reasoning.
- Make workflow activities idempotent.
- Add audit records for approvals and external actions.
- Use UTC internally and store user timezone separately.
- Use feature flags for unfinished integrations.

## Completion report for every task

Report:

1. Summary of implementation
2. Files changed
3. Database migrations
4. API changes
5. Tests added
6. Commands run
7. Test results
8. Known limitations
9. Security or privacy considerations
10. Recommended next task
