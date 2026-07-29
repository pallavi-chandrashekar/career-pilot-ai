"""Deterministic, evidence-preserving application content assembly."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicationDraft:
    tailored_resume: list[str]
    cover_letter: str
    recruiter_message: str
    referral_message: str
    evidence_map: dict[str, list[str]]


def build_draft(
    *, company: str, title: str, approved_claims: list[tuple[str, str]]
) -> ApplicationDraft:
    """Assemble a traceable draft using exact approved statements only.

    This deliberately does not paraphrase or infer candidate facts. Every candidate-facing
    sentence includes one or more source claim IDs in the returned evidence map.
    """
    statements = [statement for _, statement in approved_claims]
    claim_ids = [claim_id for claim_id, _ in approved_claims]
    selected = statements[:3]
    selected_ids = claim_ids[:3]
    evidence_summary = " ".join(selected)
    cover_letter = (
        f"Dear {company} hiring team,\n\n"
        f"I am interested in the {title} opportunity. My approved experience includes: "
        f"{evidence_summary}\n\nSincerely"
    )
    recruiter_message = f"I am interested in the {title} role at {company}. {evidence_summary}"
    referral_message = f"I am exploring the {title} opportunity at {company}. {evidence_summary}"
    return ApplicationDraft(
        tailored_resume=selected,
        cover_letter=cover_letter,
        recruiter_message=recruiter_message,
        referral_message=referral_message,
        evidence_map={
            "tailored_resume": selected_ids,
            "cover_letter": selected_ids,
            "recruiter_message": selected_ids,
            "referral_message": selected_ids,
        },
    )
