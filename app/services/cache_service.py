"""
Redis Cache Service
AI Medical Report Analyzer
"""

import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class CacheService:
    """Redis cache wrapper with graceful fallback."""
    
    _client = None

    @classmethod
    async def _get_client(cls):
        if cls._client is None:
            try:
                import redis.asyncio as aioredis
                from app.core.config import settings
                cls._client = aioredis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
            except Exception as e:
                logger.warning(f"Redis client init failed: {e}")
                return None
        return cls._client

    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        try:
            client = await cls._get_client()
            if not client:
                return None
            value = await client.get(f"medical:{key}")
            return json.loads(value) if value else None
        except Exception as e:
            logger.warning(f"Cache GET failed for {key}: {e}")
            return None

    @classmethod
    async def set(cls, key: str, value: Any, ttl: int = 3600) -> bool:
        try:
            client = await cls._get_client()
            if not client:
                return False
            await client.setex(f"medical:{key}", ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.warning(f"Cache SET failed for {key}: {e}")
            return False

    @classmethod
    async def health_check(cls) -> bool:
        try:
            client = await cls._get_client()
            if not client:
                return False
            await client.ping()
            return True
        except Exception:
            return False
