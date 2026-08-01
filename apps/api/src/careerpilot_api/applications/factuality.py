"""Deterministic factuality checks for evidence-backed application packages."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FactualityFinding:
    field: str
    claim_id: str | None
    code: str
    message: str


def validate_package(
    *,
    content: dict[str, object],
    evidence_map: dict[str, object],
    approved_claims: dict[str, str],
) -> list[FactualityFinding]:
    """Require every mapped candidate claim to be approved and present verbatim in its field."""
    findings: list[FactualityFinding] = []
    for field, claim_ids_value in evidence_map.items():
        claim_ids = claim_ids_value if isinstance(claim_ids_value, list) else []
        value = content.get(field, "")
        text = "\n".join(value) if isinstance(value, list) else str(value)
        if not claim_ids:
            findings.append(
                FactualityFinding(field, None, "MISSING_EVIDENCE", "No evidence map entry.")
            )
            continue
        for claim_id in claim_ids:
            if not isinstance(claim_id, str) or claim_id not in approved_claims:
                findings.append(
                    FactualityFinding(
                        field, str(claim_id), "UNAPPROVED_CLAIM", "Claim is not approved."
                    )
                )
            elif approved_claims[claim_id] not in text:
                findings.append(
                    FactualityFinding(
                        field,
                        claim_id,
                        "STATEMENT_NOT_PRESENT",
                        "Mapped claim statement is absent from generated content.",
                    )
                )
    return findings
