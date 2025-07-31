import os
import json
import time
import random
import string
import threading
from datetime import datetime, timedelta
import requests
from telebot import TeleBot, types
from gatet import brn6  # Tumhare SmartxChecker ka gateway logic

# ====== CONFIGURATION ======
TOKEN = "BOT_TOKEN"  # apna token yahan daalo
ADMIN_ID = 6176865951     # tumhara admin ID
DATA_FILE = "data.json"
COMBO_FILE = "combo.txt"

bot = TeleBot(TOKEN, parse_mode="HTML")
stopuser = {}

# ====== DATA HANDLING ======
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ====== USER PLAN CHECK ======
def ensure_user(user_id):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {"plan": "𝗙𝗥𝗘𝗘", "timer": "none"}
        save_data(data)
    return data

def get_user_plan(user_id):
    data = ensure_user(user_id)
    return data[str(user_id)]["plan"]

def is_vip_active(user_id):
    data = ensure_user(user_id)
    if data[str(user_id)]["plan"] != "𝗩𝗜𝗣":
        return False
    try:
        expiry = datetime.strptime(data[str(user_id)]["timer"].split(".")[0], "%Y-%m-%d %H:%M")
        return datetime.now() < expiry
    except:
        return False

# ====== START COMMAND ======
@bot.message_handler(commands=["start"])
def start(message):
    user_plan = get_user_plan(message.from_user.id)
    keyboard = types.InlineKeyboardMarkup()
    if user_plan == "𝗙𝗥𝗘𝗘":
        btn = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥 ✨", url="https://t.me/Mai_Nitesh")
        caption = (f"<b>HELLO {message.from_user.first_name}\n\n"
                   "The VIP plan allows you to use all tools and gateways without limits.\n"
                   "You can also check cards through a file.\n\n"
                   "Payment methods:\nUPI\n━━━━━━━━━━━━━━━━━\nGood luck\n『@smartxhacker』</b>")
    else:
        btn = types.InlineKeyboardButton(text="✨ 𝗝𝗢𝗜𝗡 ✨", url="https://t.me/smartxchecker_bot")
        caption = "Click /cmds to view commands or send a file to check cards."
    keyboard.add(btn)
    bot.send_photo(chat_id=message.chat.id,
                   photo="https://t.me/GF_MAA/881",
                   caption=caption,
                   reply_markup=keyboard)

# ====== COMMAND LIST ======
@bot.message_handler(commands=["cmds"])
def cmds(message):
    user_plan = get_user_plan(message.from_user.id)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=f"✨ {user_plan} ✨", callback_data="plan"))
    bot.send_message(message.chat.id,
                     text="<b>These are the bot's commands\n\n"
                          "✅ STRIPE AUTH <code>/st</code>\n\n"
                          "More gateways will be added soon</b>",
                     reply_markup=keyboard)

# ====== FILE UPLOAD HANDLER ======
@bot.message_handler(content_types=["document"])
def handle_file(message):
    user_id = message.from_user.id
    plan = get_user_plan(user_id)

    # Check VIP status
    if not is_vip_active(user_id):
        bot.send_message(message.chat.id,
                         "<b>Your plan is FREE or expired. Upgrade to VIP to use this feature.</b>")
        return

    # Save uploaded file
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    with open(COMBO_FILE, "wb") as f:
        f.write(downloaded)

    # Show gateway selection
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="🏴‍☠️ Stripe Auth ♻️", callback_data="stripe"))
    bot.reply_to(message, "Choose the gateway you want to use:", reply_markup=keyboard)

