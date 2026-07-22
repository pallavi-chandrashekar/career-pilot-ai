# Security and Privacy

## Data classification

### Highly sensitive
- Work authorization and immigration details
- OAuth tokens
- Email bodies
- Personal contact information

### Sensitive
- Resume contents
- Application notes
- Compensation preferences
- Interview details

### Internal
- Job scores
- Prompt traces
- Analytics

## Required controls

- TLS for all network traffic
- Encryption at rest for sensitive columns and object storage
- Secrets in environment-specific secret managers
- OAuth scopes limited to required operations
- Per-user authorization checks in repositories and APIs
- CSRF protection for browser sessions
- Secure cookies
- Rate limiting
- Audit logs
- Token rotation and revocation
- Redaction of sensitive logs
- No raw prompt traces containing highly sensitive data unless explicitly enabled

## External-action safety

Every external action requires:
1. Prepared payload
2. Payload hash
3. Approval request
4. Explicit approval
5. Idempotent execution
6. Audit record

An approval is invalid if the payload changes after approval.

## Email privacy

Default behavior:
- Store metadata and classification
- Avoid long-term storage of full bodies
- Store only snippets needed for workflow context
- Support configurable retention
- Never train on user email data

## Public repository safety

- Use fictional candidates
- Use fake companies
- Use synthetic email data
- Never commit private resumes
- Provide `.env.example`
- Add secret scanning
- Add dependency and container scanning

## Threat scenarios

- Prompt injection in job descriptions
- Malicious content in resumes
- Unauthorized email sending
- Cross-user data leakage
- Duplicate external action
- Model hallucination
- OAuth token theft
- Sensitive logging
- Stored XSS from job descriptions

## Mitigations

- Treat external text as untrusted data
- Never allow job text to override system policies
- Sanitize rendered HTML
- Validate all structured model output
- Separate tool permissions by agent
- Apply CSP headers
- Use signed download URLs
- Run dependency scanning in CI
