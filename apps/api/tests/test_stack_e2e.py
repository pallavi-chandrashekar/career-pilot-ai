"""Real HTTP verification for the Task 001 local stack."""

import os

import httpx
import pytest

API_BASE_URL = os.getenv("E2E_API_BASE_URL")
WEB_BASE_URL = os.getenv("E2E_WEB_BASE_URL")

pytestmark = pytest.mark.e2e


@pytest.mark.skipif(
    not API_BASE_URL or not WEB_BASE_URL,
    reason="E2E_API_BASE_URL and E2E_WEB_BASE_URL are required for stack tests",
)
def test_local_stack_health_endpoints() -> None:
    """Verify API liveness/readiness and web health through published ports."""

    for base_url, path in (
        (API_BASE_URL, "/health/live"),
        (API_BASE_URL, "/health/ready"),
        (WEB_BASE_URL, "/health"),
    ):
        response = httpx.get(f"{base_url}{path}", timeout=10.0)
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
