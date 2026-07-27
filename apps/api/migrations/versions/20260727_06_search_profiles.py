"""Create versioned search profile storage.

Revision ID: 20260727_06
Revises: 20260723_05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260727_06"
down_revision: str | None = "20260723_05"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "search_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("current_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        schema="careerpilot",
    )
    op.create_index(
        "ix_search_profiles_user_active_created_at",
        "search_profiles",
        ["user_id", "is_active", "created_at"],
        schema="careerpilot",
    )
    op.create_index(
        "ix_search_profiles_user_default",
        "search_profiles",
        ["user_id", "is_default"],
        schema="careerpilot",
    )
    op.create_table(
        "search_profile_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careerpilot.search_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("configuration", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint(
            "profile_id", "version", name="uq_search_profile_versions_profile_version"
        ),
        schema="careerpilot",
    )
    op.create_index(
        "ix_search_profile_versions_profile_version",
        "search_profile_versions",
        ["profile_id", "version"],
        schema="careerpilot",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_search_profile_versions_profile_version",
        table_name="search_profile_versions",
        schema="careerpilot",
    )
    op.drop_table("search_profile_versions", schema="careerpilot")
    op.drop_index(
        "ix_search_profiles_user_default", table_name="search_profiles", schema="careerpilot"
    )
    op.drop_index(
        "ix_search_profiles_user_active_created_at",
        table_name="search_profiles",
        schema="careerpilot",
    )
    op.drop_table("search_profiles", schema="careerpilot")
