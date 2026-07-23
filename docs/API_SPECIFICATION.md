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
Filters:
- profile_id
- verification_status
- claim_type
- employer
- technology

### PATCH /candidate-claims/{id}
Edits a draft claim.

### POST /candidate-claims/{id}/approve
Approves a claim.

### POST /candidate-claims/{id}/reject
Rejects a claim.

### POST /candidate-claims/bulk-approve
Approves multiple claims.

## Search profiles

### POST /search-profiles
Validates configuration and creates version 1.

### GET /search-profiles
Lists active and historical profiles.

### GET /search-profiles/{id}
Returns the latest or requested version.

### PUT /search-profiles/{id}
Creates a new configuration version.

### POST /search-profiles/{id}/duplicate
Creates a copy.

### POST /search-profiles/{id}/validate
Returns validation errors.

### POST /search-profiles/{id}/preview-score
Scores a supplied sample job without persisting it.

## Jobs

### POST /jobs
Creates a job from manual fields or pasted text.

### POST /jobs/import-url
Starts URL extraction and normalization.

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
