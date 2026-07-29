"""Structured, evidence-backed master resume version endpoints."""

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from careerpilot_api.auth.api import current_user
from careerpilot_api.claims.repository import ClaimRepository
from careerpilot_api.db.models import (
    ClaimVerificationStatus,
    ResumeVersionModel,
    UserModel,
)
from careerpilot_api.resumes.repository import ResumeRepository

router = APIRouter(prefix="/api/v1/resume-versions", tags=["resumes"])


class ResumeItem(BaseModel):
    claim_id: UUID


class ResumeSection(BaseModel):
    heading: str = Field(min_length=1, max_length=120)
    items: list[ResumeItem] = Field(min_length=1, max_length=100)


class ResumeContentModel(BaseModel):
    sections: list[ResumeSection] = Field(min_length=1, max_length=20)


class ResumeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    content_model: ResumeContentModel
    parent_version_id: UUID | None = None


class ResumeResponse(BaseModel):
    id: UUID
    name: str
    content_model: ResumeContentModel
    parent_version_id: UUID | None


def _repository(request: Request) -> ResumeRepository:
    return cast(ResumeRepository, request.app.state.resume_repository)


def _claims(request: Request) -> ClaimRepository:
    return cast(ClaimRepository, request.app.state.claim_repository)


def _response(resume: ResumeVersionModel) -> ResumeResponse:
    return ResumeResponse(
        id=resume.id,
        name=resume.name,
        content_model=ResumeContentModel.model_validate(resume.content_model),
        parent_version_id=resume.parent_version_id,
    )


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume_version(
    payload: ResumeCreateRequest,
    request: Request,
    user: Annotated[UserModel, Depends(current_user)],
) -> ResumeResponse:
    claim_ids = {
        item.claim_id for section in payload.content_model.sections for item in section.items
    }
    claims = await _claims(request).list_claims(user_id=user.id)
    approved_ids = {
        claim.id
        for claim in claims
        if claim.verification_status is ClaimVerificationStatus.APPROVED
    }
    if not claim_ids <= approved_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Resume sections may reference approved claims only.",
        )
    if (
        payload.parent_version_id
        and await _repository(request).get(user_id=user.id, resume_id=payload.parent_version_id)
        is None
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parent resume version not found."
        )
    resume = await _repository(request).create(
        ResumeVersionModel(
            user_id=user.id,
            name=payload.name,
            content_model=payload.content_model.model_dump(mode="json"),
            parent_version_id=payload.parent_version_id,
        )
    )
    return _response(resume)


@router.get("", response_model=list[ResumeResponse])
async def list_resume_versions(
    request: Request, user: Annotated[UserModel, Depends(current_user)]
) -> list[ResumeResponse]:
    return [_response(resume) for resume in await _repository(request).list(user_id=user.id)]


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume_version(
    resume_id: UUID, request: Request, user: Annotated[UserModel, Depends(current_user)]
) -> ResumeResponse:
    resume = await _repository(request).get(user_id=user.id, resume_id=resume_id)
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found."
        )
    return _response(resume)
