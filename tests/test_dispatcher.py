"""Tests for Dispatcher routing."""
import pytest
from src.dispatcher import Dispatcher


class TestDispatcher:
    @pytest.fixture
    def dispatcher(self):
        return Dispatcher()

    @pytest.mark.asyncio
    async def test_route_faq(self, dispatcher):
        route = await dispatcher.route("退货要什么条件")
        assert route["route"] == "faq"

    @pytest.mark.asyncio
    async def test_route_complaint(self, dispatcher):
        route = await dispatcher.route("东西是坏的，质量太差了！")
        assert route["route"] == "complaint"

    @pytest.mark.asyncio
    async def test_route_agent(self, dispatcher):
        route = await dispatcher.route("我要找你们的法务部门")
        assert route["route"] in ("complaint", "agent")

    @pytest.mark.asyncio
    async def test_handle_faq(self, dispatcher):
        result = await dispatcher.handle("退货要什么条件")
        assert result["route"] == "faq"
        assert len(result["response"]) > 20

    @pytest.mark.asyncio
    async def test_handle_complaint(self, dispatcher):
        result = await dispatcher.handle("东西是坏的，质量太差了！")
        assert result["route"] == "complaint"
