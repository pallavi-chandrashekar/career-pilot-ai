from careerpilot_api.jobs.normalization import normalize


def test_normalizes_only_explicit_job_signals() -> None:
    result = normalize(
        "Senior engineer. Security clearance required. Sponsorship available. "
        "$180,000. Required: Python"
    )
    assert result["seniority"] == "senior"
    assert result["sponsorship"] == "AVAILABLE"
    assert result["clearance"] == "REQUIRED"
    assert result["compensation"] == {"amounts": [180000]}


def test_does_not_treat_clearance_negation_as_a_requirement() -> None:
    result = normalize("No clearance required. Required: Python")
    assert result["clearance"] == "NOT_REQUIRED"
