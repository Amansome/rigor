"""Pydantic-settings configuration for the application."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    ollama_base_url: str = "http://localhost:11434"
    use_hosted_models: bool = False
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
