"""Real HTTP search profile lifecycle coverage using fictional data."""

import os
from uuid import uuid4

import httpx
import pytest

API_BASE_URL = os.getenv("E2E_API_BASE_URL")
pytestmark = pytest.mark.e2e


def valid_configuration() -> dict[str, object]:
    return {
        "name": "Fictional platform roles",
        "description": "Synthetic test profile",
        "active": True,
        "target_roles": [{"title": "Fictional Platform Engineer"}],
        "excluded_titles": ["Fictional Frontend Engineer"],
        "locations": {"preferred": ["Remote, US"], "excluded": ["Fictional City"]},
        "weights": {
            "core_technical_skills": 20,
            "distributed_systems": 15,
            "ai_alignment": 15,
            "domain_alignment": 10,
            "seniority": 10,
            "leadership": 10,
            "location": 8,
            "sponsorship": 7,
            "compensation": 3,
            "company_preference": 2,
        },
        "thresholds": {
            "apply_now": 80,
            "apply_selectively": 68,
            "manual_review": 55,
            "skip_below": 55,
        },
        "notifications": {"minimum_score": 75},
    }


@pytest.mark.skipif(not API_BASE_URL, reason="E2E_API_BASE_URL is required for search profile E2E")
def test_search_profile_lifecycle_and_owner_isolation() -> None:
    registration = httpx.post(
        f"{API_BASE_URL}/api/v1/auth/register",
        json={
            "email": f"fictional-profile-{uuid4().hex}@example.com",
            "display_name": "Fictional Profile Owner",
            "timezone": "UTC",
            "password": "fictional-password-123",
        },
        timeout=10.0,
    )
    assert registration.status_code == 201
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}
    created = httpx.post(
        f"{API_BASE_URL}/api/v1/search-profiles",
        headers=headers,
        json=valid_configuration(),
        timeout=10.0,
    )
    assert created.status_code == 201
    profile = created.json()
    assert profile["configuration_version"] == 1
    assert profile["is_active"] is True

    changed = valid_configuration()
    changed["description"] = "Updated fictional profile"
    updated = httpx.put(
        f"{API_BASE_URL}/api/v1/search-profiles/{profile['id']}",
        headers=headers,
        json=changed,
        timeout=10.0,
    )
    assert updated.status_code == 200
    assert updated.json()["configuration_version"] == 2

    duplicate = httpx.post(
        f"{API_BASE_URL}/api/v1/search-profiles/{profile['id']}/duplicate",
        headers=headers,
        json={"name": "Copied fictional profile"},
        timeout=10.0,
    )
    assert duplicate.status_code == 201
    assert duplicate.json()["configuration_version"] == 1
    assert duplicate.json()["is_active"] is False

    state = httpx.post(
        f"{API_BASE_URL}/api/v1/search-profiles/{profile['id']}/state",
        headers=headers,
        json={"is_active": True, "is_default": True},
        timeout=10.0,
    )
    assert state.status_code == 200
    assert state.json()["is_default"] is True

    copied_state = httpx.post(
        f"{API_BASE_URL}/api/v1/search-profiles/{duplicate.json()['id']}/state",
        headers=headers,
        json={"is_active": True, "is_default": True},
        timeout=10.0,
    )
    assert copied_state.status_code == 200
    profiles = httpx.get(f"{API_BASE_URL}/api/v1/search-profiles", headers=headers, timeout=10.0)
    assert profiles.status_code == 200
    assert sum(profile["is_default"] for profile in profiles.json()) == 1

    invalid = valid_configuration()
    invalid["weights"] = {**invalid["weights"], "company_preference": 1}  # type: ignore[arg-type]
    validation = httpx.post(
        f"{API_BASE_URL}/api/v1/search-profiles/{profile['id']}/validate",
        headers=headers,
        json={"configuration": invalid},
        timeout=10.0,
    )
    assert validation.status_code == 200
    assert validation.json()["valid"] is False

    second_registration = httpx.post(
        f"{API_BASE_URL}/api/v1/auth/register",
        json={
            "email": f"fictional-profile-other-{uuid4().hex}@example.com",
            "display_name": "Second Fictional Owner",
            "timezone": "UTC",
            "password": "fictional-password-123",
        },
        timeout=10.0,
    )
    second_headers = {"Authorization": f"Bearer {second_registration.json()['access_token']}"}
    hidden = httpx.get(
        f"{API_BASE_URL}/api/v1/search-profiles/{profile['id']}",
        headers=second_headers,
        timeout=10.0,
    )
    assert hidden.status_code == 404
