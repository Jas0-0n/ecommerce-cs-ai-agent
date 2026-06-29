"""Tests for Complaint Agent."""
import pytest
from src.agent import ComplainAgent


class TestComplainAgent:
    @pytest.fixture
    def agent(self):
        return ComplainAgent()

    @pytest.mark.asyncio
    async def test_normal_complaint(self, agent):
        """Mild complaint should get auto-reply, not escalate."""
        result = await agent.handle("发货太慢了，等了3天")
        assert result.get("case_id") is not None

    @pytest.mark.asyncio
    async def test_escalate_on_high_risk_keyword(self, agent):
        """High-risk keywords should trigger escalation."""
        result = await agent.handle("你们是骗子！我要报警！")
        assert result.get("type") == "escalate"

    @pytest.mark.asyncio
    async def test_pass_sentiment(self, agent):
        """Should accept pre-computed sentiment to avoid duplicate analysis."""
        sentiment = {"sentiment_score": -0.4, "urgency": "medium", "intent": "complaint"}
        result = await agent.handle("发货太慢了", sentiment=sentiment)
        assert result.get("case_id") is not None
