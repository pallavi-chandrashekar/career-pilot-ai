"""Owner-scoped draft claim and extraction workflow persistence."""

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from careerpilot_api.db.models import CandidateClaimModel, ClaimVerificationStatus, WorkflowRunModel


class ClaimRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_workflow_by_key(self, key: str) -> WorkflowRunModel | None:
        async with self._session_factory() as session:
            return cast(
                WorkflowRunModel | None,
                await session.scalar(
                    select(WorkflowRunModel).where(WorkflowRunModel.idempotency_key == key)
                ),
            )

    async def create_workflow_with_claims(
        self, workflow: WorkflowRunModel, claims: list[CandidateClaimModel]
    ) -> WorkflowRunModel:
        async with self._session_factory() as session:
            session.add(workflow)
            session.add_all(claims)
            await session.commit()
            await session.refresh(workflow)
            return workflow

    async def list_claims(self, *, user_id: UUID) -> list[CandidateClaimModel]:
        async with self._session_factory() as session:
            return list(
                (
                    await session.scalars(
                        select(CandidateClaimModel)
                        .where(CandidateClaimModel.user_id == user_id)
                        .order_by(CandidateClaimModel.created_at.desc())
                    )
                ).all()
            )

    async def get_by_id(self, *, user_id: UUID, claim_id: UUID) -> CandidateClaimModel | None:
        async with self._session_factory() as session:
            return cast(
                CandidateClaimModel | None,
                await session.scalar(
                    select(CandidateClaimModel).where(
                        CandidateClaimModel.user_id == user_id, CandidateClaimModel.id == claim_id
                    )
                ),
            )

    async def set_status(
        self, *, user_id: UUID, claim_id: UUID, claim_status: ClaimVerificationStatus
    ) -> CandidateClaimModel | None:
        async with self._session_factory() as session:
            claim = await session.scalar(
                select(CandidateClaimModel).where(
                    CandidateClaimModel.user_id == user_id, CandidateClaimModel.id == claim_id
                )
            )
            if claim is None:
                return None
            claim.verification_status = claim_status
            await session.commit()
            await session.refresh(claim)
            return claim

    async def approve_drafts(
        self, *, user_id: UUID, claim_ids: list[UUID]
    ) -> list[CandidateClaimModel]:
        """Approve a complete owner-scoped draft selection in one transaction."""
        async with self._session_factory() as session:
            claims = list(
                (
                    await session.scalars(
                        select(CandidateClaimModel).where(
                            CandidateClaimModel.user_id == user_id,
                            CandidateClaimModel.id.in_(claim_ids),
                        )
                    )
                ).all()
            )
            if len(claims) != len(claim_ids):
                raise LookupError("One or more claims were not found.")
            if any(
                claim.verification_status is not ClaimVerificationStatus.DRAFT for claim in claims
            ):
                raise ValueError("Only draft claims can be approved.")
            for claim in claims:
                claim.verification_status = ClaimVerificationStatus.APPROVED
            await session.commit()
            for claim in claims:
                await session.refresh(claim)
            return claims

    async def edit_draft(
        self, *, user_id: UUID, claim_id: UUID, canonical_statement: str
    ) -> CandidateClaimModel | None:
        async with self._session_factory() as session:
            claim = await session.scalar(
                select(CandidateClaimModel).where(
                    CandidateClaimModel.user_id == user_id, CandidateClaimModel.id == claim_id
                )
            )
            if claim is None:
                return None
            if claim.verification_status is not ClaimVerificationStatus.DRAFT:
                raise ValueError("Only draft claims can be edited.")
            claim.canonical_statement = canonical_statement
            await session.commit()
            await session.refresh(claim)
            return claim
