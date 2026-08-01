from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings. Override via environment or backend/.env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "FurniCost API"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    # Gemini — free tier: Flash-class only. Never send raw financial data.
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_free_tier: bool = True

    # Neo4j knowledge graph
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "furnicost-dev"
    neo4j_database: str = "neo4j"

    # Postgres (LangGraph checkpointer, reports)
    postgres_dsn: str = "postgresql://furnicost:furnicost@localhost:5432/furnicost"

    # Langfuse observability
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "http://localhost:3000"
    langfuse_enabled: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_prod(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
