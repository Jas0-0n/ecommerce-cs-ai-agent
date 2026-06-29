"""Tests for FAQ Agent."""
import pytest
from src.agent import FAQAgent


class TestFAQAgent:
    @pytest.fixture
    def agent(self):
        return FAQAgent()

    @pytest.mark.asyncio
    async def test_answer_returns_string(self, agent):
        response = await agent.answer("退货要什么条件？")
        assert isinstance(response, str)
        assert len(response) > 20

    @pytest.mark.asyncio
    async def test_answer_mentions_source(self, agent):
        response = await agent.answer("7天无理由退货标准是什么？")
        assert len(response) > 20
