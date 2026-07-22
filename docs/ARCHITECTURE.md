# System Architecture

## 1. High-level design

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

## 2. Architectural boundaries

### API layer
- Authentication
- Authorization
- Input validation
- Pagination
- Response serialization
- SSE workflow updates

### Domain layer
Contains deterministic business logic:
- Hard filters
- Weight validation
- Recommendation thresholds
- Claim permissions
- Approval checks
- Status transitions

### AI layer
Contains:
- Prompt templates
- Model provider abstraction
- Structured-output validation
- Retrieval
- Evidence grounding
- Factuality checking

### Workflow layer
Temporal coordinates long-running processes:
- Resume extraction
- Job evaluation
- Application generation
- Job discovery
- Email synchronization
- Interview preparation

### Integration layer
MCP servers or typed adapters isolate:
- Gmail
- Google Calendar
- GitHub
- Job providers
- Document export
- Object storage

## 3. Monorepo layout

```text
apps/
  api/
  web/
services/
  candidate/
  jobs/
  scoring/
  applications/
  integrations/
packages/
  domain-models/
  llm-gateway/
  prompt-library/
  mcp-clients/
  evaluation-kit/
workflows/
mcp-servers/
infrastructure/
evaluations/
docs/
tasks/
```

## 4. Agent orchestration

Use a controlled graph rather than an unrestricted autonomous loop.

Example job evaluation graph:

```text
load_job
→ load_search_profile
→ run_hard_filters
→ parse_requirements
→ retrieve_candidate_evidence
→ score_categories
→ llm_evidence_review
→ aggregate_score
→ compliance_check
→ persist_result
```

Every node has:
- Typed input
- Typed output
- Timeout
- Retry policy
- Audit event
- Error behavior

## 5. LLM provider abstraction

Interface methods:
- `generate_structured`
- `generate_text`
- `embed`
- `count_tokens`
- `estimate_cost`

Store:
- Provider
- Model
- Prompt version
- Temperature
- Token counts
- Latency
- Cost
- Response validation errors

## 6. Retrieval design

Use pgvector for:
- Candidate claim embeddings
- Job requirement embeddings
- Project evidence
- STAR stories

Retrieval rules:
- Retrieve only APPROVED claims
- Filter by usage permission
- Return source metadata
- Apply top-k and minimum similarity
- Rerank with structured metadata
- Preserve evidence IDs

## 7. Multi-tenancy

Initial deployment may be single-user, but all user-owned tables include `user_id`. Repository methods must scope by user. This allows later multi-user support without redesign.

## 8. Caching

Cache:
- Parsed job pages
- Embeddings
- Static company metadata
- Job fingerprints
- Model-independent normalization

Do not cache:
- Approval-sensitive external actions
- Private email content beyond configured retention
- Responses containing revoked claims

## 9. Failure handling

- Invalid structured LLM output: retry once with repair prompt, then fail to review
- Provider timeout: exponential retry
- Job page blocked: allow manual paste
- Document export failure: retain approved content and retry renderer
- Email classification uncertainty: manual review
- Duplicate workflow request: return existing idempotent result
