"""FastAPI application with liveness and dependency readiness checks."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from careerpilot_api.auth.api import router as auth_router
from careerpilot_api.auth.repository import UserRepository
from careerpilot_api.claims.api import router as claims_router
from careerpilot_api.claims.provider import (
    ClaimExtractionProvider,
    OpenAIClaimExtractionProvider,
    ProviderRegistry,
)
from careerpilot_api.claims.repository import ClaimRepository
from careerpilot_api.config import Settings
from careerpilot_api.documents.api import router as documents_router
from careerpilot_api.documents.crypto import ParsedContentCipher
from careerpilot_api.documents.repository import DocumentRepository
from careerpilot_api.storage.s3 import create_object_storage


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = Settings()
    app.state.settings = settings
    app.state.database = create_async_engine(str(settings.database_url), pool_pre_ping=True)
    session_factory = async_sessionmaker(app.state.database, expire_on_commit=False)
    app.state.user_repository = UserRepository(session_factory)
    app.state.document_repository = DocumentRepository(session_factory)
    app.state.claim_repository = ClaimRepository(session_factory)
    providers: tuple[ClaimExtractionProvider, ...] = ()
    if settings.openai_api_key is not None:
        providers = (OpenAIClaimExtractionProvider(settings.openai_api_key.get_secret_value()),)
    app.state.claim_provider_registry = ProviderRegistry(providers)
    app.state.object_storage = create_object_storage(settings)
    app.state.parsed_content_cipher = ParsedContentCipher(
        settings.parsed_content_encryption_key.get_secret_value()
    )
    try:
        yield
    finally:
        await app.state.database.dispose()


def create_app() -> FastAPI:
    """Create the API without exposing configuration or connection strings."""

    app = FastAPI(title="CareerPilot AI", version="0.1.0", lifespan=lifespan)
    app.include_router(auth_router)
    app.include_router(claims_router)
    app.include_router(documents_router)

    @app.get("/health/live", tags=["health"])
    async def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    async def ready() -> dict[str, str]:
        engine: AsyncEngine = app.state.database
        try:
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database is unavailable.",
            ) from error
        return {"status": "ok"}

    return app


app = create_app()
