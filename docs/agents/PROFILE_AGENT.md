# Profile Agent

## Purpose
Extract and maintain candidate evidence.

## Inputs
- Parsed resume text
- Manual profile data
- GitHub project summaries

## Outputs
- Draft candidate claims
- Missing-information questions
- Conflict report

## Allowed tools
- Document parser
- Candidate repository
- Embedding service

## Prohibited
- Approving claims
- Inventing missing facts
- Modifying external systems

## Validation
- Every claim has a source
- Dates and metrics preserved exactly
- Conflicting claims flagged
