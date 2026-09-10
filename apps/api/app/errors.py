"""
Structured error handling for the AEGIS API.

Every error the API returns follows the same JSON shape:

    {
      "error": {
        "code": "NOT_FOUND",
        "message": "Task abc123 not found.",
        "details": {}          # optional extra context
      }
    }

FastAPI exception handlers are registered in the app factory so they
apply uniformly, including to unhandled 422 validation errors.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


# ── Envelope ────────────────────────────────────────────────────────


def _error_body(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict:
    body: dict[str, Any] = {"code": code, "message": message}
    if details:
        body["details"] = details
    return {"error": body}


# ── Application exceptions ──────────────────────────────────────────


class AEGISError(Exception):
    """Base for all AEGIS domain errors."""

    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class NotFoundError(AEGISError):
    status_code = 404
    code = "NOT_FOUND"

    def __init__(
        self,
        resource: str = "Resource",
        resource_id: str = "",
        details: dict[str, Any] | None = None,
    ) -> None:
        msg = f"{resource} {resource_id} not found." if resource_id else f"{resource} not found."
        super().__init__(message=msg, details=details)


class ConflictError(AEGISError):
    status_code = 409
    code = "CONFLICT"


class ForbiddenError(AEGISError):
    status_code = 403
    code = "FORBIDDEN"


class BadRequestError(AEGISError):
    status_code = 400
    code = "BAD_REQUEST"


# ── Exception handlers (registered in the app factory) ──────────────


def _handle_aegis_error(_request: Request, exc: AEGISError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.code, exc.message, exc.details),
    )


def _handle_validation_error(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_error_body(
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            details={"errors": exc.errors()},
        ),
    )


_HTTP_CODE_MAP: dict[int, str] = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    429: "RATE_LIMITED",
}


def _handle_http_exception(
    _request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    code = _HTTP_CODE_MAP.get(exc.status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(code, str(exc.detail)),
    )


def _handle_unhandled(_request: Request, exc: Exception) -> JSONResponse:
    # In production you'd log exc here and redact the message.
    return JSONResponse(
        status_code=500,
        content=_error_body(
            code="INTERNAL_ERROR",
            message=str(exc) if exc.args else "An unexpected error occurred.",
        ),
    )


def register_error_handlers(app: FastAPI) -> None:
    """Attach all exception handlers to the given app instance."""
    app.add_exception_handler(AEGISError, _handle_aegis_error)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, _handle_http_exception)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _handle_validation_error)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _handle_unhandled)
