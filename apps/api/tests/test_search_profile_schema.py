"""Deterministic search profile validation with fictional settings."""

import pytest
from pydantic import ValidationError

from careerpilot_api.search_profiles.schema import SearchProfileConfiguration


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


def test_valid_search_profile_configuration() -> None:
    configuration = SearchProfileConfiguration.model_validate(valid_configuration())
    assert configuration.weights.core_technical_skills == 20


def test_weights_must_total_one_hundred() -> None:
    payload = valid_configuration()
    payload["weights"] = {**payload["weights"], "company_preference": 1}  # type: ignore[arg-type]
    with pytest.raises(ValidationError, match="Weight total"):
        SearchProfileConfiguration.model_validate(payload)


def test_conflicting_locations_are_rejected() -> None:
    payload = valid_configuration()
    payload["locations"] = {"preferred": ["Remote, US"], "excluded": ["remote, us"]}
    with pytest.raises(ValidationError, match="location cannot"):
        SearchProfileConfiguration.model_validate(payload)


def test_thresholds_must_descend() -> None:
    payload = valid_configuration()
    payload["thresholds"] = {
        "apply_now": 60,
        "apply_selectively": 68,
        "manual_review": 55,
        "skip_below": 55,
    }
    with pytest.raises(ValidationError, match="Thresholds must be descending"):
        SearchProfileConfiguration.model_validate(payload)
