# tests/test_complaint_agent.py
import pytest
from src.agent import ComplainAgent


@pytest.mark.asyncio
async def test_complaint_routine():
    agent = ComplainAgent()
    result = await agent.handle("我昨天買的衣服尺寸不對，想退貨")
    assert result["type"] in ("auto_reply", "escalate")
    assert "case_id" in result


@pytest.mark.asyncio
async def test_escalate_on_keyword():
    agent = ComplainAgent()
    result = await agent.handle("你們太誇張了，我要找消基會投訴")
    assert result["type"] == "escalate"
    assert "消基會" in result.get("reason", "")


@pytest.mark.asyncio
async def test_complaint_has_case_id():
    agent = ComplainAgent()
    result = await agent.handle("商品有瑕疵")
    assert result["case_id"].startswith("CASE-")
