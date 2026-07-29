"""Deterministic, evidence-bearing hard-filter policy."""

from dataclasses import dataclass
from enum import StrEnum


class FilterOutcome(StrEnum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class FilterResult:
    outcome: FilterOutcome
    rule_id: str
    evidence: str | None
    explanation: str


def evaluate_sponsorship(*, job_sponsorship: str | None, required: bool) -> FilterResult:
    if not required:
        return FilterResult(
            FilterOutcome.PASS, "SPONSORSHIP_NOT_REQUIRED", None, "No sponsorship constraint."
        )
    if job_sponsorship == "UNAVAILABLE":
        return FilterResult(
            FilterOutcome.REJECT,
            "SPONSORSHIP_UNAVAILABLE",
            "UNAVAILABLE",
            "Job explicitly does not sponsor.",
        )
    if job_sponsorship == "AVAILABLE":
        return FilterResult(
            FilterOutcome.PASS,
            "SPONSORSHIP_AVAILABLE",
            "AVAILABLE",
            "Job explicitly supports sponsorship.",
        )
    return FilterResult(
        FilterOutcome.UNKNOWN, "SPONSORSHIP_UNKNOWN", None, "Sponsorship information is missing."
    )


def evaluate_clearance(*, job_clearance: str | None, policy: str) -> FilterResult:
    if policy != "HARD_REQUIREMENT":
        return FilterResult(
            FilterOutcome.PASS, "CLEARANCE_NOT_REQUIRED", None, "No hard clearance constraint."
        )
    if job_clearance == "REQUIRED":
        return FilterResult(
            FilterOutcome.REJECT,
            "CLEARANCE_REQUIRED",
            "REQUIRED",
            "Job explicitly requires clearance.",
        )
    return FilterResult(
        FilterOutcome.UNKNOWN, "CLEARANCE_UNKNOWN", None, "Clearance information is missing."
    )
