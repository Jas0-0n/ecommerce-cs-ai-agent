"""
LINE Bot integration (optional).
Fixed: replaced asyncio.run() with proper async handling.
"""
from src.dispatcher import Dispatcher
from src.config import settings


def create_line_app():
    """Create LINE Bot app — only call when LINE dependencies are installed."""
    from fastapi import FastAPI, Request
    from linebot import LineBotApi, WebhookHandler
    from linebot.models import TextSendMessage, MessageEvent, TextMessage
    import asyncio

    line_bot_api = LineBotApi(settings.line_channel_access_token or "")
    handler = WebhookHandler(settings.line_channel_secret or "")
    dispatcher = Dispatcher()

    line_app = FastAPI()

    @line_app.post("/webhook")
    async def webhook(request: Request):
        body = await request.body()
        signature = request.headers.get("X-Line-Signature", "")

        # Process in background to avoid blocking the webhook response
        body_text = body.decode("utf-8")

        # Use asyncio.create_task instead of asyncio.run
        loop = asyncio.get_event_loop()

        def handle_events():
            handler.handle(body_text, signature)

        await loop.run_in_executor(None, handle_events)
        return {"status": "ok"}

    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(event):
        text = event.message.text
        # Run async dispatcher in a new event loop (safe in sync callback)
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(dispatcher.handle(text))
        finally:
            loop.close()

        response_text = result.get("response", "已为您转接人工客服")
        if result.get("case_id"):
            response_text += f"\n\n工单编号: {result['case_id']}"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_text)
        )

    return line_app
