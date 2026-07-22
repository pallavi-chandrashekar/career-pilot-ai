# Product Requirements Document

## 1. Product vision

CareerPilot AI helps candidates identify relevant jobs, understand why they match, create truthful application materials, and manage recruiting workflows. The system is useful as a private production tool and presentable as an enterprise AI agent portfolio project.

## 2. Personas

### Primary user
An experienced software engineer seeking senior backend, AI platform, distributed systems, developer platform, or engineering leadership roles.

### Secondary users
- Any professional with a verified work history
- A career coach reviewing generated materials
- A portfolio evaluator inspecting architecture, safety, and evaluation quality

## 3. Product principles

- Truthfulness over persuasion
- Human approval before external action
- Deterministic policy enforcement
- Explainability for scores and recommendations
- Configurability instead of hard-coded preferences
- Privacy by default
- Durable, auditable workflows
- Graceful behavior when information is unknown

## 4. Major modules

1. Candidate profile and evidence
2. Search profiles
3. Job ingestion
4. Job intelligence and scoring
5. Application package generation
6. Approval center
7. Application tracking
8. Communication intelligence
9. Interview preparation
10. Analytics
11. Integrations
12. Administration and privacy

## 5. Candidate profile requirements

### 5.1 Inputs
- PDF resume
- DOCX resume
- Manually entered work history
- Portfolio project descriptions
- GitHub repositories selected by the user
- LinkedIn text pasted by the user
- Certifications and education entered manually

### 5.2 Claim extraction
The system extracts atomic claims such as:
- Job title and employer
- Employment dates
- Responsibilities
- Technologies
- Achievements
- Metrics
- Scope and leadership
- Project descriptions

Each extracted claim begins in `DRAFT` status and cannot be used in generated content until approved.

### 5.3 Claim fields
- Canonical statement
- Claim type
- Employer
- Project
- Dates
- Technologies
- Metrics
- Source document
- Source location
- Verification status
- Allowed usage contexts
- Sensitivity level
- User notes

### 5.4 Claim states
- DRAFT
- APPROVED
- REJECTED
- ARCHIVED

### 5.5 Acceptance criteria
- Users can edit extracted claims.
- Users can approve or reject claims individually or in bulk.
- Approved claims are immutable except through a versioned edit.
- Generated content cannot reference unapproved claims.
- Every generated sentence can be traced to evidence IDs.

## 6. Configurable search profiles

Users can create multiple search profiles.

### 6.1 Configurable fields
- Profile name and description
- Active/default state
- Target roles
- Role aliases
- Excluded titles
- Minimum and maximum seniority
- Preferred locations
- Acceptable locations
- Excluded locations
- Remote/hybrid/onsite preferences
- Maximum commute distance
- Maximum onsite days
- Relocation preference
- Work authorization requirements
- Sponsorship policy
- Security-clearance policy
- Compensation thresholds
- Employment types
- Preferred skills
- Required skills
- Learning-interest skills
- Excluded technologies or domains
- Preferred industries
- Excluded industries
- Company size preference
- Preferred and excluded companies
- Scoring weights
- Recommendation thresholds
- Notification rules

### 6.2 Constraint policy types
Each configurable rule supports:
- HARD_REQUIREMENT
- STRONG_PREFERENCE
- SOFT_PREFERENCE
- INFORMATIONAL
- IGNORE

### 6.3 Search-profile behavior
- A job can be scored against one or more profiles.
- One profile may be marked as default.
- Profiles can be duplicated.
- Per-job overrides are supported.
- Configuration versions are retained.
- Weight totals must equal 100.
- Invalid configurations cannot be activated.

## 7. Job ingestion

### 7.1 Supported initial inputs
- Pasted job description
- Job URL
- CSV import
- Job alert email
- Company career page URL
- Manual form entry

### 7.2 Later integrations
- Public or licensed job APIs
- ATS feeds
- Browser extension capture
- Approved search providers
- Company career-page monitoring

### 7.3 Normalized job fields
- Company
- Title
- Canonical title
- Seniority
- Description
- Required qualifications
- Preferred qualifications
- Responsibilities
- Location
- Work arrangement
- Employment type
- Compensation
- Sponsorship language
- Clearance language
- Source
- Canonical URL
- Posting date
- Expiration date
- Discovered date
- Fingerprint
- Data quality score

### 7.4 Duplicate detection
Use:
- Canonical URL
- External job ID
- Company and normalized title
- Description fingerprint
- Semantic similarity

Duplicates should be merged into one canonical job while preserving source records.

## 8. Hard-filter engine

Hard filters run before scoring.

### 8.1 Supported filters
- Sponsorship unavailable
- Citizenship requirement
- Security clearance
- Location exclusion
- Onsite frequency violation
- Relocation requirement
- Salary below hard minimum
- Wrong employment type
- Seniority below minimum
- Required degree not satisfied
- Required language or license not satisfied

### 8.2 Outcomes
- PASS
- REVIEW
- REJECT
- UNKNOWN

