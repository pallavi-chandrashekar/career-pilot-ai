"""Owner-scoped draft claim and extraction workflow persistence."""

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from careerpilot_api.db.models import CandidateClaimModel, WorkflowRunModel


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
