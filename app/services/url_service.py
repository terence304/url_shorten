"""Core URL shortening and resolution service."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import base62
from app.config import settings
from app.models import URL
from app.redis_client import redis


async def create_short_url(
    db: AsyncSession,
    long_url: str,
    user_id: int | None = None,
    custom_alias: str | None = None,
    expires_at: datetime | None = None,
) -> URL:
    """Create a new shortened URL and cache the mapping."""
    url = URL(
        long_url=long_url,
        user_id=user_id,
        custom_alias=custom_alias,
        expires_at=expires_at,
    )
    db.add(url)
    await db.flush()  # populate url.id via auto-increment

    url.short_key = custom_alias or base62.encode(url.id)
    await db.commit()
    await db.refresh(url)

    # Cache in Redis
    await redis.set(f"url:{url.short_key}", url.long_url)
    return url


async def resolve_short_url(db: AsyncSession, short_key: str) -> URL | None:
    """Look up a short key and return the URL row, or None."""
    # Try Redis first
    cached = await redis.get(f"url:{short_key}")
    if cached:
        # Still need the full row for analytics / expiry checks
        pass

    stmt = select(URL).where(
        (URL.short_key == short_key) | (URL.custom_alias == short_key),
        URL.is_active == True,
    )
    result = await db.execute(stmt)
    url = result.scalar_one_or_none()

    if url is None:
        return None

    # Check expiration
    if url.expires_at and url.expires_at < datetime.now(timezone.utc):
        return None

    # Populate cache on DB hit
    if not cached:
        await redis.set(f"url:{short_key}", url.long_url)

    return url


async def list_user_urls(db: AsyncSession, user_id: int) -> list[URL]:
    """Return all URLs owned by a user."""
    stmt = select(URL).where(URL.user_id == user_id, URL.is_active == True).order_by(URL.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def deactivate_url(db: AsyncSession, short_key: str, user_id: int) -> bool:
    """Soft-delete a URL owned by the given user. Returns True if found and deactivated."""
    stmt = select(URL).where(URL.short_key == short_key, URL.user_id == user_id, URL.is_active == True)
    result = await db.execute(stmt)
    url = result.scalar_one_or_none()
    if url is None:
        return False
    url.is_active = False
    await db.commit()
    await redis.delete(f"url:{short_key}")
    return True
