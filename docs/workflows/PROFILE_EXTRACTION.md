# Profile Extraction Workflow

1. Validate upload
2. Store encrypted document
3. Parse document
4. Segment sections
5. Extract draft claims
6. Detect duplicates and conflicts
7. Generate embeddings
8. Persist claims
9. Notify user for review

Retries:
- Parsing: 2
- LLM extraction: 2
- Embedding: 3

Idempotency key:
`user_id + document_checksum + parser_version + prompt_version`
