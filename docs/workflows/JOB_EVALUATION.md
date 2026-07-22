# Job Evaluation Workflow

1. Load job and search profile
2. Normalize job if needed
3. Run deterministic hard filters
4. Stop on REJECT unless user override exists
5. Parse requirements
6. Retrieve approved candidate evidence
7. Score categories
8. Run LLM evidence relevance review
9. Aggregate score
10. Run compliance check
11. Persist result
12. Publish completion event

Unknown critical information produces MANUAL_REVIEW.
