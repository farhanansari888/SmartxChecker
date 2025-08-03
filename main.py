import logging
import os
import json
import math
import threading
import time
import psutil
from flask import Flask
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from truecaller_api import get_number_details

# === Config ===
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
USAGE_FILE = "usage.json"
ADMIN_ID = 6838940621  # apna ID daalna

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# === Flask App (Alive Check) ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ SmartxChecker Bot is alive!"

# === Usage Helpers ===
def load_usage():
    if not os.path.exists(USAGE_FILE):
        return {"used_requests": 0}
    with open(USAGE_FILE, "r") as f:
        return json.load(f)

def save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f)

def increment_usage():
    usage = load_usage()
    usage["used_requests"] += 1
    save_usage(usage)

# === Commands ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to *SmartxChecker Bot!*\n\n"
        "Send me any phone number to fetch details using Truecaller API.",
        parse_mode="Markdown"
    )

async def quota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_limit = 100
    usage = load_usage()
    used_calls = usage["used_requests"]
    remaining_calls = total_limit - used_calls
    percentage = math.floor((used_calls / total_limit) * 100)

    await update.message.reply_text(
        f"📊 *API Quota:*\n\n"
        f"Total: {total_limit}\nUsed: {used_calls}\nRemaining: {remaining_calls}\nUsage: {percentage}%",
        parse_mode="Markdown"
    )

async def set_quota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: `/setquota <number>`", parse_mode="Markdown")
        return

    new_value = int(context.args[0])
    save_usage({"used_requests": new_value})
    await update.message.reply_text(f"✅ Quota set to {new_value}")

# === Handle Number Messages ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()

    # Basic validation
    if not number.isdigit():
        await update.message.reply_text("❌ Please send only digits of the phone number.")
        return

    await update.message.reply_text(f"⏳ Fetching details for `{number}` ...", parse_mode="Markdown")

    result = get_number_details(number)

    # Agar result mila to usage increment karo
    if "No data" not in result and "Error" not in result:
        increment_usage()

    await update.message.reply_text(result, parse_mode="Markdown")

# === Flask Run ===
def run_flask():
    app.run(host="0.0.0.0", port=10000)

# === Main ===
def main():
    # Webhook delete (polling mode)
    import requests
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook")

    # Flask thread
    threading.Thread(target=run_flask).start()

    # Telegram bot
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands set
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("quota", "Check API quota"),
        BotCommand("setquota", "Set API quota (admin only)"),
    ]
    application.bot.set_my_commands(commands)

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quota", quota))
    application.add_handler(CommandHandler("setquota", set_quota))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Polling start
    application.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