### 8.3 Rules
- Explicit negative evidence takes precedence.
- Missing information should normally produce `UNKNOWN`, not rejection.
- Every result includes a rule ID, evidence text, and explanation.
- Users may override a result with a reason.
- Overrides are audited.

## 9. Job scoring

### 9.1 Default categories
- Core technical skills
- Distributed systems and architecture
- AI/LLM/RAG/agent alignment
- Domain alignment
- Seniority alignment
- Leadership and ownership
- Location/work arrangement
- Sponsorship confidence
- Compensation alignment
- Company preference

### 9.2 Scoring pipeline
1. Apply hard filters.
2. Parse requirements.
3. Retrieve candidate evidence.
4. Score each requirement deterministically where possible.
5. Ask the LLM to judge evidence relevance.
6. Aggregate weighted category scores.
7. Produce confidence and recommendation.
8. Store score version, prompt version, and evidence links.

### 9.3 Recommendation defaults
- APPLY_NOW: 80–100 and no blocking constraint
- APPLY_SELECTIVELY: 68–79
- MANUAL_REVIEW: 55–67 or insufficient information
- SKIP: below 55
- REJECT: hard-constraint violation

Thresholds are configurable.

### 9.4 Explainability
Each result includes:
- Total score
- Category scores
- Strengths
- Gaps
- Risks
- Missing information
- Hard-filter result
- Evidence links
- Confidence
- Recommendation
- Suggested next action

## 10. Tailored resume generation

### 10.1 Allowed operations
- Reorder approved bullets
- Select relevant bullets
- Shorten text
- Improve wording without altering meaning
- Emphasize relevant skills
- Select relevant projects
- Use approved metrics
- Reorder skills

### 10.2 Prohibited operations
- Invent experience or skills
- Change employers, titles, or dates
- Inflate years of experience
- Invent metrics
- Present portfolio projects as employer work
- Add unapproved education, certification, publication, patent, or award
- Claim production usage without evidence

### 10.3 Generation process
1. Retrieve job requirements.
2. Retrieve relevant approved claims.
3. Build a content plan.
4. Generate a draft.
5. Run claim-to-evidence validation.
6. Run consistency checks.
7. Run ATS formatting checks.
8. Produce a visible change report.
9. Request user approval.
10. Export DOCX and PDF.

### 10.4 Outputs
- Tailored resume
- Evidence map
- Diff from master resume
- ATS keyword coverage
- Factuality report
- Export metadata

## 11. Other application materials

Generate:
- Cover letter
- Recruiter message
- Hiring manager message
- Referral request
- Professional summary
- Why this company
- Why this role
- Sponsorship response
- Salary expectation response
- Screening-question drafts

All content must follow the same evidence rules.

## 12. Approval center

Approval is required for:
- Exporting a final application package
- Sending email
- Scheduling calendar events
- Updating an uncertain application status
- Approving claims
- Applying per-job overrides
- Any external action

Approval states:
- DRAFT
- READY_FOR_REVIEW
- APPROVED
- REJECTED
- EXECUTED
- EXPIRED

## 13. Application tracking

### 13.1 Stages
- DISCOVERED
- REVIEWING
- APPROVED_TO_APPLY
- APPLIED
- RECRUITER_SCREEN
- TECHNICAL_INTERVIEW
- HIRING_MANAGER
- ONSITE_FINAL
- OFFER
- REJECTED
- WITHDRAWN
- CLOSED

### 13.2 Tracking fields
- Applied date
- Resume version
- Cover letter version
- Referral contact
- Source
- Next action
- Next action date
- Notes
- Compensation details
- Interview rounds
- Outcome
- Rejection reason

## 14. Communication intelligence

Classify recruiting emails as:
- APPLICATION_RECEIVED
- RECRUITER_OUTREACH
- INTERVIEW_REQUEST
- ASSESSMENT
- FOLLOW_UP
- REJECTION
- OFFER_RELATED
- OTHER

Low-confidence results must be routed for review.

## 15. Interview preparation

Generate:
- Company summary
- Role summary
- Requirement-to-evidence map
- Relevant STAR stories
- Technical topics
- System-design prompts
- Behavioral questions
- Questions to ask
- 30-second introduction
- 2-minute introduction
- Preparation checklist

## 16. Analytics

Track:
- Jobs discovered
- Jobs reviewed
- Applications submitted
- Response rate
- Interview rate
- Offer rate
- Application preparation time
- Best sources
- Best role categories
- Best resume versions
- Score versus outcome
- Common gaps
- Follow-up completion

## 17. Non-functional requirements

### Performance
- Job detail page: p95 under 1 second excluding LLM work
- Normal job evaluation: under 60 seconds
- Resume package generation: under 120 seconds
- List pages paginated
- Large document parsing performed asynchronously

### Reliability
- Temporal workflows retry transient failures
- External actions are idempotent
- Workflow state survives restarts
- Duplicate external actions are prevented

### Accessibility
- Keyboard navigable
- WCAG 2.1 AA target
- Proper labels and focus states
- Status not communicated by color alone

### Privacy
- Data export
- Account deletion
- Document deletion
- Token revocation
- Retention settings
