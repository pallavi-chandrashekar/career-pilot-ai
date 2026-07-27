"""Owner-scoped immutable search profile persistence."""

from typing import cast
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from careerpilot_api.db.models import SearchProfileModel, SearchProfileVersionModel


class SearchProfileRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(
        self,
        *,
        user_id: UUID,
        name: str,
        description: str,
        is_active: bool,
        configuration: dict[str, object],
    ) -> tuple[SearchProfileModel, SearchProfileVersionModel]:
        async with self._session_factory() as session:
            profile = SearchProfileModel(
                user_id=user_id, name=name, description=description, is_active=is_active
            )
            session.add(profile)
            await session.flush()
            version = SearchProfileVersionModel(
                profile_id=profile.id, version=1, configuration=configuration
            )
            session.add(version)
            await session.commit()
            await session.refresh(profile)
            await session.refresh(version)
            return profile, version

    async def list_current(
        self, *, user_id: UUID, active_only: bool = False
    ) -> list[tuple[SearchProfileModel, SearchProfileVersionModel]]:
        async with self._session_factory() as session:
            statement = (
                select(SearchProfileModel, SearchProfileVersionModel)
                .join(
                    SearchProfileVersionModel,
                    (SearchProfileVersionModel.profile_id == SearchProfileModel.id)
                    & (SearchProfileVersionModel.version == SearchProfileModel.current_version),
                )
                .where(SearchProfileModel.user_id == user_id)
                .order_by(SearchProfileModel.created_at.desc())
            )
            if active_only:
                statement = statement.where(SearchProfileModel.is_active.is_(True))
            return list((await session.execute(statement)).tuples().all())

    async def get_current(
        self, *, user_id: UUID, profile_id: UUID
    ) -> tuple[SearchProfileModel, SearchProfileVersionModel] | None:
        async with self._session_factory() as session:
            return cast(
                tuple[SearchProfileModel, SearchProfileVersionModel] | None,
                (
                    await session.execute(
                        select(SearchProfileModel, SearchProfileVersionModel)
                        .join(
                            SearchProfileVersionModel,
                            (SearchProfileVersionModel.profile_id == SearchProfileModel.id)
                            & (
                                SearchProfileVersionModel.version
                                == SearchProfileModel.current_version
                            ),
                        )
                        .where(
                            SearchProfileModel.user_id == user_id,
                            SearchProfileModel.id == profile_id,
                        )
                    )
                ).one_or_none(),
            )

    async def create_version(
        self,
        *,
        user_id: UUID,
        profile_id: UUID,
        name: str,
        description: str,
        configuration: dict[str, object],
    ) -> tuple[SearchProfileModel, SearchProfileVersionModel] | None:
        async with self._session_factory() as session:
            profile = await session.scalar(
                select(SearchProfileModel).where(
                    SearchProfileModel.user_id == user_id, SearchProfileModel.id == profile_id
                )
            )
            if profile is None:
                return None
            version_number = profile.current_version + 1
            version = SearchProfileVersionModel(
                profile_id=profile.id, version=version_number, configuration=configuration
            )
            profile.name = name
            profile.description = description
            profile.current_version = version_number
            session.add(version)
            await session.commit()
            await session.refresh(profile)
            await session.refresh(version)
            return profile, version

    async def set_state(
        self, *, user_id: UUID, profile_id: UUID, is_active: bool, is_default: bool
    ) -> SearchProfileModel | None:
        async with self._session_factory() as session:
            profile = await session.scalar(
                select(SearchProfileModel).where(
                    SearchProfileModel.user_id == user_id, SearchProfileModel.id == profile_id
                )
            )
            if profile is None:
                return None
            if is_default:
                await session.execute(
                    update(SearchProfileModel)
                    .where(SearchProfileModel.user_id == user_id)
                    .values(is_default=False)
                )
            profile.is_active = is_active
            profile.is_default = is_default
            await session.commit()
            await session.refresh(profile)
            return profile
