from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from careerpilot_api.db.models import JobModel, JobSourceModel


class JobRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(self, job: JobModel, source: JobSourceModel) -> JobModel:
        async with self._session_factory() as session:
            session.add(job)
            await session.flush()
            source.job_id = job.id
            session.add(source)
            await session.commit()
            await session.refresh(job)
            return job

    async def find_duplicate(
        self, *, user_id: UUID, fingerprint: str, canonical_url: str | None
    ) -> JobModel | None:
        async with self._session_factory() as session:
            statement = select(JobModel).where(
                JobModel.user_id == user_id, JobModel.fingerprint == fingerprint
            )
            job = await session.scalar(statement)
            if job is None and canonical_url is not None:
                job = await session.scalar(
                    select(JobModel).where(
                        JobModel.user_id == user_id, JobModel.canonical_url == canonical_url
                    )
                )
            return job

    async def add_source(self, *, job_id: UUID, source: JobSourceModel) -> None:
        async with self._session_factory() as session:
            source.job_id = job_id
            session.add(source)
            await session.commit()

    async def list(self, *, user_id: UUID) -> list[JobModel]:
        async with self._session_factory() as session:
            return list(
                (
                    await session.scalars(
                        select(JobModel)
                        .where(JobModel.user_id == user_id)
                        .order_by(JobModel.created_at.desc())
                    )
                ).all()
            )

    async def get(self, *, user_id: UUID, job_id: UUID) -> JobModel | None:
        async with self._session_factory() as session:
            return cast(
                JobModel | None,
                await session.scalar(
                    select(JobModel).where(JobModel.user_id == user_id, JobModel.id == job_id)
                ),
            )

    async def save_normalization(
        self, *, user_id: UUID, job_id: UUID, value: dict[str, object]
    ) -> JobModel | None:
        async with self._session_factory() as session:
            job = await session.scalar(
                select(JobModel).where(JobModel.user_id == user_id, JobModel.id == job_id)
            )
            if job is None:
                return None
            job.normalized_requirements = value["requirements"]  # type: ignore[assignment]
            job.seniority = value["seniority"]  # type: ignore[assignment]
            job.compensation = value["compensation"]  # type: ignore[assignment]
            job.sponsorship = value["sponsorship"]  # type: ignore[assignment]
            job.clearance = value["clearance"]  # type: ignore[assignment]
            await session.commit()
            await session.refresh(job)
            return job
