# API Specification

Base path: `/api/v1`

## Conventions

- JSON requests and responses
- RFC 7807 problem details for errors
- Cursor pagination
- Idempotency-Key required for long-running POST actions
- Workflow endpoints return `202 Accepted`
- All resources are scoped to the authenticated user

## Authentication

### POST /auth/register
Creates a user and returns a bearer access token.

### POST /auth/login
Authenticates a user and returns a bearer access token. Invalid credentials use
the same response regardless of whether the email exists.

### GET /auth/me
Returns the current authenticated user.

## Candidate profiles

### POST /candidate-profiles
Creates a profile.

### GET /candidate-profiles
Lists profiles.

### GET /candidate-profiles/{id}
Returns one profile.

### PATCH /candidate-profiles/{id}
Updates mutable profile fields.

## Documents

### POST /documents
Multipart upload. Supported MIME types:
- application/pdf
- application/vnd.openxmlformats-officedocument.wordprocessingml.document

Requires bearer authentication. The service verifies the file signature and extension,
stores bytes under an opaque object-storage key, and returns owner-scoped metadata.
Uploading the same bytes again for the same user returns the existing metadata.
Uploads are limited to 10 MiB.

### POST /documents/{id}/extract-claims
Requires bearer authentication. Runs a configured structured LLM provider only
against the owner's parsed document. Every returned claim must cite source lines,
is stored as `DRAFT`, and cannot be used as approved candidate evidence.

Repeated requests with the same document/parser/prompt/provider/model inputs
return the existing idempotent workflow result.

### POST /documents/{id}/parse
Requires bearer authentication. Parses the owner's stored PDF or DOCX and records
encrypted normalized text, section line ranges, and a parser version.

### GET /documents/{id}/status
Requires bearer authentication. Returns upload status and metadata only when the
document belongs to the authenticated user. Other users receive `404`.

## Candidate claims

### GET /candidate-claims
Requires bearer authentication. Lists only the authenticated user's evidence-grounded
claims. This implementation returns claim type, statement, source document line range,
and verification status.

### GET /candidate-claims/{id}/evidence
Requires bearer authentication. Returns only the cited parsed-text lines for an
owner-scoped claim, allowing the reviewer to inspect its evidence without exposing
the whole source document.

### PATCH /candidate-claims/{id}
Requires bearer authentication. Edits only a `DRAFT` claim, and the replacement
statement must appear in the claim's cited source lines. Claims belonging to another
user are not disclosed.

### POST /candidate-claims/{id}/approve
Requires bearer authentication. Approves only a `DRAFT` claim. Approval is an explicit
human action; no LLM can approve claims.

### POST /candidate-claims/{id}/reject
Requires bearer authentication. Rejects only a `DRAFT` claim.

### POST /candidate-claims/bulk-approve
Requires bearer authentication. Atomically approves an owner-scoped, unique set of
`DRAFT` claims; no claims are changed if any requested claim is missing or not a draft.

## Search profiles

### POST /search-profiles
Requires bearer authentication. Validates configuration and creates version 1.

### GET /search-profiles
Requires bearer authentication. Lists the authenticated user's current profile versions.
Use `active_only=true` to return active profiles only.

### GET /search-profiles/{id}
Requires bearer authentication. Returns the authenticated user's current version.

### PUT /search-profiles/{id}
Requires bearer authentication. Creates an immutable new configuration version.

### POST /search-profiles/{id}/duplicate
Requires bearer authentication. Creates an inactive version-1 copy; it does not become default.

### POST /search-profiles/{id}/validate
Requires bearer authentication. Returns deterministic configuration validation errors without
persisting the submitted configuration.

### POST /search-profiles/{id}/state
Requires bearer authentication. Activates/deactivates a profile and optionally makes it the
single active default profile for the user. Invalid configurations cannot be persisted.

### POST /search-profiles/{id}/preview-score
Reserved for the deterministic scoring engine in Task 014. The Search Profile UI
does not present a score as available before that implementation exists.

## Jobs

### POST /jobs
Requires bearer authentication. Creates an owner-scoped manual job from company, title,
and pasted description, with optional location and source URL. Text is treated as untrusted;
normalization is deferred to Task 011. Exact owner-scoped fingerprint and URL duplicates return
the canonical job while preserving the additional manual source record.

### POST /jobs/import-url
Requires bearer authentication. Fetches a permitted public HTML page and returns bounded,
untrusted extracted text for review. Blocked or unreadable pages return `PASTE_REQUIRED` with a
paste fallback message; normalization is deferred to Task 011.

### POST /jobs/import-csv
Imports job rows.

### GET /jobs
Filters:
- search_profile_id
- recommendation
- hard_filter_status
- company
- title
- location
- discovered_after
- minimum_score

### GET /jobs/{id}
Returns normalized job and source metadata.

### POST /jobs/{id}/normalize
Requires bearer authentication. Deterministically extracts explicit requirement, seniority,
compensation, sponsorship, and clearance signals from the owner's job description.

### POST /jobs/{id}/evaluate
Starts evaluation for one or more search profiles.

### GET /jobs/{id}/matches
Returns stored match results.

### POST /jobs/{id}/override
Applies a user override with reason.

## Application packages

### POST /jobs/{id}/application-package
Starts package generation.

Request:
```json
{
  "search_profile_id": "uuid",
  "resume_template_id": "uuid",
  "include_cover_letter": true,
  "include_recruiter_message": true,
  "include_referral_message": true,
  "screening_questions": []
}
```

### GET /application-packages/{id}
Returns package, evidence map, and factuality status.

### POST /application-packages/{id}/request-approval
Creates approval request.

### POST /application-packages/{id}/export
Requires approval. Generates DOCX/PDF.

## Resumes

### GET /resume-versions/{id}
Returns structured resume model.

### GET /resume-versions/{id}/diff
Returns differences from parent or master resume.

### POST /resume-versions/{id}/validate
Runs factuality and ATS checks.

## Applications

### POST /applications
Creates tracking record.

### GET /applications
Lists by status and date.

### PATCH /applications/{id}
Updates allowed fields.

### POST /applications/{id}/transition
Validates state transition.

### POST /applications/{id}/follow-up
Creates follow-up task or approved email draft.

## Communications

### POST /integrations/gmail/sync
Starts sync workflow.

### GET /communications
Lists recruiting communications.

### POST /communications/{id}/classify
Reclassifies communication.

### POST /communications/{id}/draft-reply
Creates a reply draft; sending requires approval.

## Calendar

### POST /integrations/calendar/sync
Imports recruiting events.

### POST /interviews/{id}/prepare
Starts interview preparation workflow.

### POST /interviews/{id}/schedule-prep
Creates approval request for calendar blocks.

## Approvals

### GET /approvals
Lists pending approvals.

### POST /approvals/{id}/approve
Approves exact payload hash.

### POST /approvals/{id}/reject
Rejects request.

### POST /approvals/{id}/execute
Executes approved action idempotently.

## Analytics

### GET /analytics/funnel
### GET /analytics/sources
### GET /analytics/resume-performance
### GET /analytics/score-outcomes
### GET /analytics/time-saved
