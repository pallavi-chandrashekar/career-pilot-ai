# Product Requirements

## Vision

CareerPilot AI helps candidates identify relevant jobs, understand why they match, create truthful application materials, and manage recruiting workflows. The system is both a private production tool and a portfolio-quality enterprise AI agent project.

## Product principles

- Truthfulness over persuasion
- Human approval before external action
- Deterministic policy enforcement
- Explainable recommendations
- Configurable preferences
- Privacy by default
- Durable and auditable workflows
- Graceful behavior when information is unknown

## Core modules

1. Candidate profile and verified evidence
2. Configurable search profiles
3. Job ingestion and normalization
4. Deterministic hard filters
5. Evidence-backed match scoring
6. Tailored application generation
7. Approval center
8. Application tracking
9. Recruiting communication intelligence
10. Interview preparation
11. Analytics
12. MCP integrations

## Candidate evidence

The platform accepts PDF or DOCX resumes, manually entered work history, portfolio projects, selected GitHub repositories, and user-provided profile text. It extracts atomic claims such as job titles, employers, dates, responsibilities, technologies, achievements, metrics, project scope, and leadership.

Every extracted claim begins as `DRAFT`. A claim cannot be used in generated application material until the user approves it. Every generated sentence must retain evidence IDs internally.

Claim states:

```text
DRAFT
APPROVED
REJECTED
ARCHIVED
```

## Configurable search profiles

A user may create multiple profiles. Each profile supports:

- Target roles and aliases
- Excluded titles
- Seniority range
- Preferred, acceptable, and excluded locations
- Remote, hybrid, and onsite rules
- Maximum commute and onsite days
- Relocation preference
- Sponsorship and clearance policies
- Compensation thresholds
- Employment types
- Required, preferred, learning, and excluded skills
- Company and industry preferences
- Scoring weights
- Recommendation thresholds
- Notification settings

Constraint policies:

```text
HARD_REQUIREMENT
STRONG_PREFERENCE
SOFT_PREFERENCE
INFORMATIONAL
IGNORE
```

Weights must total 100. Configuration changes create a new version.

## Job ingestion

Initial inputs:

- Pasted job description
- Job URL
- Manual job form
- CSV import
- Job alert email
- Company career-page URL

Normalized fields include title, canonical title, seniority, responsibilities, required and preferred qualifications, location, work arrangement, employment type, compensation, sponsorship language, clearance language, source, canonical URL, posting date, expiration date, and data-quality score.

Duplicate detection uses canonical URL, external ID, company and normalized title, text fingerprint, and semantic similarity.

## Hard filters

Hard filters run before scoring and return:

```text
PASS
REVIEW
REJECT
UNKNOWN
```

Supported checks include sponsorship, citizenship, security clearance, location, onsite frequency, relocation, salary minimum, employment type, seniority, degree, language, and license requirements.

Explicit negative evidence takes precedence. Missing information normally results in `UNKNOWN`, not rejection. Every decision must include rule ID, evidence, and explanation.

## Match scoring

The scoring pipeline:

1. Run hard filters.
2. Parse requirements.
3. Retrieve approved candidate evidence.
4. Score deterministic categories.
5. Use an LLM to judge evidence relevance.
6. Aggregate weighted scores.
7. Produce confidence and recommendation.
8. Store scoring version, prompt version, and evidence links.

Default recommendation thresholds:

- `APPLY_NOW`: 80–100 with no blocking constraint
- `APPLY_SELECTIVELY`: 68–79
- `MANUAL_REVIEW`: 55–67 or incomplete information
- `SKIP`: below 55
- `REJECT`: hard-constraint violation

Every result must include total score, category scores, strengths, gaps, risks, missing information, hard-filter status, evidence links, confidence, recommendation, and suggested next action.

## Application generation

Allowed resume operations:

- Reorder approved bullets
- Select relevant bullets
- Shorten content
- Improve wording without altering meaning
- Emphasize relevant skills
- Select relevant projects
- Use approved metrics

Prohibited operations:

- Invent experience or skills
- Change employers, titles, or dates
- Inflate years of experience
- Invent metrics
- Present portfolio projects as employer work
- Add unapproved certifications, publications, patents, or awards

Outputs include tailored resume, cover letter, recruiter message, hiring-manager message, referral request, professional summary, screening answers, evidence map, factuality report, ATS coverage, and visible diff from the master resume.

## Human approval

Approval is required before final export, email sending, calendar writes, uncertain status transitions, policy overrides, or any external action. Approvals are bound to an exact payload hash and become invalid if the payload changes.

## Application tracking

Stages:

```text
DISCOVERED
REVIEWING
APPROVED_TO_APPLY
APPLIED
RECRUITER_SCREEN
TECHNICAL_INTERVIEW
HIRING_MANAGER
ONSITE_FINAL
OFFER
REJECTED
WITHDRAWN
CLOSED
```

The platform stores applied date, resume version, cover-letter version, source, referral contact, next action, next-action date, interview rounds, notes, compensation details, and outcome.

## Communication intelligence

Recruiting emails are classified as application received, recruiter outreach, interview request, assessment, follow-up, rejection, offer-related, or other. Low-confidence classifications must be routed to review.

## Interview preparation

Generate company and role summaries, requirement-to-evidence maps, relevant STAR stories, technical topics, system-design prompts, behavioral questions, questions to ask, introductions, and preparation checklists.

## Non-functional requirements

- Job detail p95 under one second excluding LLM work
- Normal evaluation under 60 seconds
- Application package generation under 120 seconds
- Temporal retries for transient failures
- Idempotent external actions
- WCAG 2.1 AA target
- Per-user data isolation
- Data export, deletion, retention, and token revocation
