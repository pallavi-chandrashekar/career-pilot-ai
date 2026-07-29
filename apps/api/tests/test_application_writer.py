from careerpilot_api.applications.service import build_draft


def test_application_draft_uses_exact_approved_claims_and_maps_evidence() -> None:
    draft = build_draft(
        company="Fictional Systems",
        title="Platform Engineer",
        approved_claims=[("claim-1", "Built fictional Python services.")],
    )

    assert draft.tailored_resume == ["Built fictional Python services."]
    assert "Built fictional Python services." in draft.cover_letter
    assert draft.evidence_map["cover_letter"] == ["claim-1"]
