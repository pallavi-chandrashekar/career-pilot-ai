import os
from uuid import uuid4

import httpx
import pytest

API_BASE_URL = os.getenv("E2E_API_BASE_URL")
pytestmark = pytest.mark.e2e


@pytest.mark.skipif(not API_BASE_URL, reason="E2E_API_BASE_URL is required")
def test_manual_job_ingestion_and_owner_isolation() -> None:
    registration = httpx.post(
        f"{API_BASE_URL}/api/v1/auth/register",
        json={
            "email": f"fictional-job-{uuid4().hex}@example.com",
            "display_name": "Fictional Owner",
            "timezone": "UTC",
            "password": "fictional-password-123",
        },
        timeout=10.0,
    )
    assert registration.status_code == 201
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}
    created = httpx.post(
        f"{API_BASE_URL}/api/v1/jobs",
        headers=headers,
        json={
            "company": "Fictional Systems",
            "title": "Fictional Platform Engineer",
            "description": "Build fictional Python services.",
            "location": "Remote, US",
        },
        timeout=10.0,
    )
    assert created.status_code == 201
    job = created.json()
    assert (
        httpx.get(f"{API_BASE_URL}/api/v1/jobs", headers=headers, timeout=10.0).json()[0]["id"]
        == job["id"]
    )
    other = httpx.post(
        f"{API_BASE_URL}/api/v1/auth/register",
        json={
            "email": f"fictional-other-{uuid4().hex}@example.com",
            "display_name": "Other",
            "timezone": "UTC",
            "password": "fictional-password-123",
        },
        timeout=10.0,
    )
    assert (
        httpx.get(
            f"{API_BASE_URL}/api/v1/jobs/{job['id']}",
            headers={"Authorization": f"Bearer {other.json()['access_token']}"},
            timeout=10.0,
        ).status_code
        == 404
    )
