"""Redis async client wrapper."""

from __future__ import annotations

import redis.asyncio as aioredis

from app.config import settings


class RedisClient:
    """Thin wrapper around an async Redis connection."""

    def __init__(self) -> None:
        self._redis: aioredis.Redis | None = None

    async def initialize(self) -> None:
        self._redis = aioredis.from_url(
            settings.redis_url, decode_responses=True
        )

    async def close(self) -> None:
        if self._redis:
            await self._redis.aclose()

    async def get(self, key: str) -> str | None:
        if self._redis is None:
            return None
        return await self._redis.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        if self._redis is None:
            return
        await self._redis.set(key, value, ex=ttl or settings.redis_cache_ttl)

    async def delete(self, key: str) -> None:
        if self._redis is None:
            return
        await self._redis.delete(key)


redis = RedisClient()
