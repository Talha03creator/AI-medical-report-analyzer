"""
Health & Diagnostics Routes
AI Medical Report Analyzer

Endpoints:
  GET /api/v1/health      System health check
  GET /api/v1/test-llm    Quick LLM connectivity test
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter

from app.database.session import check_database_connection
from app.schemas.report import HealthResponse
from app.core.config import settings
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System health check",
    description="Returns the health status of the database and cache services.",
)
async def health_check():
    """Check database and cache connectivity."""
    db_ok = await check_database_connection()

    # Cache check (Redis or in-memory fallback)
    cache_status = "disabled"
    if settings.redis_enabled:
        try:
            from app.services.cache_service import cache_service
            cache_ok = await cache_service.health_check()
            cache_status = "healthy" if cache_ok else "unhealthy"
        except Exception:
            cache_status = "unhealthy"
    else:
        cache_status = "in-memory"

    overall = "healthy" if db_ok else "degraded"

    return HealthResponse(
        status=overall,
        version=settings.app_version,
        database="healthy" if db_ok else "unhealthy",
        cache=cache_status,
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/test-llm",
    summary="Test LLM connectivity",
    description=(
        "Sends a simple 'Hello' message to Gemini and returns the response. "
        "Use this to verify that the AI API key and model are correctly configured."
    ),
    responses={
        200: {"description": "LLM responded successfully"},
        503: {"description": "LLM unavailable or misconfigured"},
    },
)
async def test_llm():
    """
    Lightweight Gemini connectivity test.
    Returns status='ok' if the API key and model are working.
    Returns status='error' with detail if configuration is broken.
    """
    logger.info("LLM connectivity test requested")
    result = await ai_service.test_connection()

    if result.get("status") == "ok":
        return {
            "status": "ok",
            "model": result.get("model"),
            "response": result.get("response"),
            "disclaimer": settings.disclaimer,
        }

    # Return 503 on failure so load balancers / monitoring picks it up
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=503,
        content={
            "status": "error",
            "error": result.get("error", "Unknown error"),
            "hint": "Check MEDICAL_AI_API_KEY in your .env file and verify the model name.",
            "disclaimer": settings.disclaimer,
        },
    )
