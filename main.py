import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from truecaller_api import search_number
from flask import Flask

# Setup logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO
)

# Telegram Bot Token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Flask app for Render keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def format_number(phone: str) -> str:
    """Extract last 10 digits (strip +91 if present)"""
    digits = ''.join(filter(str.isdigit, phone))
    return digits[-10:]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a phone number to lookup (e.g., 9460335865)")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.text.strip()
    formatted = format_number(phone_number)
    logging.info(f"User input: {phone_number} -> Formatted: {formatted}")

    result = search_number(formatted)
    logging.info(f"API Response for {formatted}: {result}")

    if "error" in result:
        await update.message.reply_text(f"❌ {result['error']}")
    else:
        response = (
            f"📞 Name: {result['name']}\n"
            f"📡 Carrier: {result['carrier']}\n"
            f"🌍 Country: {result['country']}\n"
            f"⭐ Score: {result['score']}\n"
            f"🚨 Spam: {'Yes' if result['spam'] else 'No'}"
        )
        await update.message.reply_text(response)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    from threading import Thread
    Thread(target=main).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