# ====== STRIPE AUTH CHECKER ======
@bot.callback_query_handler(func=lambda call: call.data == "stripe")
def stripe_checker(call):
    def run_checker():
        user_id = call.from_user.id
        stopuser[user_id] = {"status": "start"}

        try:
            with open(COMBO_FILE, "r") as f:
                cards = f.readlines()

            total = len(cards)
            live, dead = 0, 0

            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Checking your cards...⌛")

            for cc in cards:
                if stopuser[user_id]["status"] == "stop":
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          text="Stopped ✅\nBot by ➜ @smartxhacker")
                    return

                # BIN lookup
                try:
                    bin_data = requests.get(f"https://lookup.binlist.net/{cc[:6]}").json()
                    bank = bin_data.get("bank", {}).get("name", "unknown")
                    country = bin_data.get("country", {}).get("name", "unknown")
                    flag = bin_data.get("country", {}).get("emoji", "🏳")
                    brand = bin_data.get("scheme", "unknown")
                    card_type = bin_data.get("type", "unknown")
                except:
                    bank, country, flag, brand, card_type = "unknown", "unknown", "🏳", "unknown", "unknown"

                # Check via brn6
                try:
                    result = str(brn6(cc))
                except Exception as e:
                    result = "ERROR"

                # Determine status
                if any(x in result for x in ["success", "Approved", "Duplicate", "succeeded"]):
                    live += 1
                    msg = (f"<b>Approved ✅\n\n"
                           f"Card ➼ <code>{cc}</code>\n"
                           f"Gateway ➼ Stripe Auth\n"
                           f"Info ➼ {card_type} - {brand}\n"
                           f"Country ➼ {country} {flag}\n"
                           f"Bank ➼ {bank}\n"
                           f"Bot By: @smartxhacker</b>")
                    bot.send_message(user_id, msg)
                else:
                    dead += 1

                # Update status inline
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(types.InlineKeyboardButton(f"• APPROVED ✅ [{live}] •", callback_data="x"),
                           types.InlineKeyboardButton(f"• DECLINED ❌ [{dead}] •", callback_data="x"),
                           types.InlineKeyboardButton(f"• TOTAL 👻 [{total}] •", callback_data="x"),
                           types.InlineKeyboardButton("[ STOP ]", callback_data="stop"))
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=f"Checking cards at Stripe Auth...\nBot By @smartxhacker",
                                      reply_markup=markup)

                time.sleep(5)

            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Completed ✅\nBot By ➜ @smartxhacker")

        except Exception as e:
            print("Error in checker:", e)

    threading.Thread(target=run_checker).start()

# ====== STOP BUTTON ======
@bot.callback_query_handler(func=lambda call: call.data == "stop")
def stop_checker(call):
    user_id = call.from_user.id
    if user_id in stopuser:
        stopuser[user_id]["status"] = "stop"

# ====== REDEEM COMMAND ======
@bot.message_handler(func=lambda msg: msg.text.lower().startswith("/redeem") or msg.text.lower().startswith(".redeem"))
def redeem_key(message):
    try:
        key = message.text.split(" ")[1]
        data = load_data()
        if key not in data:
            bot.reply_to(message, "<b>Invalid or already redeemed key.</b>")
            return
        # Transfer plan/timer
        data[str(message.from_user.id)] = data[key]
        del data[key]
        save_data(data)
        bot.reply_to(message, "<b>Key redeemed successfully! You are now VIP.</b>")
    except Exception as e:
        bot.reply_to(message, "<b>Error redeeming key.</b>")

# ====== CODE GENERATION (ADMIN) ======
@bot.message_handler(commands=["code"])
def generate_code(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        hours = float(message.text.split(" ")[1])
        expiry_time = datetime.now() + timedelta(hours=hours)
        expiry_str = expiry_time.strftime("%Y-%m-%d %H:%M")

        # Generate random key
        key = "moksha-" + "-".join(["".join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3)])
        data = load_data()
        data[key] = {"plan": "𝗩𝗜𝗣", "time": expiry_str}
        save_data(data)

        bot.reply_to(message, f"<b>Key Created ✅\n\nPlan ➜ VIP\nExpires ➜ {expiry_str}\nKey ➜ <code>/redeem {key}</code></b>")
    except Exception as e:
        bot.reply_to(message, f"<b>Error: {e}</b>")

# ====== START POLLING ======
print("Bot Started ✅")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Polling error:", e)
        time.sleep(3)
