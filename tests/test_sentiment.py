"""Tests for the rule-based sentiment analyzer."""
import pytest
from src.sentiment import analyze


class TestSentimentPositive:
    def test_thank_you(self):
        r = analyze("谢谢你帮我解决了问题")
        assert r["sentiment_score"] > 0
        assert r["urgency"] == "low"

    def test_satisfied(self):
        r = analyze("服务很满意，好评")
        assert r["sentiment_score"] > 0
        assert r["intent"] == "faq"


class TestSentimentNegative:
    def test_complaint(self):
        r = analyze("东西是坏的，质量太差了")
        assert r["sentiment_score"] < -0.3
        assert r["intent"] == "complaint"

    def test_angry(self):
        r = analyze("你们是诈骗！我要报警！")
        assert r["sentiment_score"] < -0.5
        assert r["urgency"] == "high"

    def test_mild_dissatisfaction(self):
        r = analyze("等了好久太慢了")
        assert r["sentiment_score"] < 0
        assert r["urgency"] in ("medium", "high")


class TestSentimentNeutral:
    def test_general_inquiry(self):
        r = analyze("我要查一下订单状态")
        assert -0.3 <= r["sentiment_score"] <= 0.3
        assert r["urgency"] == "low"

    def test_order_status(self):
        r = analyze("我的订单出货了吗")
        assert r["urgency"] == "low"
