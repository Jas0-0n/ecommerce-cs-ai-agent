# src/complaint_workflow.py
from dataclasses import dataclass, field
from datetime import datetime
import uuid


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
        from src.sentiment import SentimentAnalyzer
        self.analyzer = SentimentAnalyzer()
        from src.config import settings
        self.escalate_keywords = settings.escalate_keywords

    async def process(self, text: str) -> ComplaintCase:
        case = ComplaintCase(customer_text=text)

        # 1. 情緒分析
        sentiment = self.analyzer.analyze(text)
        case.sentiment_score = sentiment["sentiment_score"]
        case.urgency = sentiment["urgency"]
        case.intent = sentiment.get("intent", "complaint")

        # 2. 檢查是否需立即升級（關鍵字比對）
        for keyword in self.escalate_keywords:
            if keyword in text:
                case.escalated = True
                case.escalate_reason = f"偵測到高風險關鍵字: {keyword}"
                return case

        # 3. 情緒分數過低也升級
        from src.config import settings
        if sentiment["sentiment_score"] <= settings.auto_resolve_sentiment_threshold:
            case.escalated = True
            case.escalate_reason = f"情緒分數過低 ({sentiment['sentiment_score']})"
            return case

        return case
