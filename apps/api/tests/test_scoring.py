from careerpilot_api.jobs.scoring import score


def test_weighted_score_and_recommendation() -> None:
    result = score(
        category_scores={"skills": 90, "location": 50},
        weights={"skills": 80, "location": 20},
        thresholds={"apply_now": 80, "apply_selectively": 68, "manual_review": 55},
    )
    assert result.total == 82
    assert result.recommendation == "APPLY_NOW"
