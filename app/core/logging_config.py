"""
Structured Logging Configuration
AI Medical Report Analyzer

Provides JSON-structured logging with request context.
"""

import logging
import sys
from typing import Any, Dict
from datetime import datetime

from app.core.config import settings


def configure_logging() -> None:
    """Configure application-wide logging."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        if settings.log_format != "json"
        else "%(message)s",
        stream=sys.stdout,
    )

    # Quieten noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance."""
    return logging.getLogger(name)


class RequestLogger:
    """Contextual logger for HTTP request tracking."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def log_request(self, method: str, path: str, status: int, duration_ms: float) -> None:
        self.logger.info(
            "HTTP Request",
            extra={
                "method": method,
                "path": path,
                "status": status,
                "duration_ms": round(duration_ms, 2),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def log_ai_call(self, model: str, tokens: int, duration_ms: float, cached: bool) -> None:
        self.logger.info(
            "AI API Call",
            extra={
                "model": model,
                "tokens_used": tokens,
                "duration_ms": round(duration_ms, 2),
                "cached": cached,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
