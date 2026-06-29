# src/bot_line.py
"""
LINE Bot 整合（選用）
需要 pip install line-bot-sdk
"""
from fastapi import Request
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage, MessageEvent, TextMessage
from src.dispatcher import Dispatcher
from src.config import settings

line_bot_api = LineBotApi(settings.line_channel_access_token)
handler = WebhookHandler(settings.line_channel_secret)
dispatcher = Dispatcher()


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    import asyncio
    result = asyncio.run(dispatcher.handle(text))

    response_text = result.get("response", "已為您轉接人工客服")
    if result.get("case_id"):
        response_text += f"\n\n案件編號: {result['case_id']}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_text)
    )
