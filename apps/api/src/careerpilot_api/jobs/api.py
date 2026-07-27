from hashlib import sha256
from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, HttpUrl

from careerpilot_api.auth.api import current_user
from careerpilot_api.db.models import JobModel, JobSourceModel, UserModel
from careerpilot_api.jobs.normalization import normalize
from careerpilot_api.jobs.repository import JobRepository
from careerpilot_api.jobs.url_ingestion import fetch_job_page

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


class JobRequest(BaseModel):
    company: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=100000)
    location: str | None = Field(default=None, max_length=255)
    source_url: HttpUrl | None = None


class JobResponse(BaseModel):
    id: UUID
    company: str
    title: str
    description: str
    location: str | None
    canonical_url: str | None
    source_type: str = "MANUAL"
    normalized_requirements: dict[str, object] | None = None
    seniority: str | None = None
    compensation: dict[str, object] | None = None
    sponsorship: str | None = None
    clearance: str | None = None


class UrlImportRequest(BaseModel):
    url: HttpUrl


class UrlImportResponse(BaseModel):
    status: str
    url: str
    extracted_text: str | None = None
    page_title: str | None = None
    paste_fallback_message: str | None = None


def _repo(request: Request) -> JobRepository:
    return cast(JobRepository, request.app.state.job_repository)


def _response(job: JobModel) -> JobResponse:
    return JobResponse(
        id=job.id,
        company=job.company,
        title=job.title,
        description=job.description,
        location=job.location,
        canonical_url=job.canonical_url,
        normalized_requirements=job.normalized_requirements,
        seniority=job.seniority,
        compensation=job.compensation,
        sponsorship=job.sponsorship,
        clearance=job.clearance,
    )


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobRequest, request: Request, user: Annotated[UserModel, Depends(current_user)]
) -> JobResponse:
    value = "\n".join((payload.company.strip(), payload.title.strip(), payload.description.strip()))
    job = JobModel(
        user_id=user.id,
        company=payload.company.strip(),
        title=payload.title.strip(),
        description=payload.description.strip(),
        location=payload.location.strip() if payload.location else None,
        canonical_url=str(payload.source_url) if payload.source_url else None,
        fingerprint=sha256(value.casefold().encode()).hexdigest(),
    )
    existing = await _repo(request).find_duplicate(
        user_id=user.id, fingerprint=job.fingerprint, canonical_url=job.canonical_url
    )
    if existing is not None:
        await _repo(request).add_source(
            job_id=existing.id,
            source=JobSourceModel(
                job_id=existing.id, source_type="MANUAL", source_url=job.canonical_url
            ),
        )
        return _response(existing)
    saved = await _repo(request).create(
        job, JobSourceModel(job_id=job.id, source_type="MANUAL", source_url=job.canonical_url)
    )
    return _response(saved)


@router.post("/import-url", response_model=UrlImportResponse)
async def import_job_url(
    payload: UrlImportRequest, user: Annotated[UserModel, Depends(current_user)]
) -> UrlImportResponse:
    del user
    url = str(payload.url)
    try:
        text, title = await fetch_job_page(url)
    except (PermissionError, ValueError) as error:
        return UrlImportResponse(
            status="PASTE_REQUIRED", url=url, paste_fallback_message=str(error)
        )
    return UrlImportResponse(status="EXTRACTED", url=url, extracted_text=text, page_title=title)


@router.post("/{job_id}/normalize", response_model=JobResponse)
async def normalize_job(
    job_id: UUID, request: Request, user: Annotated[UserModel, Depends(current_user)]
) -> JobResponse:
    job = await _repo(request).get(user_id=user.id, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    saved = await _repo(request).save_normalization(
        user_id=user.id, job_id=job_id, value=normalize(job.description)
    )
    if saved is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return _response(saved)


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    request: Request, user: Annotated[UserModel, Depends(current_user)]
) -> list[JobResponse]:
    return [_response(job) for job in await _repo(request).list(user_id=user.id)]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID, request: Request, user: Annotated[UserModel, Depends(current_user)]
) -> JobResponse:
    job = await _repo(request).get(user_id=user.id, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return _response(job)
