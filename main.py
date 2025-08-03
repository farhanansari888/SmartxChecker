import logging
import os
import threading
import time
from flask import Flask
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from truecaller_api import lookup_number

# === Environment Variables ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# === Flask App ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Truecaller Bot Running!"

# Flask ko alag thread par chalane ke liye function
def run_flask():
    app.run(host="0.0.0.0", port=8080)

# === Start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 *Welcome to Truecaller Lookup Bot!*\n\n"
        "Send me any phone number with country code (e.g., `+919876543210`) "
        "and I will find the details using Truecaller API."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# === Handle Phone Numbers ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()

    # Basic validation
    if not number.startswith("+") or not number[1:].isdigit():
        await update.message.reply_text("⚠️ Please send a valid phone number with `+` and country code.")
        return

    # Fetch details
    await update.message.reply_text("⏳ Fetching details from Truecaller...")
    details = lookup_number(number)
    await update.message.reply_text(details, parse_mode="Markdown")

# === Main Function ===
def main():
    logging.basicConfig(level=logging.INFO)

    # Delete webhook (polling use karne ke liye)
    from requests import get
    get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook")

    # Flask thread start
    threading.Thread(target=run_flask).start()

    # Telegram bot build
    app_bot = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands set
    commands = [
        BotCommand("start", "Start the bot"),
    ]
    app_bot.bot.set_my_commands(commands)

    # Handlers
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Polling run
    app_bot.run_polling(close_loop=False)

# === Entry Point ===
if __name__ == "__main__":
    main()
