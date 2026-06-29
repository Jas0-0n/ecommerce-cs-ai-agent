# src/dispatcher.py
import json
from src.llm_client import LLMClient, Message
from src.sentiment import SentimentAnalyzer
from src.agent import FAQAgent, ComplainAgent

DISPATCH_SYSTEM_PROMPT = """You are an e-commerce customer service dispatch system.
Analyze the user input and decide which sub-agent should handle it.

Return JSON format:
{
    "route": "faq" | "complaint" | "agent",
    "reason": "Brief reason",
    "confidence": 0.0-1.0
}

Decision principles:
- faq: Inquiry-type questions (order status, return policy, shipping time, payment methods, product specifications)
- complaint: Complaints, grievances, requests for compensation, expressions of dissatisfaction, return requests
- agent: Request to transfer to a human agent, legal threats, complex cross-department issues
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
            route_info = {"route": "agent", "reason": "LLM parse failed", "confidence": 0.0}

        # Also run sentiment analysis for double-check
        sentiment = self.sentiment.analyze(text)
        if sentiment["sentiment_score"] < -0.6 and route_info["route"] != "complaint":
            # Low sentiment but misclassified -> override to complaint
            route_info["route"] = "complaint"
            route_info["reason"] += " (sentiment override)"

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
                "response": "I will transfer you to a human agent, please wait...",
                "route_info": route_info
            }
