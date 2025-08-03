import logging
import os
import threading
import time
import psutil
from flask import Flask
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from truecaller_api import search_number

# ===== Env Variables =====
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 6838940621  # Apna Telegram ID

# ===== Flask App =====
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ SmartxChecker Bot is alive!"

# Flask ko alag thread par run karenge
def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ===== Telegram Bot Commands =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to *SmartxChecker*!\n\n"
        "Send me any phone number with country code (e.g., `+91xxxxxxxxxx`) to get details.",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *Help - SmartxChecker*\n\n"
        "• Send phone number with country code to get info.\n"
        "• Example: `+918888888888`\n\n"
        "/status - Bot system status\n"
        "/about - About this bot",
        parse_mode="Markdown"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *SmartxChecker Bot*\n"
        "Built using *Python + Telegram Bot API + RapidAPI (CallApp)*.\n\n"
        "Created by: [SmartxHacker](https://t.me/smartxhacker)",
        parse_mode="Markdown"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    await update.message.reply_text(
        f"📊 *System Status*\n\n"
        f"CPU: {cpu}%\nRAM: {ram}%\nDisk: {disk}%\n\n"
        "Bot is running smoothly ✅",
        parse_mode="Markdown"
    )

# ===== Handle Phone Numbers =====
async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()

    if not number.startswith("+"):
        await update.message.reply_text("⚠️ Please send number with country code (e.g., `+91xxxxxxxxxx`)", parse_mode="Markdown")
        return

    await update.message.reply_text("⏳ Fetching details... Please wait")

    data = search_number(number)
    if data:
        # Format response
        name = data.get("name", "Unknown")
        carrier = data.get("carrier", "N/A")
        country = data.get("country", "N/A")

        reply_text = (
            f"📞 *Number Info*\n\n"
            f"*Name:* {name}\n"
            f"*Carrier:* {carrier}\n"
            f"*Country:* {country}\n\n"
            "➤ Data by SmartxChecker"
        )

        await update.message.reply_text(reply_text, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No data found for this number.")

# ===== Main Function =====
def main():
    logging.basicConfig(level=logging.INFO)

    # Delete webhook (polling mode ke liye)
    os.system(f"curl -s https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook")

    # Flask thread
    threading.Thread(target=run_flask).start()

    # Telegram Bot
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help message"),
        BotCommand("about", "About this bot"),
        BotCommand("status", "Check system status"),
    ]
    application.bot.set_my_commands(commands)

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))

    # Start polling
    application.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
