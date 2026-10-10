"""Tests for URL shortening endpoints."""

import pytest
from httpx import AsyncClient


async def _get_token(client: AsyncClient) -> str:
    await client.post("/api/v1/auth/register", json={"email": "u@t.com", "password": "pw"})
    resp = await client.post("/api/v1/auth/login", json={"email": "u@t.com", "password": "pw"})
    return resp.json()["access_token"]


class TestShorten:
    @pytest.mark.asyncio
    async def test_shorten_anonymous(self, client: AsyncClient):
        resp = await client.post("/api/v1/shorten", json={"long_url": "https://example.com"})
        assert resp.status_code == 201
        data = resp.json()
        assert "short_key" in data
        assert data["long_url"] == "https://example.com/"
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_shorten_authenticated(self, client: AsyncClient):
        token = await _get_token(client)
        resp = await client.post(
            "/api/v1/shorten",
            json={"long_url": "https://example.com/page"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_shorten_custom_alias(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/shorten",
            json={"long_url": "https://example.com", "custom_alias": "mylink"},
        )
        assert resp.status_code == 201
        assert resp.json()["short_key"] == "mylink"


class TestListAndDelete:
    @pytest.mark.asyncio
    async def test_list_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/urls")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_list_urls(self, client: AsyncClient):
        token = await _get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        await client.post("/api/v1/shorten", json={"long_url": "https://a.com"}, headers=headers)
        await client.post("/api/v1/shorten", json={"long_url": "https://b.com"}, headers=headers)
        resp = await client.get("/api/v1/urls", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

    @pytest.mark.asyncio
    async def test_delete_url(self, client: AsyncClient):
        token = await _get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        create_resp = await client.post("/api/v1/shorten", json={"long_url": "https://c.com"}, headers=headers)
        short_key = create_resp.json()["short_key"]
        del_resp = await client.delete(f"/api/v1/urls/{short_key}", headers=headers)
        assert del_resp.status_code == 204
