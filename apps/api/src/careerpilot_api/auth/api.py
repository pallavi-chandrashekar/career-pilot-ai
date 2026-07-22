"""Versioned authentication API with generic credential failures."""

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from careerpilot_api.auth.repository import UserRepository
from careerpilot_api.auth.security import (
    hash_password,
    issue_access_token,
    verify_access_token,
    verify_password,
)
from careerpilot_api.config import Settings
from careerpilot_api.db.models import UserModel, UserStatus

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=120)
    timezone: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    display_name: str
    timezone: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _repository(request: Request) -> UserRepository:
    return cast(UserRepository, request.app.state.user_repository)


async def current_user(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> UserModel:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication is required.")
    settings: Settings = request.app.state.settings
    user_id = verify_access_token(
        authorization.removeprefix("Bearer "), settings.auth_secret.get_secret_value()
    )
    user = None if user_id is None else await _repository(request).get_by_id(user_id)
    if user is None or user.status is not UserStatus.ACTIVE:
        raise HTTPException(status_code=401, detail="Authentication is required.")
    return user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, request: Request) -> TokenResponse:
    repository = _repository(request)
    email = str(payload.email).casefold()
    if await repository.get_by_email(email) is not None:
        raise HTTPException(status_code=409, detail="An account already exists for this email.")
    user = await repository.create(
        UserModel(
            email=email,
            password_hash=hash_password(payload.password),
            display_name=payload.display_name,
            timezone=payload.timezone,
        )
    )
    settings: Settings = request.app.state.settings
    return TokenResponse(
        access_token=issue_access_token(
            user.id, settings.auth_secret.get_secret_value(), settings.auth_access_token_minutes
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, request: Request) -> TokenResponse:
    user = await _repository(request).get_by_email(str(payload.email).casefold())
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    settings: Settings = request.app.state.settings
    return TokenResponse(
        access_token=issue_access_token(
            user.id, settings.auth_secret.get_secret_value(), settings.auth_access_token_minutes
        )
    )


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[UserModel, Depends(current_user)]) -> UserResponse:
    return UserResponse(
        id=user.id, email=user.email, display_name=user.display_name, timezone=user.timezone
    )
