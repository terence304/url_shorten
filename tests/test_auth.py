"""Tests for auth endpoints."""

import pytest
from httpx import AsyncClient


class TestAuth:
    @pytest.mark.asyncio
    async def test_register(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "secret"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "a@b.com"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "s"})
        resp = await client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "s"})
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "secret"})
        resp = await client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "secret"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "secret"})
        resp = await client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "wrong"})
        assert resp.status_code == 401
