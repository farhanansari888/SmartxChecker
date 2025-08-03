import logging
import os
import threading
import time
from flask import Flask
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from truecaller_api import lookup_number

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# === Environment Variables ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Check token
if not TELEGRAM_BOT_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN not set! Set environment variable first.")
else:
    logger.info("✅ TELEGRAM_BOT_TOKEN loaded successfully.")

# === Flask App ===
app = Flask(__name__)

@app.route('/')
def home():
    logger.info("Home route accessed.")
    return "✅ Truecaller Bot Running!"

# Flask ko alag thread par chalane ke liye function
def run_flask():
    logger.info("Starting Flask server on port 8080...")
    app.run(host="0.0.0.0", port=8080)

# === Start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/start command used by {update.effective_user.id}")
    welcome_text = (
        "👋 *Welcome to Truecaller Lookup Bot!*\n\n"
        "Send me any phone number with country code (e.g., `+919876543210`) "
        "and I will find the details using Truecaller API."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# === Handle Phone Numbers ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    logger.info(f"Received message: {number} from user {update.effective_user.id}")

    # Basic validation
    if not number.startswith("+") or not number[1:].isdigit():
        logger.warning("Invalid number format received.")
        await update.message.reply_text("⚠️ Please send a valid phone number with `+` and country code.")
        return

    # Fetch details
    await update.message.reply_text("⏳ Fetching details from Truecaller...")
    details = lookup_number(number)
    logger.info(f"API Response for {number}: {details}")
    await update.message.reply_text(details, parse_mode="Markdown")

# === Main Function ===
def main():
    logger.info("Bot starting...")

    # Delete webhook (polling use karne ke liye)
    from requests import get
    try:
        get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook")
        logger.info("Webhook deleted successfully.")
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")

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
    logger.info("Polling started...")
    app_bot.run_polling(close_loop=False)

# === Entry Point ===
if __name__ == "__main__":
    main()
