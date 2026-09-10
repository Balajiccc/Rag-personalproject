"""
Health check endpoint.

Returns the service name, version, environment, and a status field. On Day 3
this will also probe the database; for now it checks only that the API process
itself is responsive.

The typed response model means the contract is enforced at the framework
level — if the return dict ever drifts from the schema, FastAPI raises a
validation error rather than silently returning garbage.
"""

from __future__ import annotations

from pydantic import BaseModel

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings

router = APIRouter(tags=["system"])


# ── Response schema ─────────────────────────────────────────────────


class HealthResponse(BaseModel):
    service: str
    version: str
    status: str
    environment: str


# ── Route ───────────────────────────────────────────────────────────


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System health check",
    description="Returns API process health. DB probe is added on Day 3.",
)
def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        service="aegis-api",
        version="0.1.0",
        status="healthy",
        environment=settings.app_env,
    )
