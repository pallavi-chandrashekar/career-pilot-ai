"""Add application package export metadata.

Revision ID: 20260801_12
Revises: 20260729_11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260801_12"
down_revision: str | None = "20260729_11"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "application_packages", sa.Column("docx_storage_key", sa.String(512)), schema="careerpilot"
    )
    op.add_column(
        "application_packages", sa.Column("pdf_storage_key", sa.String(512)), schema="careerpilot"
    )


def downgrade() -> None:
    op.drop_column("application_packages", "pdf_storage_key", schema="careerpilot")
    op.drop_column("application_packages", "docx_storage_key", schema="careerpilot")
