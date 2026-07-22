# Evaluation Plan

## 1. Job-scoring benchmark

Create 100 labeled jobs:
- 25 strong matches
- 20 moderate matches
- 20 weak matches
- 15 sponsorship conflicts
- 10 location conflicts
- 10 seniority or domain mismatches

For each case store:
- Expected hard-filter result
- Expected score range
- Expected recommendation
- Required evidence
- Important gaps
- Human rationale

Targets:
- Hard-filter precision: >= 98%
- Hard-filter recall: >= 98%
- Recommendation agreement: >= 85%
- Mean score error versus labeled midpoint: <= 8 points

## 2. Resume factuality benchmark

For each generated sentence verify:
- Employer matches evidence
- Title matches evidence
- Dates match evidence
- Metric matches evidence
- Technology is approved
- Responsibility is supported
- Portfolio work is correctly labeled

Targets:
- Unsupported critical claim rate: 0%
- Unsupported non-critical claim rate: < 1%
- Date/title/employer mutation rate: 0%

## 3. Retrieval evaluation

Measure:
- Recall@5 for supporting claims
- Precision@5
- Evidence diversity
- Usage-permission compliance

## 4. Email classification

Dataset classes:
- Application received
- Recruiter outreach
- Interview request
- Assessment
- Follow-up
- Rejection
- Offer related
- Other

Target macro F1: >= 0.90
Critical rule: low-confidence predictions route to review.

## 5. Prompt injection tests

Job descriptions and emails must not:
- Change system rules
- Trigger unauthorized tools
- Access other users
- Bypass approval
- Introduce unsupported claims

## 6. End-to-end tests

1. Upload resume → approve claims → paste job → score → generate resume → approve → export
2. Job with no sponsorship → deterministic rejection
3. Missing sponsorship data → review, not rejection
4. Email interview request → application linkage → preparation package
5. Approval payload changes → execution blocked
6. Duplicate workflow request → no duplicate action

## 7. Release gates

A release fails when:
- Any critical factuality test fails
- Hard-filter accuracy is below target
- Approval bypass is detected
- Cross-user authorization test fails
- Critical end-to-end workflow fails
