"""Validated, non-secret API configuration."""

from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded without logging sensitive connection values."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: PostgresDsn = PostgresDsn(
        "postgresql+asyncpg://careerpilot:careerpilot@postgres:5432/careerpilot"
    )
    auth_secret: SecretStr = SecretStr("development-only-change-me")
    auth_access_token_minutes: int = 30
    object_storage_endpoint: str = "http://minio:9000"
    object_storage_bucket: str = "careerpilot-documents"
    object_storage_access_key: str = "careerpilot"
    object_storage_secret_key: SecretStr = SecretStr("careerpilot-development-only")
    parsed_content_encryption_key: SecretStr = SecretStr(
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    )
    openai_api_key: SecretStr | None = None
    llm_default_provider: str = "openai"
    llm_default_model: str = "gpt-5.6-sol"
