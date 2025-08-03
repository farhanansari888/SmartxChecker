import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from truecaller_api import search_number

# Telegram Bot Token
import os
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Logging Setup
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO
)


# -------- Helper: Sanitize Number --------
def format_number(raw_number: str) -> str:
    """
    Format number to '91XXXXXXXXXX'
    """
    raw_number = raw_number.strip().replace(" ", "").replace("-", "")

    if raw_number.startswith("+91"):
        return raw_number.replace("+", "")  # +91 → 91
    elif raw_number.startswith("91") and len(raw_number) == 12:
        return raw_number
    elif len(raw_number) == 10:
        return "91" + raw_number
    else:
        return None


# -------- Commands --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to SmartxChecker!\n\nSend me a phone number to lookup details via Truecaller API."
    )


# -------- Handle Numbers --------
async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_number = update.message.text

    # Format number
    phone_number = format_number(raw_number)
    if not phone_number:
        await update.message.reply_text("⚠️ Invalid number format. Send a valid 10-digit Indian number.")
        return

    # Log formatted number
    logging.info(f"User input: {raw_number} | Formatted: {phone_number}")

    # Call API
    result = search_number(phone_number)

    # Show result
    if "error" in result:
        await update.message.reply_text(f"❌ {result['error']}")
    else:
        reply = (
            f"📞 *Number Details*\n\n"
            f"**Name:** {result['name']}\n"
            f"**Carrier:** {result['carrier']}\n"
            f"**Country:** {result['country']}\n"
            f"**Score:** {result['score']}\n"
            f"**Spam:** {'Yes' if result['spam'] else 'No'}"
        )
        await update.message.reply_text(reply, parse_mode="Markdown")


# -------- Main --------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))

    logging.info("Bot started polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
