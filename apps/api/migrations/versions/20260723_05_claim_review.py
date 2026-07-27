"""Add candidate claim review states.

Revision ID: 20260723_05
Revises: 20260721_04
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260723_05"
down_revision: str | None = "20260721_04"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE careerpilot.claim_verification_status ADD VALUE IF NOT EXISTS 'APPROVED'"
    )
    op.execute(
        "ALTER TYPE careerpilot.claim_verification_status ADD VALUE IF NOT EXISTS 'REJECTED'"
    )
    op.execute(
        "ALTER TYPE careerpilot.claim_verification_status ADD VALUE IF NOT EXISTS 'ARCHIVED'"
    )


def downgrade() -> None:
    pass
