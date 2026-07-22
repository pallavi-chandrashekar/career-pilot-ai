"""Add encrypted parsed document content and parser metadata.

Revision ID: 20260721_03
Revises: 20260721_02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260721_03"
down_revision: str | None = "20260721_02"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE careerpilot.document_status ADD VALUE IF NOT EXISTS 'PARSED'")
    op.execute("ALTER TYPE careerpilot.document_status ADD VALUE IF NOT EXISTS 'PARSE_FAILED'")
    op.add_column(
        "documents",
        sa.Column("parsed_text_encrypted", sa.Text(), nullable=True),
        schema="careerpilot",
    )
    op.add_column(
        "documents",
        sa.Column("parsed_sections_encrypted", sa.Text(), nullable=True),
        schema="careerpilot",
    )
    op.add_column(
        "documents", sa.Column("parser_version", sa.String(32), nullable=True), schema="careerpilot"
    )


def downgrade() -> None:
    op.drop_column("documents", "parser_version", schema="careerpilot")
    op.drop_column("documents", "parsed_sections_encrypted", schema="careerpilot")
    op.drop_column("documents", "parsed_text_encrypted", schema="careerpilot")
