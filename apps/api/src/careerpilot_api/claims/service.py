"""Deterministic safeguards around LLM-proposed draft claims."""

from hashlib import sha256
from uuid import UUID

from careerpilot_api.claims.prompt import PROMPT_VERSION
from careerpilot_api.claims.provider import ExtractedClaim


def extraction_idempotency_key(
    *,
    user_id: UUID,
    document_checksum: str,
    parser_version: str,
    provider: str,
    model: str,
) -> str:
    value = ":".join(
        (str(user_id), document_checksum, parser_version, PROMPT_VERSION, provider, model)
    )
    return sha256(value.encode()).hexdigest()


def validate_claims(
    *, claims: tuple[ExtractedClaim, ...], parsed_text: str
) -> tuple[ExtractedClaim, ...]:
    lines = [line for line in parsed_text.splitlines() if line.strip()]
    validated: list[ExtractedClaim] = []
    for claim in claims:
        if not claim.claim_type.strip() or not claim.canonical_statement.strip():
            raise ValueError("Each claim must include a type and canonical statement.")
        if claim.start_line < 1 or claim.end_line < claim.start_line or claim.end_line > len(lines):
            raise ValueError("Each claim source location must reference parsed document lines.")
        source_text = "\n".join(lines[claim.start_line - 1 : claim.end_line]).casefold()
        if claim.canonical_statement.casefold() not in source_text:
            raise ValueError("Each claim statement must be directly supported by its source lines.")
        validated.append(claim)
    return tuple(validated)
