"""Alembic environment for CareerPilot's async PostgreSQL schema."""

from alembic import context
from sqlalchemy import engine_from_config, pool

from careerpilot_api.config import Settings
from careerpilot_api.db import models  # noqa: F401
from careerpilot_api.db.base import Base

config = context.config
config.set_main_option(
    "sqlalchemy.url", str(Settings().database_url).replace("+asyncpg", "+psycopg")
)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
