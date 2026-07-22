"""Create owner-scoped uploaded document metadata.

Revision ID: 20260721_02
Revises: 20260721_01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260721_02"
down_revision: str | None = "20260721_01"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    document_status = postgresql.ENUM(
        "UPLOADED", name="document_status", schema="careerpilot", create_type=False
    )
    document_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("document_type", sa.String(32), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(128), nullable=False),
        sa.Column("storage_key", sa.String(512), nullable=False, unique=True),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("status", document_status, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("user_id", "checksum", name="uq_documents_user_checksum"),
        schema="careerpilot",
    )
    op.create_index(
        "ix_documents_user_status_created_at",
        "documents",
        ["user_id", "status", "created_at"],
        schema="careerpilot",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_documents_user_status_created_at", table_name="documents", schema="careerpilot"
    )
    op.drop_table("documents", schema="careerpilot")
    postgresql.ENUM(name="document_status", schema="careerpilot").drop(
        op.get_bind(), checkfirst=True
    )
