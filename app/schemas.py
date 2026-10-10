"""Pydantic request/response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, HttpUrl


# --- Auth ---

class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- URLs ---

class URLCreate(BaseModel):
    long_url: HttpUrl
    custom_alias: str | None = None
    expires_at: datetime | None = None


class URLResponse(BaseModel):
    short_key: str
    short_url: str
    long_url: str
    created_at: datetime
    expires_at: datetime | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class URLListResponse(BaseModel):
    urls: list[URLResponse]
    total: int


# --- Analytics ---

class ClickDetail(BaseModel):
    clicked_at: datetime
    referrer: str | None
    country: str | None

    model_config = {"from_attributes": True}


class URLStats(BaseModel):
    short_key: str
    long_url: str
    total_clicks: int
    clicks_today: int
    top_referrers: list[dict[str, int]]
    top_countries: list[dict[str, int]]
    recent_clicks: list[ClickDetail]
