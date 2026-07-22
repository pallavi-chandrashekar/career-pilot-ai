"""FastAPI application with liveness and dependency readiness checks."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from careerpilot_api.config import Settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = Settings()
    app.state.database = create_async_engine(str(settings.database_url), pool_pre_ping=True)
    try:
        yield
    finally:
        await app.state.database.dispose()


def create_app() -> FastAPI:
    """Create the API without exposing configuration or connection strings."""

    app = FastAPI(title="CareerPilot AI", version="0.1.0", lifespan=lifespan)

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
