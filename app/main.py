"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine
from app.models import Base
from app.redis_client import redis
from app.routers import analytics, auth, redirect, urls

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hook."""
    await redis.initialize()
    yield
    await redis.close()
    await engine.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(auth.router)
app.include_router(urls.router)
app.include_router(analytics.router)
# Redirect router last -- it has a catch-all /{short_key} path
app.include_router(redirect.router)


@app.get("/")
async def root():
    """Serve the URL shortener UI."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}
