"""
Rate Limiting Middleware
AI Medical Report Analyzer

Implements sliding window rate limiting per IP address.
"""

import time
import logging
from collections import defaultdict, deque
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiter.
    Default: 5 requests per 60 seconds per IP.
    """

    def __init__(self, app, max_requests: int = None, window_seconds: int = None):
        super().__init__(app)
        self.max_requests = max_requests or settings.rate_limit_requests
        self.window_seconds = window_seconds or settings.rate_limit_window
        self._windows: dict = defaultdict(deque)
        logger.info(
            f"Rate limiter: {self.max_requests} req/{self.window_seconds}s per IP"
        )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP, respecting proxy headers."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        # Only rate-limit upload/analysis endpoints
        if not request.url.path.startswith("/api/v1/reports"):
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        now = time.time()
        window = self._windows[client_ip]

        # Remove timestamps outside the window
        while window and window[0] < now - self.window_seconds:
            window.popleft()

        if len(window) >= self.max_requests:
            remaining_wait = int(window[0] + self.window_seconds - now + 1)
            logger.warning(f"Rate limit exceeded for IP {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {self.max_requests} requests per {self.window_seconds} seconds.",
                    "retry_after_seconds": remaining_wait,
                    "disclaimer": settings.disclaimer,
                },
                headers={"Retry-After": str(remaining_wait)},
            )

        window.append(now)

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(self.max_requests - len(window))
        response.headers["X-RateLimit-Window"] = str(self.window_seconds)
        return response
