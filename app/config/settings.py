"""Application settings loaded from environment variables."""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # App
    app_name: str = "VQA Backend"
    app_env: str = "development"
    api_key: str = "change-me-supersecret"

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/app.db"

    # OCR
    ocr_languages: str = "en"
    ocr_gpu: bool = False
    temp_image_dir: str = "./data/uploads"

    # LLM
    llm_provider: Literal["ollama", "gemini", "openai"] = "gemini"
    llm_model: str = "gemini-1.5-flash"
    llm_temperature: float = 0.2

    openai_api_key: str | None = None
    google_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    # Cache
    cache_size: int = 128
    similarity_threshold: float = 0.92

    # Rate limiting
    rate_limit: str = "30/minute"

    # Logging
    log_level: str = "INFO"

    @property
    def ocr_lang_list(self) -> list[str]:
        return [l.strip() for l in self.ocr_languages.split(",") if l.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()