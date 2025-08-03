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

# ==== Import Truecaller API function ====
from truecaller_api import get_truecaller_data

# ==== Environment Variables ====
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# ==== Config ====
USAGE_FILE = "usage.json"
ADMIN_ID = 6838940621  # Apna Telegram ID daalna

# ==== Usage Helpers ====
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

# ==== Flask Keep Alive ====
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ SmartxChecker Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ==== Commands ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "✨ *Welcome to SmartxChecker Bot!*\n\n"
        "Send any phone number with country code (e.g., `+919876543210`) "
        "and I will fetch details using Truecaller API.\n\n"
        "Commands:\n/start - Start bot\n/help - Help info\n/status - Bot status\n/quota - API usage\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *How to use:*\nJust send a phone number with country code.\n\nExample:\n`+919876543210`",
        parse_mode="Markdown"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    await update.message.reply_text(
        f"📊 *Bot Status:*\nCPU: {cpu}%\nRAM: {ram}%\nDisk: {disk}%",
        parse_mode="Markdown"
    )

async def quota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_limit = 6  # free plan limit
    usage = load_usage()
    used = usage["used_requests"]
    remaining = total_limit - used
    percent = math.floor((used / total_limit) * 100)
    await update.message.reply_text(
        f"📊 *API Usage:*\nUsed: {used}\nRemaining: {remaining}\n({percent}% used)",
        parse_mode="Markdown"
    )

# ==== Handle phone number messages ====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()

    if not number.startswith("+") or not number[1:].isdigit():
        await update.message.reply_text("⚠️ Please send a valid phone number with country code.\nExample: `+919876543210`", parse_mode="Markdown")
        return

    msg = await update.message.reply_text("⏳ Fetching details, please wait...")

    try:
        data = get_truecaller_data(number)
        if data:
            increment_usage()

            # Format output
            name = data.get("name", "N/A")
            carrier = data.get("carrier", "N/A")
            city = data.get("city", "N/A")
            score = data.get("score", "N/A")

            result = (
                f"🔍 *Truecaller Data:*\n"
                f"• Name: `{name}`\n"
                f"• Carrier: `{carrier}`\n"
                f"• City: `{city}`\n"
                f"• Spam Score: `{score}`"
            )
            await update.message.reply_text(result, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No data found for this number.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

    finally:
        await msg.delete()

# ==== Main ====
def main():
    logging.basicConfig(level=logging.INFO)

    # Flask ko thread me run karna
    threading.Thread(target=run_flask).start()

    # Telegram Polling
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "How to use"),
        BotCommand("status", "Check bot status"),
        BotCommand("quota", "Check API usage")
    ]
    application.bot.set_my_commands(commands)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("quota", quota))

    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run bot
    application.run_polling()

if __name__ == "__main__":
    main()
