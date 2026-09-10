"""
AEGIS API — application factory.

The ``create_app()`` factory is the canonical way to build the FastAPI
instance.  It wires up:

  1. Typed Pydantic settings (``app.config``).
  2. Structured error handlers (``app.errors``).
  3. All route routers (currently: ``/health``; more in later days).

A module-level ``app`` is exported so the Dockerfile CMD
(``uvicorn app.main:app``) keeps working without changes.
"""

from __future__ import annotations

from fastapi import FastAPI

from app.config import get_settings
from app.errors import register_error_handlers
from app.routes.health import router as health_router


def create_app() -> FastAPI:
    """Build and return a fully-configured FastAPI application."""
    settings = get_settings()

    application = FastAPI(
        title="AEGIS API",
        summary="Autonomous Engineering Intelligence & Guarded Software Recovery",
        version="0.1.0",
        docs_url="/docs" if settings.app_env != "production" else None,
        redoc_url="/redoc" if settings.app_env != "production" else None,
    )

    # ── Error handling ──────────────────────────────────────────
    register_error_handlers(application)

    # ── Routers ─────────────────────────────────────────────────
    application.include_router(health_router)

    # ── Root (kept from Day 1 for backward compat) ──────────────
    @application.get("/", include_in_schema=False)
    def root() -> dict:
        return {"service": "aegis-api", "status": "ok"}

    return application


# Module-level instance so `uvicorn app.main:app` works unchanged.
app = create_app()
