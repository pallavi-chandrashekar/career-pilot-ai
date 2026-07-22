"""Persistence models. Every future user-owned record must include user_id."""

from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from careerpilot_api.db.base import TimestampedModel


class UserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class DocumentStatus(StrEnum):
    UPLOADED = "UPLOADED"
    PARSED = "PARSED"
    PARSE_FAILED = "PARSE_FAILED"


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


class DocumentModel(TimestampedModel):
    """Owner-scoped uploaded document metadata; bytes reside in object storage."""

    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("user_id", "checksum", name="uq_documents_user_checksum"),
        Index("ix_documents_user_status_created_at", "user_id", "status", "created_at"),
        {"schema": "careerpilot"},
    )

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    document_type: Mapped[str] = mapped_column(String(32), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    parsed_text_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_sections_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    parser_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status", schema="careerpilot"),
        nullable=False,
        default=DocumentStatus.UPLOADED,
    )
