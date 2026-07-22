# Search Profile Configuration Schema

```yaml
name: Senior AI Platform - Remote US
description: Primary search profile
active: true
target_roles:
  - title: Senior Software Engineer, AI Platform
    priority: 1
    aliases:
      - LLM Platform Engineer
      - Enterprise AI Engineer
    minimum_seniority: senior
    maximum_seniority: staff
excluded_titles:
  - frontend-only engineer

locations:
  preferred:
    - Remote, US
    - Irvine, CA
    - Orange County, CA
  acceptable:
    - Los Angeles, CA
    - San Diego, CA
  excluded:
    - San Francisco, CA
  remote_policy: STRONG_PREFERENCE
  hybrid_policy: SOFT_PREFERENCE
  onsite_policy: HARD_REQUIREMENT
  maximum_onsite_days: 2
  maximum_commute_miles: 40
  relocation_allowed: false

work_authorization:
  sponsorship_required: true
  sponsorship_policy: HARD_REQUIREMENT
  clearance_policy: HARD_REQUIREMENT
  reject_phrases:
    - no sponsorship
    - US citizens only
    - active security clearance required
  positive_phrases:
    - H-1B transfer
    - visa sponsorship available

compensation:
  currency: USD
  minimum_base: 180000
  preferred_base: 210000
  minimum_total_compensation: 230000
  below_minimum_policy: SOFT_PREFERENCE

employment_types:
  allowed:
    - fulltime
  policy: HARD_REQUIREMENT

skills:
  required:
    - name: backend engineering
      policy: HARD_REQUIREMENT
    - name: distributed systems
      policy: STRONG_PREFERENCE
  preferred:
    - Java
    - Kotlin
    - Golang
    - Python
    - Kubernetes
    - Kafka
    - Temporal
    - RAG
    - MCP
  learning_interests:
    - AWS Bedrock
    - agent evaluation
  excluded:
    - embedded systems

companies:
  preferred_industries:
    - enterprise software
    - AI infrastructure
    - developer platforms
  excluded_industries: []
  preferred_companies: []
  excluded_companies: []
  minimum_company_size: 50
  startups_allowed: true

weights:
  core_technical_skills: 20
  distributed_systems: 15
  ai_alignment: 15
  domain_alignment: 10
  seniority: 10
  leadership: 10
  location: 8
  sponsorship: 7
  compensation: 3
  company_preference: 2

thresholds:
  apply_now: 80
  apply_selectively: 68
  manual_review: 55
  skip_below: 55

notifications:
  minimum_score: 75
  immediate_for_apply_now: true
  daily_digest: true
```

## Validation rules

- Weight total must equal 100.
- Thresholds must be descending.
- Maximum onsite days must be 0–7.
- Minimum compensation cannot exceed preferred compensation.
- A location cannot appear in both preferred and excluded lists.
- A title cannot appear in both target and excluded lists.
- Every constraint policy must be valid.
