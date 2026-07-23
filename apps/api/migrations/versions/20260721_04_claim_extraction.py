"""Create draft claims and idempotent extraction workflow records.

Revision ID: 20260721_04
Revises: 20260721_03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260721_04"
down_revision: str | None = "20260721_03"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    verification = postgresql.ENUM(
        "DRAFT", name="claim_verification_status", schema="careerpilot", create_type=False
    )
    workflow_status = postgresql.ENUM(
        "COMPLETED", "FAILED", name="workflow_status", schema="careerpilot", create_type=False
    )
    verification.create(op.get_bind(), checkfirst=True)
    workflow_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "candidate_claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careerpilot.documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("claim_type", sa.String(64), nullable=False),
        sa.Column("canonical_statement", sa.Text(), nullable=False),
        sa.Column("source_locator", sa.JSON(), nullable=False),
        sa.Column("verification_status", verification, nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("model", sa.String(128), nullable=False),
        sa.Column("prompt_version", sa.String(64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        schema="careerpilot",
    )
    op.create_index(
        "ix_candidate_claims_user_status_created_at",
        "candidate_claims",
        ["user_id", "verification_status", "created_at"],
        schema="careerpilot",
    )
    op.create_table(
        "workflow_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careerpilot.users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("workflow_type", sa.String(64), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("status", workflow_status, nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("model", sa.String(128), nullable=False),
        sa.Column("prompt_version", sa.String(64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("idempotency_key", name="uq_workflow_runs_idempotency_key"),
        schema="careerpilot",
    )


def downgrade() -> None:
    op.drop_table("workflow_runs", schema="careerpilot")
    op.drop_index(
        "ix_candidate_claims_user_status_created_at",
        table_name="candidate_claims",
        schema="careerpilot",
    )
    op.drop_table("candidate_claims", schema="careerpilot")
