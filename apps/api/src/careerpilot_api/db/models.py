"""Persistence models. Every future user-owned record must include user_id."""

from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, Enum, ForeignKey, Index, String, Text, UniqueConstraint
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


class ClaimVerificationStatus(StrEnum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class WorkflowStatus(StrEnum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


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


class CandidateClaimModel(TimestampedModel):
    __tablename__ = "candidate_claims"
    __table_args__ = (
        Index(
            "ix_candidate_claims_user_status_created_at",
            "user_id",
            "verification_status",
            "created_at",
        ),
        {"schema": "careerpilot"},
    )

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_document_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("careerpilot.documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    claim_type: Mapped[str] = mapped_column(String(64), nullable=False)
    canonical_statement: Mapped[str] = mapped_column(Text, nullable=False)
    source_locator: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False)
    verification_status: Mapped[ClaimVerificationStatus] = mapped_column(
        Enum(ClaimVerificationStatus, name="claim_verification_status", schema="careerpilot"),
        nullable=False,
        default=ClaimVerificationStatus.DRAFT,
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(64), nullable=False)


class SearchProfileModel(TimestampedModel):
    """Owner-scoped search-profile identity and current operational state."""

    __tablename__ = "search_profiles"
    __table_args__ = (
        Index("ix_search_profiles_user_active_created_at", "user_id", "is_active", "created_at"),
        Index("ix_search_profiles_user_default", "user_id", "is_default"),
        {"schema": "careerpilot"},
    )

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_default: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=False)
    current_version: Mapped[int] = mapped_column(nullable=False, default=1)


class SearchProfileVersionModel(TimestampedModel):
    """Immutable validated configuration history for a search profile."""

    __tablename__ = "search_profile_versions"
    __table_args__ = (
        UniqueConstraint(
            "profile_id", "version", name="uq_search_profile_versions_profile_version"
        ),
        Index("ix_search_profile_versions_profile_version", "profile_id", "version"),
        {"schema": "careerpilot"},
    )

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    profile_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("careerpilot.search_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(nullable=False)
    configuration: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class JobModel(TimestampedModel):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("user_id", "fingerprint", name="uq_jobs_user_fingerprint"),
        Index("ix_jobs_user_created_at", "user_id", "created_at"),
        {"schema": "careerpilot"},
    )

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    canonical_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    normalized_requirements: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    seniority: Mapped[str | None] = mapped_column(String(64), nullable=True)
    compensation: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    sponsorship: Mapped[str | None] = mapped_column(String(32), nullable=True)
    clearance: Mapped[str | None] = mapped_column(String(32), nullable=True)
    hard_filter_results: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    hard_filter_override: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)


class JobSourceModel(TimestampedModel):
    __tablename__ = "job_sources"
    __table_args__ = (
        Index("ix_job_sources_job_created_at", "job_id", "created_at"),
        {"schema": "careerpilot"},
    )

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("careerpilot.jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, default="MANUAL")
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)


class ResumeVersionModel(TimestampedModel):
    """Immutable, owner-scoped structured resume version backed by approved claims."""

    __tablename__ = "resume_versions"
    __table_args__ = (
        Index("ix_resume_versions_user_created_at", "user_id", "created_at"),
        {"schema": "careerpilot"},
    )

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    content_model: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    parent_version_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("careerpilot.resume_versions.id", ondelete="SET NULL"),
        nullable=True,
    )


class ApplicationPackageModel(TimestampedModel):
    """Draft application material and its claim-level evidence map."""

    __tablename__ = "application_packages"
    __table_args__ = (
        Index("ix_application_packages_user_job_created", "user_id", "job_id", "created_at"),
        {"schema": "careerpilot"},
    )

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("careerpilot.jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    resume_version_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("careerpilot.resume_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    content: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    evidence_map: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    docx_storage_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    pdf_storage_key: Mapped[str | None] = mapped_column(String(512), nullable=True)


class WorkflowRunModel(TimestampedModel):
    __tablename__ = "workflow_runs"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_workflow_runs_idempotency_key"),
        {"schema": "careerpilot"},
    )

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    workflow_type: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[WorkflowStatus] = mapped_column(
        Enum(WorkflowStatus, name="workflow_status", schema="careerpilot"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(64), nullable=False)
