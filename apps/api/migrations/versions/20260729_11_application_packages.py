"""Create persisted draft application packages.

Revision ID: 20260729_11
Revises: 20260729_10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260729_11"
down_revision: str | None = "20260729_10"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "application_packages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careerpilot.jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "resume_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careerpilot.resume_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("evidence_map", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="DRAFT"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        schema="careerpilot",
    )
    op.create_index(
        "ix_application_packages_user_job_created",
        "application_packages",
        ["user_id", "job_id", "created_at"],
        schema="careerpilot",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_application_packages_user_job_created",
        table_name="application_packages",
        schema="careerpilot",
    )
    op.drop_table("application_packages", schema="careerpilot")
