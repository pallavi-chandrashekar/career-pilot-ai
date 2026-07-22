"""Owner identity repository; future repositories must require user_id."""

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from careerpilot_api.db.models import UserModel


class UserRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_by_email(self, email: str) -> UserModel | None:
        async with self._session_factory() as session:
            return cast(
                UserModel | None,
                await session.scalar(select(UserModel).where(UserModel.email == email)),
            )

    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        async with self._session_factory() as session:
            return await session.get(UserModel, user_id)

    async def create(self, user: UserModel) -> UserModel:
        async with self._session_factory() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
