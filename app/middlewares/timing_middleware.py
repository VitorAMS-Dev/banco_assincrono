"""Middleware assíncrono que mede o tempo de resposta de cada requisição."""
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging_config import access_logger


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()

        response = await call_next(request)

        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-ms"] = f"{elapsed_ms:.2f}"

        access_logger.info(
            "%s %s %s status=%s tempo=%.2fms",
            request_id, request.method, request.url.path, response.status_code, elapsed_ms,
        )
        return response
