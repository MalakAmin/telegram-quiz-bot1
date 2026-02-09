# أبسط بوت لـ Render
import os
from telegram.ext import Application, CommandHandler

TOKEN = os.environ.get('TELEGRAM_TOKEN')

async def start(update, context):
    await update.message.reply_text("مرحباً! البوت يعمل 24/7 🚀")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
