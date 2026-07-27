"""Create manual job ingestion storage.

Revision ID: 20260727_07
Revises: 20260727_06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260727_07"
down_revision: str | None = "20260727_06"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(255)),
        sa.Column("canonical_url", sa.String(2048)),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("user_id", "fingerprint", name="uq_jobs_user_fingerprint"),
        schema="careerpilot",
    )
    op.create_index(
        "ix_jobs_user_created_at", "jobs", ["user_id", "created_at"], schema="careerpilot"
    )
    op.create_table(
        "job_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "job_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careerpilot.jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("source_url", sa.String(2048)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        schema="careerpilot",
    )
    op.create_index(
        "ix_job_sources_job_created_at",
        "job_sources",
        ["job_id", "created_at"],
        schema="careerpilot",
    )


def downgrade() -> None:
    op.drop_index("ix_job_sources_job_created_at", table_name="job_sources", schema="careerpilot")
    op.drop_table("job_sources", schema="careerpilot")
    op.drop_index("ix_jobs_user_created_at", table_name="jobs", schema="careerpilot")
    op.drop_table("jobs", schema="careerpilot")
