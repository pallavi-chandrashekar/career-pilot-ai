"""Versioned, safety-constrained claim extraction prompt."""

PROMPT_VERSION = "claim-extraction-v1"

SYSTEM_PROMPT = """Extract only atomic candidate claims directly supported by the provided document.
Do not infer, embellish, combine facts, or invent missing dates, employers, metrics, skills,
responsibilities, or titles. The canonical_statement must be an exact verbatim quote contained
within its cited inclusive source line range. Every claim must cite exact source line ranges from
the provided text. Return an empty list when support is absent or uncertain. All output claims are
drafts and are not approved for use in generated application content."""
