"""Owner-scoped application package persistence."""

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from careerpilot_api.db.models import ApplicationPackageModel


class ApplicationPackageRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(self, package: ApplicationPackageModel) -> ApplicationPackageModel:
        async with self._session_factory() as session:
            session.add(package)
            await session.commit()
            await session.refresh(package)
            return package

    async def get(self, *, user_id: UUID, package_id: UUID) -> ApplicationPackageModel | None:
        async with self._session_factory() as session:
            return cast(
                ApplicationPackageModel | None,
                await session.scalar(
                    select(ApplicationPackageModel).where(
                        ApplicationPackageModel.user_id == user_id,
                        ApplicationPackageModel.id == package_id,
                    )
                ),
            )

    async def save_export_keys(
        self, *, user_id: UUID, package_id: UUID, docx_key: str, pdf_key: str
    ) -> ApplicationPackageModel | None:
        async with self._session_factory() as session:
            package = await session.scalar(
                select(ApplicationPackageModel).where(
                    ApplicationPackageModel.user_id == user_id,
                    ApplicationPackageModel.id == package_id,
                )
            )
            if package is None:
                return None
            package.docx_storage_key = docx_key
            package.pdf_storage_key = pdf_key
            await session.commit()
            await session.refresh(package)
            return package
