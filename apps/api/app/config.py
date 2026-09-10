"""
Typed application settings.

All configuration is read from environment variables (or .env via
pydantic-settings). This module is the single source of truth — no
hardcoded connection strings, ports, or model names anywhere else.

New config categories are added here as the project grows (Days 6, 25,
32, 48 per the roadmap), but the existing fields must stay
backward-compatible.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AEGIS API configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore env vars not declared here
    )

    # ---- App ----
    app_env: Literal["local", "test", "staging", "production"] = "local"

    # ---- API ----
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # ---- Database (wired Day 3) ----
    database_url: str = "postgresql://aegis:aegis_dev_password@db:5432/aegis"

    # ---- Observability ----
    log_level: Literal[
        "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    ] = "INFO"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance (parsed once per process)."""
    return Settings()
