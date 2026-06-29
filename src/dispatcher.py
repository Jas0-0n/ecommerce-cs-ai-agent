# src/dispatcher.py
import json
from src.llm_client import LLMClient, Message
from src.sentiment import SentimentAnalyzer
from src.agent import FAQAgent, ComplainAgent

DISPATCH_SYSTEM_PROMPT = """你是一個電商客服分流系統。
請分析用戶輸入，決定由哪個子 Agent 處理。

回傳 JSON 格式：
{
    "route": "faq" | "complaint" | "agent",
    "reason": "簡短理由",
    "confidence": 0.0-1.0
}

判斷原則：
- faq: 查詢型問題（訂單狀態、退貨政策、運送時間、付款方式、產品規格）
- complaint: 抱怨、投訴、要求補償、表達不滿情緒、退貨要求
- agent: 要求轉接真人、法律威脅、複雜跨部門問題
"""


class Dispatcher:
    def __init__(self):
        self.llm = LLMClient()
        self.faq_agent = FAQAgent()
        self.complain_agent = ComplainAgent()
        self.sentiment = SentimentAnalyzer()

    async def route(self, text: str) -> dict:
        messages = [
            Message(role="system", content=DISPATCH_SYSTEM_PROMPT),
            Message(role="user", content=text)
        ]
        resp = self.llm.chat(messages)
        try:
            route_info = json.loads(resp.content)
        except json.JSONDecodeError:
            route_info = {"route": "agent", "reason": "LLM 解析失敗", "confidence": 0.0}

        # 也跑情緒分析做雙重檢查
        sentiment = self.sentiment.analyze(text)
        if sentiment["sentiment_score"] < -0.6 and route_info["route"] != "complaint":
            # 情緒低落但被分類錯 → 覆寫為 complaint
            route_info["route"] = "complaint"
            route_info["reason"] += "（情緒分析覆寫）"

        return route_info

    async def handle(self, text: str) -> dict:
        route_info = await self.route(text)
        route = route_info["route"]

        if route == "faq":
            response = await self.faq_agent.answer(text)
            return {"route": "faq", "response": response, "route_info": route_info}
        elif route == "complaint":
            result = await self.complain_agent.handle(text)
            return {"route": "complaint", **result, "route_info": route_info}
        else:
            return {
                "route": "agent",
                "response": "我將為您轉接人工客服專員，請稍候...",
                "route_info": route_info
            }
