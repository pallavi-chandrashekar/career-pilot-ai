"""Real HTTP document upload coverage using fictional data and the Compose stack."""

import os
from uuid import uuid4

import httpx
import pytest

API_BASE_URL = os.getenv("E2E_API_BASE_URL")
pytestmark = pytest.mark.e2e


@pytest.mark.skipif(not API_BASE_URL, reason="E2E_API_BASE_URL is required for document E2E tests")
def test_document_upload_deduplication_and_owner_isolation() -> None:
    email = f"fictional-document-{uuid4().hex}@example.com"
    registration = httpx.post(
        f"{API_BASE_URL}/api/v1/auth/register",
        json={
            "email": email,
            "display_name": "Fictional Candidate",
            "timezone": "UTC",
            "password": "fictional-password-123",
        },
        timeout=10.0,
    )
    assert registration.status_code == 201
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}
    files = {
        "file": (
            "fictional-resume.pdf",
            b"%PDF-1.7\\nfictional candidate document",
            "application/pdf",
        )
    }
    upload = httpx.post(
        f"{API_BASE_URL}/api/v1/documents", headers=headers, files=files, timeout=10.0
    )
    assert upload.status_code == 201
    document = upload.json()
    assert document["status"] == "UPLOADED"
    assert "storage_key" not in document

    duplicate = httpx.post(
        f"{API_BASE_URL}/api/v1/documents", headers=headers, files=files, timeout=10.0
    )
    assert duplicate.status_code == 200
    assert duplicate.json()["id"] == document["id"]

    second_registration = httpx.post(
        f"{API_BASE_URL}/api/v1/auth/register",
        json={
            "email": f"fictional-owner-{uuid4().hex}@example.com",
            "display_name": "Second Fictional Candidate",
            "timezone": "UTC",
            "password": "fictional-password-123",
        },
        timeout=10.0,
    )
    second_headers = {"Authorization": f"Bearer {second_registration.json()['access_token']}"}
    hidden = httpx.get(
        f"{API_BASE_URL}/api/v1/documents/{document['id']}/status",
        headers=second_headers,
        timeout=10.0,
    )
    assert hidden.status_code == 404
