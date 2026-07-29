"""Add persisted hard-filter decisions.

Revision ID: 20260728_09
Revises: 20260727_08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260728_09"
down_revision: str | None = "20260727_08"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("hard_filter_results", sa.JSON()), schema="careerpilot")
    op.add_column("jobs", sa.Column("hard_filter_override", sa.JSON()), schema="careerpilot")


def downgrade() -> None:
    op.drop_column("jobs", "hard_filter_override", schema="careerpilot")
    op.drop_column("jobs", "hard_filter_results", schema="careerpilot")
