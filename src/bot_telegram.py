# src/bot_telegram.py
"""
Telegram Bot 整合（選用）
需要 pip install python-telegram-bot
"""
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from src.dispatcher import Dispatcher
from src.config import settings

dispatcher = Dispatcher()


async def handle_message(update: Update, context):
    text = update.message.text
    result = await dispatcher.handle(text)
    response = result.get("response", "已為您轉接人工客服")
    await update.message.reply_text(response)


async def start(update: Update, context):
    await update.message.reply_text("🛒 您好！我是電商客服 AI Agent。請問有什麼可以幫您的嗎？")


def start_telegram():
    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
