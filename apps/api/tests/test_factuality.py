from careerpilot_api.applications.factuality import validate_package


def test_validator_accepts_exact_approved_claim_statement() -> None:
    findings = validate_package(
        content={"cover_letter": "My approved experience: Built fictional Python services."},
        evidence_map={"cover_letter": ["claim-1"]},
        approved_claims={"claim-1": "Built fictional Python services."},
    )
    assert findings == []


def test_validator_flags_missing_or_unapproved_evidence() -> None:
    findings = validate_package(
        content={"cover_letter": "I led global teams."},
        evidence_map={"cover_letter": ["claim-1", "claim-2"]},
        approved_claims={"claim-1": "Built fictional Python services."},
    )
    assert {finding.code for finding in findings} == {"STATEMENT_NOT_PRESENT", "UNAPPROVED_CLAIM"}
