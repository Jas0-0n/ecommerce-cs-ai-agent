# tests/test_api.py
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_chat_faq():
    resp = client.post("/chat", json={"message": "怎麼退貨？"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["route"] in ("faq", "complaint")
    assert len(data["response"]) > 0


def test_chat_complaint():
    resp = client.post("/chat", json={"message": "商品品質很差，我要客訴"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["route"] in ("complaint", "faq", "agent")
