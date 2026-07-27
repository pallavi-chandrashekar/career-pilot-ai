"""Add normalized job fields.

Revision ID: 20260727_08
Revises: 20260727_07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260727_08"
down_revision: str | None = "20260727_07"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("normalized_requirements", sa.JSON()), schema="careerpilot")
    op.add_column("jobs", sa.Column("seniority", sa.String(64)), schema="careerpilot")
    op.add_column("jobs", sa.Column("compensation", sa.JSON()), schema="careerpilot")
    op.add_column("jobs", sa.Column("sponsorship", sa.String(32)), schema="careerpilot")
    op.add_column("jobs", sa.Column("clearance", sa.String(32)), schema="careerpilot")


def downgrade() -> None:
    for name in (
        "clearance",
        "sponsorship",
        "compensation",
        "seniority",
        "normalized_requirements",
    ):
        op.drop_column("jobs", name, schema="careerpilot")
