"""Create immutable structured resume versions.

Revision ID: 20260729_10
Revises: 20260728_09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260729_10"
down_revision: str | None = "20260728_09"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "resume_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("content_model", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "parent_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careerpilot.resume_versions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        schema="careerpilot",
    )
    op.create_index(
        "ix_resume_versions_user_created_at",
        "resume_versions",
        ["user_id", "created_at"],
        schema="careerpilot",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_resume_versions_user_created_at", table_name="resume_versions", schema="careerpilot"
    )
    op.drop_table("resume_versions", schema="careerpilot")
