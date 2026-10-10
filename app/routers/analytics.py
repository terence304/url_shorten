"""Analytics endpoints -- click stats per URL."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user_id
from app.schemas import URLStats
from app.services import analytics_service, url_service

router = APIRouter(prefix="/api/v1", tags=["analytics"])


@router.get("/urls/{short_key}/stats", response_model=URLStats)
async def get_stats(
    short_key: str,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    url = await url_service.resolve_short_url(db, short_key)
    if url is None or url.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
    stats = await analytics_service.get_url_stats(db, url)
    return URLStats(**stats)
