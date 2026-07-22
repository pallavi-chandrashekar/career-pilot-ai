"""Owner-scoped document metadata persistence."""

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from careerpilot_api.db.models import DocumentModel, DocumentStatus


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

    async def save_parse_result(
        self,
        *,
        user_id: UUID,
        document_id: UUID,
        parsed_text_encrypted: str,
        parsed_sections_encrypted: str,
        parser_version: str,
    ) -> DocumentModel | None:
        async with self._session_factory() as session:
            document = await session.scalar(
                select(DocumentModel).where(
                    DocumentModel.user_id == user_id,
                    DocumentModel.id == document_id,
                )
            )
            if document is None:
                return None
            document.parsed_text_encrypted = parsed_text_encrypted
            document.parsed_sections_encrypted = parsed_sections_encrypted
            document.parser_version = parser_version
            document.status = DocumentStatus.PARSED
            await session.commit()
            await session.refresh(document)
            return document
