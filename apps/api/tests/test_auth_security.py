from uuid import uuid4

from careerpilot_api.auth.security import (
    hash_password,
    issue_access_token,
    verify_access_token,
    verify_password,
)


def test_password_hash_does_not_contain_plaintext_and_verifies() -> None:
    encoded = hash_password("fictional-password-123")

    assert "fictional-password-123" not in encoded
    assert verify_password("fictional-password-123", encoded)
    assert not verify_password("wrong-password-123", encoded)


def test_signed_access_token_rejects_tampering() -> None:
    user_id = uuid4()
    token = issue_access_token(user_id, "test-secret", 30)

    assert verify_access_token(token, "test-secret") == user_id
    assert verify_access_token(f"{token}x", "test-secret") is None
