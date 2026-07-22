# Data Model

All tables use UUID primary keys, `created_at`, `updated_at`, and optimistic version fields where appropriate. All user-owned records include `user_id`.

## users
- id UUID PK
- email CITEXT UNIQUE NOT NULL
- display_name TEXT
- timezone TEXT NOT NULL
- status TEXT NOT NULL
- created_at TIMESTAMPTZ
- updated_at TIMESTAMPTZ

## candidate_profiles
- id UUID PK
- user_id UUID FK
- name TEXT NOT NULL
- professional_summary TEXT
- home_location JSONB
- work_authorization JSONB encrypted
- years_experience NUMERIC
- is_default BOOLEAN
- version INTEGER
- UNIQUE(user_id, name, version)

## documents
- id UUID PK
- user_id UUID FK
- document_type TEXT
- filename TEXT
- mime_type TEXT
- storage_key TEXT
- checksum TEXT
- parsed_text_encrypted TEXT
- parser_version TEXT
- status TEXT
- UNIQUE(user_id, checksum)

## candidate_claims
- id UUID PK
- user_id UUID FK
- candidate_profile_id UUID FK
- source_document_id UUID FK NULL
- claim_type TEXT
- canonical_statement TEXT
- employer TEXT
- project TEXT
- start_date DATE NULL
- end_date DATE NULL
- technologies JSONB
- metrics JSONB
- source_locator JSONB
- verification_status TEXT
- allowed_contexts JSONB
- sensitivity TEXT
- version INTEGER
- supersedes_claim_id UUID NULL
- embedding VECTOR
- INDEX(user_id, verification_status)
- VECTOR INDEX(embedding)

## search_profiles
- id UUID PK
- user_id UUID FK
- name TEXT
- description TEXT
- is_default BOOLEAN
- is_active BOOLEAN
- configuration JSONB
- configuration_version INTEGER
- UNIQUE(user_id, name, configuration_version)

## jobs
- id UUID PK
- user_id UUID FK
- company TEXT
- title TEXT
- canonical_title TEXT
- seniority TEXT
- description TEXT
- normalized_requirements JSONB
- location JSONB
- work_arrangement TEXT
- employment_type TEXT
- compensation JSONB
- sponsorship JSONB
- clearance JSONB
- canonical_url TEXT
- posting_date DATE
- expiration_date DATE
- fingerprint TEXT
- data_quality_score NUMERIC
- UNIQUE(user_id, fingerprint)

## job_sources
- id UUID PK
- job_id UUID FK
- source_type TEXT
- external_id TEXT
- source_url TEXT
- raw_payload_encrypted JSONB
- discovered_at TIMESTAMPTZ
- UNIQUE(source_type, external_id)

## job_matches
- id UUID PK
- user_id UUID FK
- job_id UUID FK
- search_profile_id UUID FK
- hard_filter_status TEXT
- total_score NUMERIC
- confidence NUMERIC
- recommendation TEXT
- category_scores JSONB
- strengths JSONB
- gaps JSONB
- risks JSONB
- missing_information JSONB
- evidence_map JSONB
- scoring_version TEXT
- prompt_version TEXT
- UNIQUE(job_id, search_profile_id, scoring_version)

## resume_versions
- id UUID PK
- user_id UUID FK
- candidate_profile_id UUID FK
- job_id UUID FK NULL
- name TEXT
- content_model JSONB
- evidence_map JSONB
- factuality_status TEXT
- parent_version_id UUID NULL
- docx_storage_key TEXT NULL
- pdf_storage_key TEXT NULL

## application_packages
- id UUID PK
- user_id UUID FK
- job_id UUID FK
- resume_version_id UUID FK
- cover_letter TEXT
- recruiter_message TEXT
- referral_message TEXT
- screening_answers JSONB
- evidence_map JSONB
- status TEXT

## applications
- id UUID PK
- user_id UUID FK
- job_id UUID FK
- package_id UUID FK NULL
- status TEXT
- applied_at TIMESTAMPTZ NULL
- next_action TEXT
- next_action_at TIMESTAMPTZ NULL
- source TEXT
- notes_encrypted TEXT
- outcome JSONB

## communications
- id UUID PK
- user_id UUID FK
- application_id UUID FK NULL
- provider_message_id TEXT
- direction TEXT
- sender TEXT
- recipients JSONB
- subject TEXT
- body_storage_policy TEXT
- classification TEXT
- confidence NUMERIC
- received_at TIMESTAMPTZ
- UNIQUE(user_id, provider_message_id)

## interviews
- id UUID PK
- application_id UUID FK
- calendar_event_id TEXT NULL
- interview_type TEXT
- start_time TIMESTAMPTZ
- end_time TIMESTAMPTZ
- timezone TEXT
- participants JSONB
- preparation_package_id UUID NULL

## approval_requests
- id UUID PK
- user_id UUID FK
- action_type TEXT
- object_type TEXT
- object_id UUID
- payload_hash TEXT
- status TEXT
- requested_at TIMESTAMPTZ
- reviewed_at TIMESTAMPTZ NULL
- executed_at TIMESTAMPTZ NULL
- reviewer_notes TEXT
- UNIQUE(object_type, object_id, action_type, payload_hash)

## workflow_runs
- id UUID PK
- user_id UUID FK
- workflow_type TEXT
- temporal_workflow_id TEXT UNIQUE
- idempotency_key TEXT UNIQUE
- status TEXT
- input_reference JSONB
- output_reference JSONB
- started_at TIMESTAMPTZ
- completed_at TIMESTAMPTZ NULL
- cost JSONB
- error JSONB

## audit_events
- id UUID PK
- user_id UUID FK
- actor_type TEXT
- actor_id TEXT
- event_type TEXT
- object_type TEXT
- object_id TEXT
- metadata JSONB
- created_at TIMESTAMPTZ
- INDEX(user_id, created_at)

## evaluation_results
- id UUID PK
- suite TEXT
- case_id TEXT
- model TEXT
- prompt_version TEXT
- scoring_version TEXT
- result JSONB
- passed BOOLEAN
- created_at TIMESTAMPTZ
