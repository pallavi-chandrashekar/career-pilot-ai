# MCP Integration Specification

## Profile MCP
Tools:
- get_candidate_profile
- list_verified_claims
- search_candidate_evidence
- create_claim_draft
- request_claim_approval

## Jobs MCP
Tools:
- search_jobs
- get_job
- capture_job_url
- normalize_job
- list_company_jobs

## Applications MCP
Tools:
- create_application
- get_application
- update_application_status
- list_due_followups
- record_outcome

## Gmail MCP
Tools:
- search_recruiting_emails
- get_recruiting_thread
- create_reply_draft

No direct send tool should be exposed to autonomous agents. Sending must go through approval execution.

## Calendar MCP
Tools:
- list_interview_events
- find_availability
- create_interview_hold
- create_preparation_block

All writes require approval.

## GitHub MCP
Tools:
- list_repositories
- analyze_repository
- extract_project_evidence

## Document MCP
Tools:
- render_resume_docx
- render_resume_pdf
- render_cover_letter
- compare_resume_versions

## Tool contract requirements
Every tool defines:
- JSON input schema
- JSON output schema
- Authentication
- Authorization
- Timeout
- Retry behavior
- Idempotency
- Audit event
- Error codes
- Sensitive-data handling
