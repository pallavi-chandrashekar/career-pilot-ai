"""Owner-scoped persisted application package retrieval."""

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from careerpilot_api.applications.repository import ApplicationPackageRepository
from careerpilot_api.auth.api import current_user
from careerpilot_api.db.models import ApplicationPackageModel, UserModel

router = APIRouter(prefix="/api/v1/application-packages", tags=["application-packages"])


class ApplicationPackageResponse(BaseModel):
    id: UUID
    job_id: UUID
    resume_version_id: UUID
    content: dict[str, object]
    evidence_map: dict[str, object]
    status: str


def _repository(request: Request) -> ApplicationPackageRepository:
    return cast(ApplicationPackageRepository, request.app.state.application_package_repository)


def _response(package: ApplicationPackageModel) -> ApplicationPackageResponse:
    return ApplicationPackageResponse(
        id=package.id,
        job_id=package.job_id,
        resume_version_id=package.resume_version_id,
        content=package.content,
        evidence_map=package.evidence_map,
        status=package.status,
    )


@router.get("/{package_id}", response_model=ApplicationPackageResponse)
async def get_application_package(
    package_id: UUID, request: Request, user: Annotated[UserModel, Depends(current_user)]
) -> ApplicationPackageResponse:
    package = await _repository(request).get(user_id=user.id, package_id=package_id)
    if package is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application package not found."
        )
    return _response(package)
