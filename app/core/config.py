from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NewEcon Finance API"
    app_version: str = "0.2.0"
    group_name: str = "NewEcon"
    database_url: str = "sqlite:///./data/fintech.db"
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://127.0.0.1:5500", "http://localhost:5500"]
    )
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CBU_", case_sensitive=False)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
