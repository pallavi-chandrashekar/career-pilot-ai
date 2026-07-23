"""Evidence-only claim extraction safeguards with fictional data."""

from uuid import UUID

import pytest

from careerpilot_api.claims.provider import ExtractedClaim, ProviderRegistry
from careerpilot_api.claims.service import extraction_idempotency_key, validate_claims


def test_valid_claim_requires_exact_source_text() -> None:
    claims = (ExtractedClaim("SKILL", "Python", 2, 2),)
    assert validate_claims(claims=claims, parsed_text="SUMMARY\nPython") == claims


def test_unsupported_claim_is_rejected() -> None:
    with pytest.raises(ValueError, match="directly supported"):
        validate_claims(claims=(ExtractedClaim("SKILL", "Kubernetes", 1, 1),), parsed_text="Python")


def test_invalid_source_range_is_rejected() -> None:
    with pytest.raises(ValueError, match="source location"):
        validate_claims(claims=(ExtractedClaim("SKILL", "Python", 2, 2),), parsed_text="Python")


def test_idempotency_key_changes_for_provider_or_model() -> None:
    base = dict(user_id=UUID(int=1), document_checksum="a" * 64, parser_version="1")
    assert extraction_idempotency_key(
        **base, provider="openai", model="one"
    ) != extraction_idempotency_key(**base, provider="openai", model="two")


def test_unknown_provider_is_rejected() -> None:
    with pytest.raises(ValueError, match="not enabled"):
        ProviderRegistry(()).get("unknown")
