"""
Rule-based sentiment analysis — no LLM call, instant response.
Replaces the previous LLM-based implementation for speed.
"""
import re


# Weighted keyword dictionaries
STRONG_NEGATIVE = {
    "诈骗": -1.0, "骗子": -1.0, "垃圾": -0.8, "坑人": -0.8,
    "报警": -0.9, "起诉": -0.9, "律师": -0.8, "法律途径": -0.8,
    "太差了": -0.7, "很差": -0.6, "很差劲": -0.7,
    "投诉": -0.5, "举报": -0.7, "曝光": -0.8,
    "退款": -0.4, "退货": -0.3, "发错货": -0.4,
    "太慢了": -0.5, "太慢": -0.5, "等了很久": -0.4,
    "坏的": -0.6, "坏了": -0.6, "损坏": -0.6, "破损": -0.6,
    "瑕疵": -0.4, "质量差": -0.6, "质量不好": -0.5,
    "不满意": -0.4, "不高兴": -0.4, "生气": -0.5, "愤怒": -0.7,
    "无语": -0.4, "离谱": -0.5, "过分": -0.5,
    "不想要了": -0.3, "后悔": -0.3,
}

MILD_NEGATIVE = {
    "不好": -0.3, "不太行": -0.3, "有点失望": -0.3,
    "慢": -0.2, "等": -0.1, "问题": -0.1,
    "怎么回事": -0.2, "怎么处理": -0.1, "怎么办": -0.1,
}

POSITIVE = {
    "谢谢": 0.5, "感谢": 0.5, "满意": 0.6, "好评": 0.6,
    "好用": 0.5, "不错": 0.4, "很好": 0.5, "很好用": 0.6,
    "棒": 0.5, "赞": 0.5, "喜欢": 0.4, "方便": 0.3,
    "快速": 0.3, "及时": 0.3, "耐心": 0.4, "专业": 0.4,
}

# Urgency escalation keywords
HIGH_URGENCY_KW = ["报警", "律师", "起诉", "消协", "12315", "曝光", "媒体", "记者", "诈骗"]
MEDIUM_URGENCY_KW = ["投诉", "退款", "退货", "太慢", "坏的", "损坏", "不满意", "生气"]


def _count_score(text: str, keyword_scores: dict) -> tuple[float, list[str]]:
    """Count weighted score from keyword matches, return (score, matched_keywords)."""
    total = 0.0
    matched = []
    for kw, score in keyword_scores.items():
        if kw in text:
            total += score
            matched.append(kw)
    return total, matched


def analyze(text: str) -> dict:
    """Analyze sentiment from text using keyword rules. Returns same format as before."""
    neg_strong, neg_matched = _count_score(text, STRONG_NEGATIVE)
    neg_mild, _ = _count_score(text, MILD_NEGATIVE)
    pos_score, pos_matched = _count_score(text, POSITIVE)

    raw_score = neg_strong + neg_mild + pos_score
    # Clamp to [-1.0, 1.0]
    score = max(-1.0, min(1.0, raw_score))

    # Determine urgency
    if any(kw in text for kw in HIGH_URGENCY_KW):
        urgency = "high"
    elif any(kw in text for kw in MEDIUM_URGENCY_KW):
        urgency = "medium"
    elif score < -0.3:
        urgency = "medium"
    else:
        urgency = "low"

    # Determine intent
    complaint_matched = neg_strong < -0.3 or any(kw in text for kw in MEDIUM_URGENCY_KW + HIGH_URGENCY_KW)
    if complaint_matched:
        intent = "complaint"
    elif pos_score > 0:
        intent = "faq"
    else:
        intent = "faq"  # default to faq

    # Build reason
    all_matched = neg_matched + pos_matched
    if all_matched:
        reason = f"关键词匹配: {', '.join(all_matched[:5])}"
    else:
        reason = "无明显情感关键词"

    return {
        "sentiment_score": round(score, 2),
        "urgency": urgency,
        "intent": intent,
        "reason": reason,
    }
