"""Tests for analytics endpoints."""

import pytest
from httpx import AsyncClient


async def _setup_url_with_token(client: AsyncClient) -> tuple[str, str]:
    """Register, login, create a URL, return (short_key, token)."""
    await client.post("/api/v1/auth/register", json={"email": "stats@t.com", "password": "pw"})
    login = await client.post("/api/v1/auth/login", json={"email": "stats@t.com", "password": "pw"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    create = await client.post("/api/v1/shorten", json={"long_url": "https://example.com"}, headers=headers)
    return create.json()["short_key"], token


class TestAnalytics:
    @pytest.mark.asyncio
    async def test_stats_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/urls/abc/stats")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_stats_returns_data(self, client: AsyncClient):
        short_key, token = await _setup_url_with_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.get(f"/api/v1/urls/{short_key}/stats", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["short_key"] == short_key
        assert data["total_clicks"] == 0
