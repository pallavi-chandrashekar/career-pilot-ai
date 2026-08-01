from careerpilot_api.jobs.hard_filters import (
    FilterOutcome,
    evaluate_clearance,
    evaluate_sponsorship,
)


def test_explicit_sponsorship_negative_evidence_rejects() -> None:
    result = evaluate_sponsorship(job_sponsorship="UNAVAILABLE", required=True)
    assert result.outcome is FilterOutcome.REJECT
    assert result.rule_id == "SPONSORSHIP_UNAVAILABLE"


def test_missing_sponsorship_information_is_unknown() -> None:
    assert (
        evaluate_sponsorship(job_sponsorship=None, required=True).outcome is FilterOutcome.UNKNOWN
    )


def test_explicit_clearance_negation_passes_hard_clearance_policy() -> None:
    result = evaluate_clearance(job_clearance="NOT_REQUIRED", policy="HARD_REQUIREMENT")
    assert result.outcome is FilterOutcome.PASS
    assert result.rule_id == "CLEARANCE_NOT_REQUIRED"
