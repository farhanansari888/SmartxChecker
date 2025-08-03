import os
import logging
import threading
import time
import json
from flask import Flask
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from truecaller_api import search_number

# ====== ENV ======
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# ====== Logging ======
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

# ====== Flask Setup ======
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ SmartxChecker is Alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ====== Usage File ======
USAGE_FILE = "usage.json"
if not os.path.exists(USAGE_FILE):
    with open(USAGE_FILE, "w") as f:
        json.dump({"used_requests": 0}, f)

def increment_usage():
    with open(USAGE_FILE, "r") as f:
        data = json.load(f)
    data["used_requests"] += 1
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f)

# ====== Number Formatter ======
def format_number(raw_number: str) -> str:
    raw_number = raw_number.strip().replace(" ", "").replace("-", "")

    if raw_number.startswith("+91"):
        return raw_number.replace("+", "")  # +91 → 91XXXXXXXXXX
    elif raw_number.startswith("91") and len(raw_number) == 12:
        return raw_number
    elif len(raw_number) == 10:
        return "91" + raw_number
    else:
        return None

# ====== Commands ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to SmartxChecker!\n\nSend an Indian phone number (10 digits) to lookup details."
    )

async def quota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(USAGE_FILE, "r") as f:
        data = json.load(f)
    await update.message.reply_text(f"API Calls used: {data['used_requests']}")

# ====== Handle Numbers ======
async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_number = update.message.text
    phone_number = format_number(raw_number)

    if not phone_number:
        await update.message.reply_text("⚠️ Invalid number format. Send valid 10-digit Indian number.")
        return

    logging.info(f"Received: {raw_number} | Formatted: {phone_number}")

    result = search_number(phone_number)

    if "error" in result:
        await update.message.reply_text(f"❌ {result['error']}")
    else:
        increment_usage()
        reply = (
            f"📞 *Number Details*\n\n"
            f"**Name:** {result['name']}\n"
            f"**Carrier:** {result['carrier']}\n"
            f"**Country:** {result['country']}\n"
            f"**Score:** {result['score']}\n"
            f"**Spam:** {'Yes' if result['spam'] else 'No'}"
        )
        await update.message.reply_text(reply, parse_mode="Markdown")

# ====== Main ======
def main():
    # Flask thread
    threading.Thread(target=run_flask).start()

    # Telegram bot
    app_telegram = ApplicationBuilder().token(TOKEN).build()

    # Commands
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("quota", "Check API usage"),
    ]
    app_telegram.bot.set_my_commands(commands)

    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("quota", quota))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))

    logging.info("Bot started polling...")
    app_telegram.run_polling()

if __name__ == "__main__":
    main()
