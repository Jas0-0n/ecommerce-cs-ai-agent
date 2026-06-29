# src/sentiment.py
import json
from src.llm_client import LLMClient, Message

SENTIMENT_SYSTEM_PROMPT = """You are a sentiment analysis expert for e-commerce customer service conversations.
Analyze the following customer message and output JSON format (no other text):

{
    "sentiment_score": float from -1.0 to 1.0,
    "urgency": "low" | "medium" | "high",
    "intent": "faq" | "complaint" | "refund_request" | "cancel_request" | "other",
    "reason": "Brief analysis reason"
}

Score definitions:
- 1.0 = Very positive (gratitude, satisfaction)
- 0.0 = Neutral
- -0.5 = Dissatisfied (complaining about product/service)
- -1.0 = Extremely angry (complaints, insults, threats)
"""


class SentimentAnalyzer:
    def __init__(self):
        self.llm = LLMClient()

    def analyze(self, text: str) -> dict:
        messages = [
            Message(role="system", content=SENTIMENT_SYSTEM_PROMPT),
            Message(role="user", content=text)
        ]
        resp = self.llm.chat(messages)
        try:
            return json.loads(resp.content)
        except json.JSONDecodeError:
            # fallback
            return {
                "sentiment_score": 0.0,
                "urgency": "medium",
                "intent": "other",
                "reason": "parse failed"
            }
