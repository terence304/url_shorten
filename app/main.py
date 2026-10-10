"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import engine
from app.models import Base
from app.redis_client import redis
from app.routers import analytics, auth, redirect, urls


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hook."""
    await redis.initialize()
    yield
    await redis.close()
    await engine.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(auth.router)
app.include_router(urls.router)
app.include_router(analytics.router)
# Redirect router last -- it has a catch-all /{short_key} path
app.include_router(redirect.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
