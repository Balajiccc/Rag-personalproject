"""
Day 2 — API foundation tests.

These run in-process via FastAPI's TestClient (no external server needed).
They verify the five Day 2 deliverables:

  1. App factory produces a working FastAPI instance.
  2. /health returns a typed, correct response.
  3. Structured error envelope is used for all error responses.
  4. Pydantic settings are loaded and injected.
  5. Backward compat: the Day 1 root route still works.
"""

import sys
from pathlib import Path

import pytest

# ── Make the api package importable from the repo root ──────────────
API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app, create_app  # noqa: E402
from app.errors import NotFoundError, BadRequestError  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# ── 1. App factory ──────────────────────────────────────────────────


class TestAppFactory:
    def test_create_app_returns_fastapi_instance(self):
        from fastapi import FastAPI

        result = create_app()
        assert isinstance(result, FastAPI)

    def test_create_app_sets_title(self):
        result = create_app()
        assert result.title == "AEGIS API"


# ── 2. Health endpoint (the Day 2 acceptance gate) ──────────────────


class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_response_shape(self, client: TestClient):
        data = client.get("/health").json()
        assert data["service"] == "aegis-api"
        assert data["version"] == "0.1.0"
        assert data["status"] == "healthy"
        assert "environment" in data

    def test_health_environment_from_settings(self, client: TestClient):
        """Settings injection works — environment reflects APP_ENV."""
        data = client.get("/health").json()
        # In the test runner APP_ENV defaults to 'local' unless overridden.
        assert data["environment"] in ("local", "test")


# ── 3. Structured error envelope ────────────────────────────────────


class TestStructuredErrors:
    def test_unknown_route_returns_structured_404(self, client: TestClient):
        r = client.get("/this/route/does/not/exist")
        assert r.status_code == 404
        body = r.json()
        assert "error" in body
        assert body["error"]["code"] == "NOT_FOUND"

    def test_domain_not_found_error(self):
        """AEGISError subclasses produce the correct envelope."""
        test_app = create_app()

        @test_app.get("/test-not-found")
        def _raise_not_found():
            raise NotFoundError(resource="Task", resource_id="abc123")

        tc = TestClient(test_app, raise_server_exceptions=False)
        r = tc.get("/test-not-found")
        assert r.status_code == 404
        body = r.json()
        assert body["error"]["code"] == "NOT_FOUND"
        assert "abc123" in body["error"]["message"]

    def test_domain_bad_request_error(self):
        test_app = create_app()

        @test_app.get("/test-bad-request")
        def _raise_bad_request():
            raise BadRequestError(message="Invalid input data.")

        tc = TestClient(test_app, raise_server_exceptions=False)
        r = tc.get("/test-bad-request")
        assert r.status_code == 400
        body = r.json()
        assert body["error"]["code"] == "BAD_REQUEST"

    def test_unhandled_exception_returns_500_envelope(self):
        test_app = create_app()

        @test_app.get("/test-crash")
        def _crash():
            raise RuntimeError("something broke")

        tc = TestClient(test_app, raise_server_exceptions=False)
        r = tc.get("/test-crash")
        assert r.status_code == 500
        body = r.json()
        assert body["error"]["code"] == "INTERNAL_ERROR"


# ── 4. Pydantic settings ───────────────────────────────────────────


class TestSettings:
    def test_settings_load(self):
        from app.config import get_settings

        s = get_settings()
        assert s.api_port == 8000
        assert s.app_env in ("local", "test", "staging", "production")

    def test_settings_cached(self):
        from app.config import get_settings

        a = get_settings()
        b = get_settings()
        assert a is b  # same cached instance


# ── 5. Backward compatibility ──────────────────────────────────────


class TestBackwardCompat:
    def test_root_route_still_works(self, client: TestClient):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["service"] == "aegis-api"

    def test_openapi_docs_available(self, client: TestClient):
        r = client.get("/docs")
        assert r.status_code == 200
