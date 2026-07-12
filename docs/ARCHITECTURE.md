# System Architecture

## High-level design

```text
Next.js Web App
    |
FastAPI API
    |
Domain Services
    |-- Candidate Service
    |-- Search Profile Service
    |-- Job Intelligence Service
    |-- Scoring Service
    |-- Application Package Service
    |-- Approval Service
    |-- Tracking Service
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

## Architectural boundaries

### API layer

- Authentication and authorization
- Input validation
- Pagination
- Response serialization
- Workflow status streaming

### Domain layer

Contains deterministic rules:

- Hard filters
- Search-profile validation
- Recommendation thresholds
- Claim permissions
- Approval enforcement
- Application-state transitions

### AI layer

Contains:

- Versioned prompts
- Model-provider abstraction
- Structured-output validation
- Retrieval over approved claims
- Evidence grounding
- Factuality validation

### Workflow layer

Temporal coordinates:

- Resume extraction
- Job ingestion and evaluation
- Application-package generation
- Scheduled job discovery
- Gmail synchronization
- Interview preparation

### Integration layer

MCP servers or typed adapters isolate Gmail, Calendar, GitHub, job providers, document export, and object storage.

## Controlled agent graph

Agents must use bounded graphs rather than unrestricted autonomous loops.

Example job-evaluation graph:

```text
load_job
→ load_search_profile
→ run_hard_filters
→ parse_requirements
→ retrieve_candidate_evidence
→ score_categories
→ review_evidence_relevance
→ aggregate_score
→ compliance_check
→ persist_result
```

Every node has typed input and output, timeout, retry policy, audit event, and defined failure behavior.

## LLM provider abstraction

Required methods:

- `generate_structured`
- `generate_text`
- `embed`
- `count_tokens`
- `estimate_cost`

Persist provider, model, prompt version, temperature, token usage, latency, cost, and validation errors.

## Retrieval design

Use pgvector for candidate claims, project evidence, job requirements, and STAR stories.

Rules:

- Retrieve only `APPROVED` claims
- Enforce allowed usage contexts
- Preserve evidence IDs and source metadata
- Apply minimum similarity and top-k limits
- Rerank using structured metadata

## Reliability

- Workflow activities are idempotent.
- Invalid structured model output is repaired once, then routed to review.
- Provider timeouts use bounded exponential retry.
- Blocked job pages fall back to manual paste.
- Duplicate workflow requests return the existing result.
- External actions require an approved payload hash.
