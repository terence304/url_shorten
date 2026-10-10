"""Redirect endpoint -- the core short-URL resolution path."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import analytics_service, url_service

router = APIRouter(tags=["redirect"])


@router.get("/{short_key}")
async def redirect(short_key: str, request: Request, db: AsyncSession = Depends(get_db)):
    url = await url_service.resolve_short_url(db, short_key)
    if url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found or expired")

    # Fire-and-forget click logging so redirect is not delayed
    asyncio.create_task(
        _log_click(url.id, request)
    )

    return RedirectResponse(url=url.long_url, status_code=status.HTTP_302_FOUND)


async def _log_click(url_id: int, request: Request) -> None:
    """Log click in a background task with its own DB session."""
    from app.database import async_session

    async with async_session() as db:
        await analytics_service.log_click(
            db,
            url_id=url_id,
            referrer=request.headers.get("referer"),
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )
