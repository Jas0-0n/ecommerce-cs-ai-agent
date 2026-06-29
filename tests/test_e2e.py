"""End-to-end tests."""
import pytest
from src.dispatcher import Dispatcher


@pytest.mark.asyncio
class TestE2EFAQ:
    """FAQ core scenarios"""

    async def test_order_status(self):
        d = Dispatcher()
        r = await d.handle("我的订单出货了吗？")
        assert len(r.get("response", "")) > 20

    async def test_return_policy(self):
        d = Dispatcher()
        r = await d.handle("退货需要什么条件？")
        assert len(r.get("response", "")) > 20

    async def test_shipping_time(self):
        d = Dispatcher()
        r = await d.handle("运送大概要几天？")
        assert len(r.get("response", "")) > 20

    async def test_payment_methods(self):
        d = Dispatcher()
        r = await d.handle("可以用支付宝吗？")
        assert len(r.get("response", "")) > 20


@pytest.mark.asyncio
class TestE2EComplaint:
    """Complaint core scenarios"""

    async def test_product_defect(self):
        d = Dispatcher()
        r = await d.handle("收到的东西是坏的，我要退货！")
        assert r["route"] == "complaint"

    async def test_delay_complaint(self):
        d = Dispatcher()
        r = await d.handle("你们送货太慢了，等了一周了")
        assert r["route"] == "complaint"

    async def test_angry_escalate(self):
        d = Dispatcher()
        r = await d.handle("你们这是诈骗！我要报警！")
        assert r["route"] == "complaint"
        assert r.get("type") == "escalate"

    async def test_normal_query_not_complaint(self):
        """Normal inquiry should NOT be routed to complaint."""
        d = Dispatcher()
        r = await d.handle("告诉我怎么退货")
        assert r["route"] == "faq"

    async def test_mild_dissatisfaction_auto_reply(self):
        """Mild dissatisfaction about delivery should NOT escalate."""
        d = Dispatcher()
        r = await d.handle("发货有点慢，等了两三天了")
        # Regardless of faq/complaint routing, should NOT escalate
        assert r.get("type") != "escalate"
