"""Application settings shared by the API, agent, and MCP server."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed local runtime configuration."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    database_url: str = "postgresql+psycopg://orion_reader:orion_reader_dev@localhost:5432/orion"
    database_admin_url: str = "postgresql+psycopg://orion_admin:orion_admin_dev@localhost:5432/orion"
    mcp_server_url: str = "http://localhost:8000/mcp"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "local-only"
    llm_model: str = "qwen2.5:3b"
    max_history_messages: int = Field(default=20, ge=2, le=100)
    max_tool_rounds: int = Field(default=4, ge=1, le=10)
    mcp_discovery_attempts: int = Field(default=30, ge=1, le=120)
    mcp_discovery_retry_seconds: float = Field(default=1.0, gt=0, le=10)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a process-cached settings instance."""
    return Settings()
