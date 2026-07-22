# Job Discovery Workflow

1. Load active search profiles
2. Generate source queries
3. Fetch from configured sources
4. Normalize jobs
5. Deduplicate
6. Persist new jobs
7. Evaluate against relevant profiles
8. Notify according to profile rules

The workflow must be idempotent and respect provider rate limits.
