"""Tests for FastAPI endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from src.api import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_chat_faq(client):
    resp = await client.post("/chat", json={"message": "退货要什么条件"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["route"] == "faq"
    assert len(data["response"]) > 20
    assert data["session_id"] is not None


@pytest.mark.asyncio
async def test_chat_complaint(client):
    resp = await client.post("/chat", json={"message": "东西是坏的，质量太差了！"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["route"] == "complaint"
