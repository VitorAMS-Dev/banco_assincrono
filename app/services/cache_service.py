"""Wrapper assíncrono para Redis (cache de saldo/extrato)."""
import json
from typing import Any

import redis.asyncio as redis

from app.core.config import settings

_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


class CacheService:
    """Serviço de cache assíncrono. Falhas no Redis nunca derrubam a aplicação
    (cache é um otimização, não uma dependência crítica)."""

    def __init__(self):
        self.client = get_redis_client()

    async def get(self, key: str) -> Any | None:
        try:
            value = await self.client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: int = settings.CACHE_TTL_SECONDS) -> None:
        try:
            await self.client.set(key, json.dumps(value, default=str), ex=ttl)
        except Exception:
            pass

    async def delete(self, key: str) -> None:
        try:
            await self.client.delete(key)
        except Exception:
            pass
