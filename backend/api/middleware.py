"""Request timing + metrics middleware."""
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.db.engine import _session_factory
from backend.services.metrics.collector import MetricsCollector

_collector = MetricsCollector()

# Endpoints that don't need metric tracking
_SKIP_PATHS = {"/health", "/metrics", "/docs", "/openapi.json", "/redoc"}


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = (time.perf_counter() - start) * 1000

        # Extract repo id from path or body (best-effort)
        repo_id = _extract_repo_id(request)

        try:
            async with _session_factory() as session:
                await _collector.record_request(
                    session,
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    latency_ms=latency_ms,
                    repository_id=repo_id,
                )
        except Exception:
            pass  # never let metrics recording crash the response

        response.headers["X-Response-Time-Ms"] = f"{latency_ms:.1f}"
        return response


def _extract_repo_id(request: Request) -> uuid.UUID | None:
    path_parts = request.url.path.strip("/").split("/")
    for part in path_parts:
        try:
            return uuid.UUID(part)
        except ValueError:
            continue
    return None
