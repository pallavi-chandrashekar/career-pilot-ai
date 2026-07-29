from uuid import uuid4

import pytest
from pydantic import ValidationError

from careerpilot_api.resumes.api import ResumeCreateRequest


def test_resume_content_requires_at_least_one_claim_reference() -> None:
    payload = ResumeCreateRequest(
        name="Fictional master resume",
        content_model={
            "sections": [{"heading": "Experience", "items": [{"claim_id": str(uuid4())}]}]
        },
    )
    assert payload.content_model.sections[0].heading == "Experience"


def test_resume_content_rejects_empty_sections() -> None:
    with pytest.raises(ValidationError):
        ResumeCreateRequest(name="Fictional master resume", content_model={"sections": []})
