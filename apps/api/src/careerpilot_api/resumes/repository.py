"""Owner-scoped immutable resume version persistence."""

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from careerpilot_api.db.models import ResumeVersionModel


class ResumeRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(self, resume: ResumeVersionModel) -> ResumeVersionModel:
        async with self._session_factory() as session:
            session.add(resume)
            await session.commit()
            await session.refresh(resume)
            return resume

    async def get(self, *, user_id: UUID, resume_id: UUID) -> ResumeVersionModel | None:
        async with self._session_factory() as session:
            return cast(
                ResumeVersionModel | None,
                await session.scalar(
                    select(ResumeVersionModel).where(
                        ResumeVersionModel.user_id == user_id, ResumeVersionModel.id == resume_id
                    )
                ),
            )

    async def list(self, *, user_id: UUID) -> list[ResumeVersionModel]:
        async with self._session_factory() as session:
            return list(
                (
                    await session.scalars(
                        select(ResumeVersionModel)
                        .where(ResumeVersionModel.user_id == user_id)
                        .order_by(ResumeVersionModel.created_at.desc())
                    )
                ).all()
            )
