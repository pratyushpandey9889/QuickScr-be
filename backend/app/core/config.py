from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "QuickScribe Enterprise Accelerator"
    app_env: str = "local"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[AnyHttpUrl | str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )
    database_url: str = "postgresql+asyncpg://quickscribe:quickscribe@localhost:5432/quickscribe"
    jwt_issuer: str = ""
    jwt_audience: str = ""
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""
    sharepoint_site_id: str = ""
    sap_base_url: str = ""
    sap_client: str = ""
    sap_username: str = ""
    sap_password: str = ""
    openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    pinecone_api_key: str = ""
    pinecone_index: str = "quickscribe-documents"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
