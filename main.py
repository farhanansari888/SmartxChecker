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
from truecaller_api import get_truecaller_data

# === Config ===
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
USAGE_FILE = "usage.json"
ADMIN_ID = 6838940621  # Apna Telegram ID

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
    logger.info("Health check hit on /")
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
    msg = (
        "✨ 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐒𝐦𝐚𝐫𝐭𝐱𝐂𝐡𝐞𝐜𝐤𝐞𝐫 𝐁𝐨𝐭 ✨\n\n"
        "🚀 𝐂𝐡𝐞𝐜𝐤 𝐃𝐞𝐭𝐚𝐢𝐥𝐬 𝐎𝐟 𝐀𝐧𝐲 𝐍𝐮𝐦𝐛𝐞𝐫 𝐈𝐧𝐬𝐭𝐚𝐧𝐭𝐥𝐲!\n\n"
        "──────────────\n"
        "• 𝐀𝐜𝐜𝐮𝐫𝐚𝐭𝐞 𝐃𝐚𝐭𝐚 ⚡\n"
        "• 𝐅𝐚𝐬𝐭 & 𝐑𝐞𝐥𝐢𝐚𝐛𝐥𝐞 🖤\n"
        "• 𝐒𝐢𝐦𝐩𝐥𝐞 𝐓𝐨 𝐔𝐬𝐞 🎯\n"
        "──────────────\n\n"
        "➤ 𝐁𝐨𝐭 𝐁𝐲: [𝐒𝐦𝐚𝐫𝐭𝐱𝐇𝐚𝐜𝐤𝐞𝐫](https://t.me/smartxhacker)"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def quota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usage = load_usage()
    total_limit = 100
    used_calls = usage["used_requests"]
    remaining_calls = total_limit - used_calls
    percentage = math.floor((used_calls / total_limit) * 100)

    msg = (
        "📊 *𝐀𝐏𝐈 𝐐𝐮𝐨𝐭𝐚:*\n\n"
        f"𝐓𝐨𝐭𝐚𝐥: {total_limit}\n"
        f"𝐔𝐬𝐞𝐝: {used_calls}\n"
        f"𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠: {remaining_calls}\n"
        f"𝐔𝐬𝐚𝐠𝐞: {percentage}%"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text(" Pinging...")
    latency = round((time.time() - start_time) * 1000)
    await msg.edit_text(f" Ping! `{latency}ms`", parse_mode="Markdown")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    msg = (
        "📡 *𝐁𝐨𝐭 𝐒𝐭𝐚𝐭𝐮𝐬:*\n\n"
        f"𝐂𝐏𝐔: {cpu}%\n"
        f"𝐌𝐞𝐦𝐨𝐫𝐲: {mem}%"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

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

    if not number.isdigit():
        await update.message.reply_text("❌ Please send only digits of the phone number.")
        return

    if not number.startswith("91"):
        number = f"91{number}"

    # Temporary fetching message
    temp_msg = await update.message.reply_text(f"⏳ 𝐅𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐝𝐞𝐭𝐚𝐢𝐥𝐬 𝐟𝐨𝐫 `{number}` ...", parse_mode="Markdown")

    result = get_truecaller_data(number)

    # Increment usage if valid result
    if "No data" not in result and "Error" not in result:
        increment_usage()

    # Delete temp message and send result
    await temp_msg.delete()
    await update.message.reply_text(result, parse_mode="Markdown")

# === Flask Run ===
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# === Main ===
def main():
    # Delete webhook for polling
    import requests
    try:
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook")
    except:
        pass

    # Run Flask in background
    threading.Thread(target=run_flask, daemon=True).start()

    # Telegram bot
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("quota", "Check API quota"),
        BotCommand("ping", "Check bot latency"),
        BotCommand("status", "Check bot system status"),
        BotCommand("setquota", "Set API quota (admin only)"),
    ]
    application.bot.set_my_commands(commands)

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quota", quota))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("setquota", set_quota))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
