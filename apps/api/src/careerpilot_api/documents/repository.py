"""Owner-scoped document metadata persistence."""

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from careerpilot_api.db.models import DocumentModel


class DocumentRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_by_checksum(self, *, user_id: UUID, checksum: str) -> DocumentModel | None:
        async with self._session_factory() as session:
            return cast(
                DocumentModel | None,
                await session.scalar(
                    select(DocumentModel).where(
                        DocumentModel.user_id == user_id,
                        DocumentModel.checksum == checksum,
                    )
                ),
            )

    async def get_by_id(self, *, user_id: UUID, document_id: UUID) -> DocumentModel | None:
        async with self._session_factory() as session:
            return cast(
                DocumentModel | None,
                await session.scalar(
                    select(DocumentModel).where(
                        DocumentModel.user_id == user_id,
                        DocumentModel.id == document_id,
                    )
                ),
            )

    async def create(self, document: DocumentModel) -> DocumentModel:
        async with self._session_factory() as session:
            session.add(document)
            await session.commit()
            await session.refresh(document)
            return document
