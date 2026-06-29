# tests/test_e2e.py
import pytest
from src.dispatcher import Dispatcher


@pytest.mark.asyncio
class TestE2EFAQ:
    """FAQ 核心場景"""

    async def test_order_status(self):
        d = Dispatcher()
        r = await d.handle("我的訂單出貨了嗎？")
        assert len(r.get("response", "")) > 20

    async def test_return_policy(self):
        d = Dispatcher()
        r = await d.handle("退貨需要什麼條件？")
        assert len(r.get("response", "")) > 20

    async def test_shipping_time(self):
        d = Dispatcher()
        r = await d.handle("運送大概要幾天？")
        assert len(r.get("response", "")) > 20

    async def test_payment_methods(self):
        d = Dispatcher()
        r = await d.handle("可以用 line pay 嗎？")
        assert len(r.get("response", "")) > 20


@pytest.mark.asyncio
class TestE2EComplaint:
    """客訴核心場景"""

    async def test_product_defect(self):
        d = Dispatcher()
        r = await d.handle("收到的東西是壞的，我要退貨！")
        assert r["route"] == "complaint"

    async def test_delay_complaint(self):
        d = Dispatcher()
        r = await d.handle("你們送貨太慢了，等了一個禮拜")
        assert r["route"] == "complaint"

    async def test_angry_escalate(self):
        d = Dispatcher()
        r = await d.handle("你們這是詐騙集團！我要報警！")
        if r["route"] == "complaint":
            assert r.get("type") == "escalate"  # 應該升級
