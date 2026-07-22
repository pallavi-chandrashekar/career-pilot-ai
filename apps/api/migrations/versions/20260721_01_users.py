"""Create user identities.

Revision ID: 20260721_01
Revises:
Create Date: 2026-07-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260721_01"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS careerpilot")
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    user_status = postgresql.ENUM(
        "ACTIVE", "DISABLED", name="user_status", schema="careerpilot", create_type=False
    )
    user_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", postgresql.CITEXT(), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False),
        sa.Column("status", user_status, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        schema="careerpilot",
    )
    op.create_index(
        "ix_users_status_created_at", "users", ["status", "created_at"], schema="careerpilot"
    )


def downgrade() -> None:
    op.drop_index("ix_users_status_created_at", table_name="users", schema="careerpilot")
    op.drop_table("users", schema="careerpilot")
    postgresql.ENUM(name="user_status", schema="careerpilot").drop(op.get_bind(), checkfirst=True)
