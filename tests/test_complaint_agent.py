# tests/test_complaint_agent.py
import pytest
from src.agent import ComplainAgent


@pytest.mark.asyncio
async def test_complaint_routine():
    agent = ComplainAgent()
    result = await agent.handle("I bought a shirt yesterday and the size is wrong, I want to return it")
    assert result["type"] in ("auto_reply", "escalate")
    assert "case_id" in result


@pytest.mark.asyncio
async def test_escalate_on_keyword():
    agent = ComplainAgent()
    result = await agent.handle("I want to file a complaint with the complaint bureau, this is outrageous!")
    assert result["type"] == "escalate"
    assert "complaint bureau" in result.get("reason", "")


@pytest.mark.asyncio
async def test_complaint_has_case_id():
    agent = ComplainAgent()
    result = await agent.handle("This product is defective")
    assert result["case_id"].startswith("CASE-")
