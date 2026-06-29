# tests/test_agent_faq.py
from src.agent import FAQAgent
import pytest


@pytest.mark.asyncio
async def test_faq_agent_basic_flow():
    agent = FAQAgent()
    result = await agent.answer("如何查詢我的訂單狀態？")
    assert isinstance(result, str)
    assert len(result) > 10  # 有實際回覆
