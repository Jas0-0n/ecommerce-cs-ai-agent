# tests/test_dispatcher.py
import pytest
from src.dispatcher import Dispatcher


@pytest.mark.asyncio
async def test_dispatch_faq():
    d = Dispatcher()
    result = await d.handle("請問退貨有幾天鑑賞期？")
    assert result["route"] in ("faq", "complaint")
    if result["route"] == "faq":
        assert "response" in result


@pytest.mark.asyncio
async def test_dispatch_complaint():
    d = Dispatcher()
    result = await d.handle("你們的服務真的很爛，我等了五天了")
    assert result["route"] in ("complaint", "agent")


@pytest.mark.asyncio
async def test_dispatch_agent():
    d = Dispatcher()
    result = await d.handle("叫你們主管出來")
    # "找主管" → 應該轉人工
    assert result["route"] == "agent" or (
        result.get("route") == "complaint" and "escalate" in str(result)
    )
