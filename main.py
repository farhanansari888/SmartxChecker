import json
import os
import random
import string
import asyncio
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from gatet import brn6

# --- Global setup ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6838940621
DATA_FILE = "data.json"
COMBO_FILE = "combo.txt"
stopuser = {}

# Ensure data.json exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)


# Utility functions
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# --- START Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    if str(user.id) not in data:
        data[str(user.id)] = {"plan": "𝗙𝗥𝗘𝗘", "timer": "none"}
        save_data(data)

    plan = data[str(user.id)]["plan"]

    keyboard = [
        [InlineKeyboardButton("✨ 𝗝𝗢𝗜𝗡 ✨", url="https://t.me/smartxchecker")]
    ]
    await update.message.reply_text(
        f"<b>HELLO {user.first_name}\nYou are on {plan} plan.</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


# --- CMDS Command ---
async def cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    plan = data.get(str(update.effective_user.id), {}).get("plan", "𝗙𝗥𝗘𝗘")

    keyboard = [[InlineKeyboardButton(f"✨ {plan} ✨", callback_data="plan")]]
    await update.message.reply_text(
        "<b>Commands:\n\n✅ STRIPE AUTH: upload file then select gateway\n\nMore tools soon!</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


# --- File Upload ---
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    plan = data.get(user_id, {}).get("plan", "𝗙𝗥𝗘𝗘")

    if plan == "𝗙𝗥𝗘𝗘":
        keyboard = [
            [InlineKeyboardButton("✨ 𝗢𝗪𝗡𝗘𝗥 ✨", url="https://t.me/smartxhacker")]
        ]
        await update.message.reply_text(
            "<b>Upgrade to VIP to use file checking feature.</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )
        return

    # Download file
    file = await context.bot.get_file(update.message.document.file_id)
    combo_data = await file.download_as_bytearray()

    with open(COMBO_FILE, "wb") as f:
        f.write(combo_data)

    keyboard = [
        [InlineKeyboardButton("🏴‍☠️ Stripe Auth ♻️", callback_data="b6")]
    ]
    await update.message.reply_text(
        "Choose gateway to use:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


# --- Stripe Auth Callback ---
async def stripe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    stopuser[user_id] = {"status": "start"}

    with open(COMBO_FILE, "r") as f:
        cards = f.readlines()

    await query.edit_message_text("Checking your cards...⌛")

    live, dead = 0, 0
    for cc in cards:
        if stopuser[user_id]["status"] == "stop":
            await query.edit_message_text("STOPPED ✅\nBOT BY ➜ @smartxhacker")
            return

        start_time = time.time()
        try:
            result = str(brn6(cc))
        except Exception:
            result = "ERROR"

        msg = (
            f"<b>Card ➼ <code>{cc.strip()}</code>\n"
            f"Status ➼ {result}\n"
            f"Gateway ➼ Stripe Auth\n"
            f"Time ➼ {'{:.1f}'.format(time.time() - start_time)}s\n"
            f"BOT BY: @smartxhacker</b>"
        )

        if "Approved" in result or "succeeded" in result or "Duplicate" in result:
            live += 1
            await context.bot.send_message(query.from_user.id, msg, parse_mode="HTML")
        else:
            dead += 1

        await asyncio.sleep(3)

    await query.edit_message_text("COMPLETED ✅\nBOT BY ➜ @smartxhacker")


# --- Redeem Command ---
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    try:
        key = context.args[0]
    except IndexError:
        await update.message.reply_text("<b>Usage: /redeem <key></b>", parse_mode="HTML")
        return

    if key not in data:
        await update.message.reply_text(
            "<b>Invalid or already redeemed key</b>", parse_mode="HTML"
        )
        return

    timer = data[key]["time"]
    plan = data[key]["plan"]

    data[str(update.effective_user.id)] = {"plan": plan, "timer": timer}
    del data[key]
    save_data(data)

    await update.message.reply_text(
        f"<b>Key Redeemed ✅\nPlan: {plan}\nExpires: {timer}</b>", parse_mode="HTML"
    )


# --- Code Generation (Admin) ---
async def code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        hours = float(context.args[0])
    except:
        await update.message.reply_text("Usage: /code <hours>")
        return

    expire_time = datetime.now() + timedelta(hours=hours)
    expire_str = expire_time.strftime("%Y-%m-%d %H:%M")

    key = "moksha-" + "-".join(
        "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        for _ in range(3)
    )

    data = load_data()
    data[key] = {"plan": "𝗩𝗜𝗣", "time": expire_str}
    save_data(data)

    await update.message.reply_text(
        f"<b>Key Created ✅\nPlan: VIP\nExpires: {expire_str}\nKey: /redeem {key}</b>",
        parse_mode="HTML",
    )


# --- Stop Callback ---
async def stop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    stopuser[str(query.from_user.id)]["status"] = "stop"
    await query.answer("Stopped!")


# --- Main (Webhook mode for Render) ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cmds", cmds))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("code", code))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(CallbackQueryHandler(stripe_callback, pattern="^b6$"))
    app.add_handler(CallbackQueryHandler(stop_callback, pattern="^stop$"))

    # Webhook setup
    port = int(os.getenv("PORT", 10000))
    url = os.getenv("RENDER_EXTERNAL_URL")
    webhook_url = f"{url}/{BOT_TOKEN}"

    print(f"Setting webhook at {webhook_url}")

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=BOT_TOKEN,
        webhook_url=webhook_url
    )


if __name__ == "__main__":
    main()
