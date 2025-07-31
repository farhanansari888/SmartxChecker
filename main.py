import os
import json
import time
import random
import string
from datetime import datetime, timedelta
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from gatet import brn6

# --- Config ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6838940621
DATA_FILE = "data.json"

# Ensure data.json exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

# Flask App
app = Flask(__name__)

# PTB Application
application = Application.builder().token(TOKEN).build()

# --- Helpers ---
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    name = update.effective_user.first_name

    data = load_data()
    if user_id not in data:
        data[user_id] = {"plan": "𝗙𝗥𝗘𝗘", "timer": "none"}
        save_data(data)

    plan = data[user_id]["plan"]
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✨ 𝗝𝗢𝗜𝗡 ✨", url="https://t.me/smartxchecker")]])
    await update.message.reply_html(f"HELLO {name}\nYou are on {plan} plan.", reply_markup=keyboard)

async def cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    plan = data.get(str(update.effective_user.id), {}).get("plan", "𝗙𝗥𝗘𝗘")
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"✨ {plan} ✨", callback_data="plan")]])
    await update.message.reply_html("<b>Commands:\n\n✅ STRIPE AUTH: upload file\n/redeem <key>\n/code <hours> (admin)</b>", reply_markup=keyboard)

# --- File Upload ---
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    plan = data.get(user_id, {}).get("plan", "𝗙𝗥𝗘𝗘")
    if plan == "𝗙𝗥𝗘𝗘":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✨ 𝗢𝗪𝗡𝗘𝗥 ✨", url="https://t.me/smartxhacker")]])
        await update.message.reply_html("<b>Upgrade to VIP to use file checking feature.</b>", reply_markup=keyboard)
        return

    file = await update.message.document.get_file()
    await file.download_to_drive("combo.txt")

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🏴‍☠️ Stripe Auth ♻️", callback_data='b6')]])
    await update.message.reply_text("Choose gateway to use:", reply_markup=keyboard)

# --- Callback for Stripe ---
async def stripe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    with open("combo.txt", "r") as f:
        cards = f.readlines()

    live = 0
    dd = 0
    for cc in cards:
        result = brn6(cc)
        if "Approved" in result:
            live += 1
            await context.bot.send_message(chat_id=query.from_user.id, text=f"<b>Card: {cc.strip()}\nStatus: {result}</b>", parse_mode="HTML")
        else:
            dd += 1
        time.sleep(2)

    await query.edit_message_text(f"COMPLETED ✅\nLIVE: {live} | DEAD: {dd}")

# --- Redeem ---
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        key = context.args[0]
    except:
        await update.message.reply_text("Usage: /redeem <key>")
        return

    data = load_data()
    if key not in data:
        await update.message.reply_text("Invalid or already redeemed key")
        return

    timer = data[key]['time']
    plan = data[key]['plan']
    data[str(update.effective_user.id)] = {"plan": plan, "timer": timer}
    del data[key]
    save_data(data)

    await update.message.reply_html(f"<b>Key Redeemed ✅\nPlan: {plan}\nExpires: {timer}</b>")

# --- Code Generation (Admin) ---
async def gen_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        hours = float(context.args[0])
    except:
        await update.message.reply_text("Usage: /code <hours>")
        return

    expire_time = datetime.now() + timedelta(hours=hours)
    expire_str = expire_time.strftime("%Y-%m-%d %H:%M")
    key = 'moksha-' + '-'.join(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3))

    data = load_data()
    data[key] = {"plan": "𝗩𝗜𝗣", "time": expire_str}
    save_data(data)

    await update.message.reply_html(f"<b>Key Created ✅\nPlan: VIP\nExpires: {expire_str}\nKey: /redeem {key}</b>")

# --- Handlers ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("cmds", cmds))
application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
application.add_handler(CallbackQueryHandler(stripe_callback, pattern='b6'))
application.add_handler(CommandHandler("redeem", redeem))
application.add_handler(CommandHandler("code", gen_code))

# --- Flask route for webhook ---
@app.route(f"/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

@app.route("/")
def index():
    return "Bot running via Flask Webhook!", 200

# --- Set webhook at startup ---
if os.getenv("RENDER_EXTERNAL_URL"):
    import requests
    url = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"
    requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={url}")
