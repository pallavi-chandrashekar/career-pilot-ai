"""Authenticated, versioned search profile endpoints."""

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, ValidationError

from careerpilot_api.auth.api import current_user
from careerpilot_api.db.models import SearchProfileModel, SearchProfileVersionModel, UserModel
from careerpilot_api.search_profiles.repository import SearchProfileRepository
from careerpilot_api.search_profiles.schema import SearchProfileConfiguration

router = APIRouter(prefix="/api/v1/search-profiles", tags=["search-profiles"])


class SearchProfileResponse(BaseModel):
    id: UUID
    name: str
    description: str
    is_default: bool
    is_active: bool
    configuration_version: int
    configuration: SearchProfileConfiguration


class DuplicateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)


class StateRequest(BaseModel):
    is_active: bool
    is_default: bool


class ValidationRequest(BaseModel):
    configuration: dict[str, object]


class ValidationResponse(BaseModel):
    valid: bool
    errors: list[str]


def _repository(request: Request) -> SearchProfileRepository:
    return cast(SearchProfileRepository, request.app.state.search_profile_repository)


def _response(
    profile: SearchProfileModel, version: SearchProfileVersionModel
) -> SearchProfileResponse:
    configuration = SearchProfileConfiguration.model_validate(version.configuration).model_copy(
        update={"active": profile.is_active}
    )
    return SearchProfileResponse(
        id=profile.id,
        name=profile.name,
        description=profile.description,
        is_default=profile.is_default,
        is_active=profile.is_active,
        configuration_version=version.version,
        configuration=configuration,
    )


@router.post("", response_model=SearchProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_search_profile(
    configuration: SearchProfileConfiguration,
    request: Request,
    user: Annotated[UserModel, Depends(current_user)],
) -> SearchProfileResponse:
    profile, version = await _repository(request).create(
        user_id=user.id,
        name=configuration.name,
        description=configuration.description,
        is_active=configuration.active,
        configuration=configuration.model_dump(mode="json"),
    )
    return _response(profile, version)


@router.get("", response_model=list[SearchProfileResponse])
async def list_search_profiles(
    request: Request,
    user: Annotated[UserModel, Depends(current_user)],
    active_only: bool = False,
) -> list[SearchProfileResponse]:
    return [
        _response(profile, version)
        for profile, version in await _repository(request).list_current(
            user_id=user.id, active_only=active_only
        )
    ]


@router.get("/{profile_id}", response_model=SearchProfileResponse)
async def get_search_profile(
    profile_id: UUID, request: Request, user: Annotated[UserModel, Depends(current_user)]
) -> SearchProfileResponse:
    result = await _repository(request).get_current(user_id=user.id, profile_id=profile_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Search profile not found.")
    return _response(*result)


@router.put("/{profile_id}", response_model=SearchProfileResponse)
async def update_search_profile(
    profile_id: UUID,
    configuration: SearchProfileConfiguration,
    request: Request,
    user: Annotated[UserModel, Depends(current_user)],
) -> SearchProfileResponse:
    result = await _repository(request).create_version(
        user_id=user.id,
        profile_id=profile_id,
        name=configuration.name,
        description=configuration.description,
        configuration=configuration.model_dump(mode="json"),
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Search profile not found.")
    return _response(*result)


@router.post(
    "/{profile_id}/duplicate",
    response_model=SearchProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def duplicate_search_profile(
    profile_id: UUID,
    payload: DuplicateRequest,
    request: Request,
    user: Annotated[UserModel, Depends(current_user)],
) -> SearchProfileResponse:
    existing = await _repository(request).get_current(user_id=user.id, profile_id=profile_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Search profile not found.")
    _, version = existing
    configuration = SearchProfileConfiguration.model_validate(version.configuration).model_copy(
        update={"name": payload.name or f"{existing[0].name} (copy)", "active": False}
    )
    profile, copied_version = await _repository(request).create(
        user_id=user.id,
        name=configuration.name,
        description=configuration.description,
        is_active=False,
        configuration=configuration.model_dump(mode="json"),
    )
    return _response(profile, copied_version)


@router.post("/{profile_id}/state", response_model=SearchProfileResponse)
async def set_search_profile_state(
    profile_id: UUID,
    payload: StateRequest,
    request: Request,
    user: Annotated[UserModel, Depends(current_user)],
) -> SearchProfileResponse:
    if payload.is_default and not payload.is_active:
        raise HTTPException(status_code=422, detail="A default search profile must be active.")
    profile = await _repository(request).set_state(
        user_id=user.id,
        profile_id=profile_id,
        is_active=payload.is_active,
        is_default=payload.is_default,
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Search profile not found.")
    result = await _repository(request).get_current(user_id=user.id, profile_id=profile.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Search profile not found.")
    return _response(*result)


@router.post("/{profile_id}/validate", response_model=ValidationResponse)
async def validate_search_profile(
    profile_id: UUID,
    payload: ValidationRequest,
    request: Request,
    user: Annotated[UserModel, Depends(current_user)],
) -> ValidationResponse:
    if await _repository(request).get_current(user_id=user.id, profile_id=profile_id) is None:
        raise HTTPException(status_code=404, detail="Search profile not found.")
    try:
        SearchProfileConfiguration.model_validate(payload.configuration)
    except ValidationError as error:
        return ValidationResponse(valid=False, errors=[item["msg"] for item in error.errors()])
    return ValidationResponse(valid=True, errors=[])
