"""Complaint workflow — uses pre-computed sentiment to avoid duplicate LLM calls."""
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import re
from src.config import settings


@dataclass
class ComplaintCase:
    case_id: str = field(default_factory=lambda: f"CASE-{uuid.uuid4().hex[:8].upper()}")
    customer_text: str = ""
    sentiment_score: float = 0.0
    urgency: str = "medium"
    intent: str = "complaint"
    auto_response: str = ""
    escalated: bool = False
    escalate_reason: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ComplaintWorkflow:
    def __init__(self):
        self.escalate_keywords = settings.escalate_keywords

    async def process(self, text: str, sentiment: dict | None = None) -> ComplaintCase:
        case = ComplaintCase(customer_text=text)

        # 1. Use pre-computed sentiment if available, otherwise compute locally
        if sentiment:
            case.sentiment_score = sentiment.get("sentiment_score", 0.0)
            case.urgency = sentiment.get("urgency", "medium")
            case.intent = sentiment.get("intent", "complaint")
        else:
            from src.sentiment import analyze as sentiment_analyze
            sentiment = sentiment_analyze(text)
            case.sentiment_score = sentiment["sentiment_score"]
            case.urgency = sentiment["urgency"]
            case.intent = sentiment.get("intent", "complaint")

        # 2. Check if immediate escalation is needed (keyword match with word boundary)
        for keyword in self.escalate_keywords:
            if keyword.lower() in text.lower():
                case.escalated = True
                case.escalate_reason = f"检测到高危关键词: {keyword}"
                return case

        # 3. Sentiment score too low also triggers escalation
        if sentiment["sentiment_score"] <= settings.auto_resolve_sentiment_threshold:
            case.escalated = True
            case.escalate_reason = f"情感分数过低 ({sentiment['sentiment_score']})"
            return case

        return case
