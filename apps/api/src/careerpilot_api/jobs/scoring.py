"""Deterministic weighted job score aggregation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreResult:
    total: int
    confidence: float
    recommendation: str
    category_scores: dict[str, int]


def score(
    *, category_scores: dict[str, int], weights: dict[str, int], thresholds: dict[str, int]
) -> ScoreResult:
    total = round(
        sum(category_scores.get(name, 0) * weight for name, weight in weights.items()) / 100
    )
    recommendation = (
        "APPLY_NOW"
        if total >= thresholds["apply_now"]
        else "APPLY_SELECTIVELY"
        if total >= thresholds["apply_selectively"]
        else "MANUAL_REVIEW"
        if total >= thresholds["manual_review"]
        else "SKIP"
    )
    confidence = round(
        sum(1 for value in category_scores.values() if value >= 0) / max(len(weights), 1), 2
    )
    return ScoreResult(total, confidence, recommendation, category_scores)
