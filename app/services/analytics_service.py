"""Analytics service -- click logging and stats aggregation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Click, URL


async def log_click(
    db: AsyncSession,
    url_id: int,
    referrer: str | None = None,
    user_agent: str | None = None,
    ip_address: str | None = None,
    country: str | None = None,
) -> None:
    """Record a single click event."""
    click = Click(
        url_id=url_id,
        referrer=referrer,
        user_agent=user_agent,
        ip_address=ip_address,
        country=country,
    )
    db.add(click)
    await db.commit()


async def get_url_stats(db: AsyncSession, url: URL) -> dict:
    """Aggregate click statistics for a URL."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Total clicks
    total_q = select(func.count()).where(Click.url_id == url.id)
    total = (await db.execute(total_q)).scalar() or 0

    # Clicks today
    today_q = select(func.count()).where(Click.url_id == url.id, Click.clicked_at >= today_start)
    clicks_today = (await db.execute(today_q)).scalar() or 0

    # Top referrers
    ref_q = (
        select(Click.referrer, func.count().label("cnt"))
        .where(Click.url_id == url.id, Click.referrer.is_not(None))
        .group_by(Click.referrer)
        .order_by(func.count().desc())
        .limit(10)
    )
    ref_rows = (await db.execute(ref_q)).all()
    top_referrers = [{r[0]: r[1]} for r in ref_rows]

    # Top countries
    country_q = (
        select(Click.country, func.count().label("cnt"))
        .where(Click.url_id == url.id, Click.country.is_not(None))
        .group_by(Click.country)
        .order_by(func.count().desc())
        .limit(10)
    )
    country_rows = (await db.execute(country_q)).all()
    top_countries = [{r[0]: r[1]} for r in country_rows]

    # Recent clicks
    recent_q = (
        select(Click)
        .where(Click.url_id == url.id)
        .order_by(Click.clicked_at.desc())
        .limit(20)
    )
    recent = (await db.execute(recent_q)).scalars().all()

    return {
        "short_key": url.short_key,
        "long_url": url.long_url,
        "total_clicks": total,
        "clicks_today": clicks_today,
        "top_referrers": top_referrers,
        "top_countries": top_countries,
        "recent_clicks": recent,
    }
