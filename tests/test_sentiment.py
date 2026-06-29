# tests/test_sentiment.py
def test_sentiment_output_format():
    """測試輸出結構是否正確（mock 模式）"""
    from src.sentiment import SentimentAnalyzer
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("你們的商品品質很差，我要退貨！")
    assert "sentiment_score" in result
    assert "urgency" in result
    assert "intent" in result
    assert isinstance(result["sentiment_score"], float)
    assert result["urgency"] in ("low", "medium", "high")
