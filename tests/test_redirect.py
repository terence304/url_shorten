"""Tests for the redirect endpoint."""

import pytest
from httpx import AsyncClient


class TestRedirect:
    @pytest.mark.asyncio
    async def test_redirect_success(self, client: AsyncClient):
        create = await client.post("/api/v1/shorten", json={"long_url": "https://example.com"})
        short_key = create.json()["short_key"]
        resp = await client.get(f"/{short_key}", follow_redirects=False)
        assert resp.status_code == 302
        assert "example.com" in resp.headers["location"]

    @pytest.mark.asyncio
    async def test_redirect_not_found(self, client: AsyncClient):
        resp = await client.get("/nonexistent")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_redirect_custom_alias(self, client: AsyncClient):
        await client.post(
            "/api/v1/shorten",
            json={"long_url": "https://example.com/custom", "custom_alias": "go"},
        )
        resp = await client.get("/go", follow_redirects=False)
        assert resp.status_code == 302
        assert "example.com/custom" in resp.headers["location"]
