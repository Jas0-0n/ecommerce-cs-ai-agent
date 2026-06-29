import json
import time
import asyncio
from src.llm_client import LLMClient, Message
from src.sentiment import analyze as sentiment_analyze
from src.agent import FAQAgent, ComplainAgent
from src.monitoring import monitor

DISPATCH_SYSTEM_PROMPT = """你是一个电商客服分流系统。分析用户输入，决定由哪个子系统处理。

返回JSON格式（不要输出其他文字）：
{
    "route": "faq" | "complaint" | "agent",
    "reason": "简要原因",
    "confidence": 0.0-1.0
}

分流原则：
- faq：咨询类问题（订单状态、退货政策、物流时效、支付方式、商品规格、发票、保修）
- complaint：投诉、不满、要求赔偿、要求退款、表达失望/愤怒
- agent：要求转人工客服、法律威胁、涉及多个部门的复杂问题

注意区分：
- "退货要什么条件" → faq（咨询退货政策）
- "收到的东西是坏的，我要退货" → complaint（质量问题投诉）
- "太慢了等了一周" → complaint（服务不满）
- "我要找主管" → complaint（非高危，先尝试自动处理）
"""


class Dispatcher:
    def __init__(self):
        self.llm = LLMClient()
        self.faq_agent = FAQAgent()
        self.complain_agent = ComplainAgent()

    async def route(self, text: str) -> dict:
        # Run LLM routing and sentiment analysis in parallel
        route_task = self._llm_route(text)
        sentiment_task = asyncio.to_thread(sentiment_analyze, text)

        route_info, sentiment = await asyncio.gather(route_task, sentiment_task)

        # Sentiment override: if very negative but not classified as complaint
        if sentiment["sentiment_score"] < -0.6 and route_info["route"] != "complaint":
            route_info["route"] = "complaint"
            route_info["reason"] += "（情感覆盖：检测到强烈负面情绪）"

        # Attach sentiment to route_info for downstream use
        route_info["sentiment"] = sentiment
        return route_info

    async def _llm_route(self, text: str) -> dict:
        messages = [
            Message(role="system", content=DISPATCH_SYSTEM_PROMPT),
            Message(role="user", content=text)
        ]
        resp = self.llm.chat(messages)
        try:
            return json.loads(resp.content)
        except json.JSONDecodeError:
            return {"route": "agent", "reason": "LLM解析失败", "confidence": 0.0}

    async def handle(self, text: str) -> dict:
        start = time.time()
        route_info = await self.route(text)
        route = route_info["route"]

        if route == "faq":
            response = await self.faq_agent.answer(text)
            result = {"route": "faq", "response": response, "route_info": route_info}
        elif route == "complaint":
            result = await self.complain_agent.handle(text, route_info.get("sentiment"))
            result["route"] = "complaint"
            result["route_info"] = route_info
        else:
            result = {
                "route": "agent",
                "response": "正在为您转接人工客服，请稍候……",
                "route_info": route_info
            }

        duration = int((time.time() - start) * 1000)
        monitor.log_interaction(text, result, duration)
        return result

    async def handle_stream(self, text: str):
        """Streaming version of handle — yields response chunks."""
        start = time.time()
        route_info = await self.route(text)
        route = route_info["route"]

        if route == "faq":
            async for chunk in self.faq_agent.answer_stream(text):
                yield chunk
        elif route == "complaint":
            result = await self.complain_agent.handle(text, route_info.get("sentiment"))
            yield result.get("response", "")
            route_info["_complaint_result"] = result
        else:
            yield "正在为您转接人工客服，请稍候……"

        duration = int((time.time() - start) * 1000)
        result = {"route": route, "route_info": route_info}
        if route == "complaint" and "_complaint_result" in route_info:
            result.update(route_info["_complaint_result"])
        monitor.log_interaction(text, result, duration)
