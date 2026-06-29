"""
Telegram Bot integration (optional).
Usage: python -c "from src.bot_telegram import start_telegram; start_telegram()"
"""
from src.dispatcher import Dispatcher
from src.config import settings


def start_telegram():
    """Start Telegram bot — only call when telegram dependencies are installed."""
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters

    dispatcher = Dispatcher()

    async def handle_message(update: Update, context):
        text = update.message.text
        result = await dispatcher.handle(text)
        response = result.get("response", "已为您转接人工客服")
        if result.get("case_id"):
            response += f"\n\n工单编号: {result['case_id']}"
        await update.message.reply_text(response)

    async def start(update: Update, context):
        await update.message.reply_text("🛒 您好！我是电商客服AI助手，请问有什么可以帮您的吗？")

    app = Application.builder().token(settings.telegram_bot_token or "").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
