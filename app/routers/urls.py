"""URL CRUD endpoints -- shorten, list, delete."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps import get_current_user_id, get_optional_user_id
from app.schemas import URLCreate, URLListResponse, URLResponse
from app.services import url_service

router = APIRouter(prefix="/api/v1", tags=["urls"])


def _url_to_response(url) -> URLResponse:
    return URLResponse(
        short_key=url.short_key,
        short_url=f"{settings.base_url}/{url.short_key}",
        long_url=url.long_url,
        created_at=url.created_at,
        expires_at=url.expires_at,
        is_active=url.is_active,
    )


@router.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(
    body: URLCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int | None = Depends(get_optional_user_id),
):
    url = await url_service.create_short_url(
        db,
        long_url=str(body.long_url),
        user_id=user_id,
        custom_alias=body.custom_alias,
        expires_at=body.expires_at,
    )
    return _url_to_response(url)


@router.get("/urls", response_model=URLListResponse)
async def list_urls(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    urls = await url_service.list_user_urls(db, user_id)
    return URLListResponse(
        urls=[_url_to_response(u) for u in urls],
        total=len(urls),
    )


@router.delete("/urls/{short_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_url(
    short_key: str,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    ok = await url_service.deactivate_url(db, short_key, user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
