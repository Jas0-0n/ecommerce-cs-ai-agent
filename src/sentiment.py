# src/sentiment.py
import json
from src.llm_client import LLMClient, Message

SENTIMENT_SYSTEM_PROMPT = """你是一個電商客服對話的情緒分析專家。
請分析以下顧客訊息，輸出 JSON 格式（不要其他文字）：

{
    "sentiment_score": -1.0 到 1.0 的浮點數,
    "urgency": "low" | "medium" | "high",
    "intent": "faq" | "complaint" | "refund_request" | "cancel_request" | "other",
    "reason": "簡短分析原因（10字以內）"
}

分數定義：
- 1.0 = 非常正面（感謝、滿意）
- 0.0 = 中性
- -0.5 = 不滿（抱怨產品/服務）
- -1.0 = 極度憤怒（投訴、罵人、威脅）
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
                "reason": "解析失敗"
            }
