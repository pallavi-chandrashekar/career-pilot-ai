"""Persistence models. Every future user-owned record must include user_id."""

from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Enum, Index, String
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from careerpilot_api.db.base import TimestampedModel


class UserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class UserModel(TimestampedModel):
    """Authenticated user identity; passwords are held in a separate credential table."""

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_status_created_at", "status", "created_at"),
        {"schema": "careerpilot"},
    )

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(CITEXT(), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status", schema="careerpilot"),
        nullable=False,
        default=UserStatus.ACTIVE,
    )
