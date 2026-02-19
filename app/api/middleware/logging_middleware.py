"""
Logging Middleware
AI Medical Report Analyzer

Logs all HTTP requests with timing, method, path, status, and request ID.
"""

import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Structured request/response logging middleware."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start_time = time.monotonic()

        # Attach request_id for downstream use
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            duration_ms = (time.monotonic() - start_time) * 1000

            log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
            logger.log(
                log_level,
                f"[{request_id}] {request.method} {request.url.path} "
                f"→ {response.status_code} ({duration_ms:.1f}ms) "
                f"client={request.client.host if request.client else 'unknown'}"
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            duration_ms = (time.monotonic() - start_time) * 1000
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} "
                f"→ ERROR ({duration_ms:.1f}ms) {exc}"
            )
            raise
