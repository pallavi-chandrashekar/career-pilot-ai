"""Real HTTP authentication coverage using the local Compose stack."""

import os
from uuid import uuid4

import httpx
import pytest

API_BASE_URL = os.getenv("E2E_API_BASE_URL")

pytestmark = pytest.mark.e2e


@pytest.mark.skipif(
    not API_BASE_URL, reason="E2E_API_BASE_URL is required for auth integration tests"
)
def test_register_login_and_current_user() -> None:
    """Prove registration, protected identity, and generic login failure behavior."""

    email = f"fictional-{uuid4().hex}@example.com"
    password = "fictional-password-123"
    registration = httpx.post(
        f"{API_BASE_URL}/api/v1/auth/register",
        json={
            "email": email,
            "display_name": "Fictional Candidate",
            "timezone": "UTC",
            "password": password,
        },
        timeout=10.0,
    )

    assert registration.status_code == 201
    token = registration.json()["access_token"]
    current_user = httpx.get(
        f"{API_BASE_URL}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    assert current_user.status_code == 200
    assert current_user.json()["email"] == email

    failed_login = httpx.post(
        f"{API_BASE_URL}/api/v1/auth/login",
        json={"email": email, "password": "wrong-password-123"},
        timeout=10.0,
    )
    assert failed_login.status_code == 401
    assert failed_login.json() == {"detail": "Invalid email or password."}
