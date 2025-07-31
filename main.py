import os
import json
import time
import random
import string
import threading
from datetime import datetime, timedelta
from flask import Flask, request
import telebot
from telebot import types, apihelper
from gatet import *

# Enable middleware for Flask + Telebot
apihelper.ENABLE_MIDDLEWARE = True

# Flask init
app = Flask(__name__)

# Telegram bot init (Render par BOT_TOKEN env me set karna)
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

stopuser = {}
admin = 6838940621  # admin user id

# Ensure data.json exists
if not os.path.exists("data.json"):
    with open("data.json", "w") as f:
        json.dump({}, f)

# --- START Command ---
@bot.message_handler(commands=["start"])
def start_cmd(message):
    name = message.from_user.first_name
    user_id = str(message.from_user.id)

    # Load or initialize user data
    with open("data.json", "r") as file:
        data = json.load(file)

    if user_id not in data:
        data[user_id] = {"plan": "𝗙𝗥𝗘𝗘", "timer": "none"}
        with open("data.json", "w") as file:
            json.dump(data, file, indent=4)

    plan = data[user_id]["plan"]

    # Reply with welcome message
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="✨ 𝗝𝗢𝗜𝗡 ✨", url="https://t.me/smartxchecker")
    keyboard.add(button)
    bot.send_message(message.chat.id, f"<b>HELLO {name}\nYou are on {plan} plan.</b>", reply_markup=keyboard)

# --- CMDS Command ---
@bot.message_handler(commands=["cmds"])
def cmds(message):
    with open("data.json", "r") as file:
        data = json.load(file)
    plan = data.get(str(message.from_user.id), {}).get("plan", "𝗙𝗥𝗘𝗘")

    keyboard = types.InlineKeyboardMarkup()
    contact_button = types.InlineKeyboardButton(text=f"✨ {plan} ✨", callback_data='plan')
    keyboard.add(contact_button)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"<b>Commands available:\n\n✅ STRIPE AUTH: /st\n\nMore gateways coming soon!</b>",
        reply_markup=keyboard
    )

# --- File Upload Handler ---
@bot.message_handler(content_types=["document"])
def handle_file(message):
    name = message.from_user.first_name
    user_id = str(message.from_user.id)

    # Load plan info
    with open("data.json", "r") as file:
        data = json.load(file)

    plan = data.get(user_id, {}).get("plan", "𝗙𝗥𝗘𝗘")

    # If FREE, ask for VIP
    if plan == "𝗙𝗥𝗘𝗘":
        keyboard = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥 ✨", url="https://t.me/smartxhacker")
        keyboard.add(btn)
        bot.send_message(message.chat.id, f"<b>HELLO {name}\nUpgrade to VIP to use file checking feature.</b>", reply_markup=keyboard)
        return

    # Save uploaded file
    file_info = bot.get_file(message.document.file_id)
    file_data = bot.download_file(file_info.file_path)
    with open("combo.txt", "wb") as f:
        f.write(file_data)

    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="🏴‍☠️ Stripe Auth ♻️", callback_data='b6')
    keyboard.add(button)
    bot.reply_to(message, "Choose the gateway you want to use:", reply_markup=keyboard)

# --- Stripe Auth Callback ---
@bot.callback_query_handler(func=lambda call: call.data == 'b6')
def stripe_auth(call):
    def process_cards():
        user_id = call.from_user.id
        gate = 'Stripe Auth'
        dd = live = 0

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Checking your cards...⌛"
        )

        with open("combo.txt", "r") as file:
            cards = file.readlines()

        total = len(cards)
        stopuser[str(user_id)] = {"status": "start"}

        for cc in cards:
            if stopuser[str(user_id)]["status"] == "stop":
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text='STOPPED ✅\nBOT BY ➜ @smartxhacker'
                )
                return

            start_time = time.time()
            try:
                result = str(brn6(cc))
            except Exception as e:
                result = "ERROR"

            # Build message
            msg = f"""<b>Card ➼ <code>{cc.strip()}</code>
Status ➼ {result}
Gateway ➼ {gate}
Time ➼ {"{:.1f}".format(time.time()-start_time)}s
BOT BY: @smartxhacker</b>"""

            if "Approved" in result or "succeeded" in result or "Duplicate" in result:
                live += 1
                bot.send_message(call.from_user.id, msg)
            else:
                dd += 1

            time.sleep(3)  # Delay between checks

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="COMPLETED ✅\nBOT BY ➜ @smartxhacker"
        )

    threading.Thread(target=process_cards).start()

# --- Redeem Command ---
@bot.message_handler(func=lambda m: m.text.lower().startswith('.redeem') or m.text.lower().startswith('/redeem'))
def redeem_key(message):
    def process_redeem():
        try:
            key = message.text.split(' ')[1]
            with open('data.json', 'r') as file:
                data = json.load(file)

            # Transfer plan and timer to user
            if key not in data:
                bot.reply_to(message, "<b>Invalid or already redeemed key</b>", parse_mode="HTML")
                return

            timer = data[key]['time']
            plan = data[key]['plan']

            data[str(message.from_user.id)] = {"plan": plan, "timer": timer}
            del data[key]

            with open('data.json', 'w') as file:
                json.dump(data, file, indent=4)

            bot.reply_to(message, f"<b>Key Redeemed Successfully ✅\nPlan: {plan}\nExpires: {timer}</b>", parse_mode="HTML")
        except Exception as e:
            bot.reply_to(message, "<b>Incorrect code or already redeemed</b>", parse_mode="HTML")

    threading.Thread(target=process_redeem).start()

# --- Code Generation (Admin Only) ---
@bot.message_handler(commands=["code"])
def gen_code(message):
    def process_code():
        if message.from_user.id != admin:
            return

        try:
            hours = float(message.text.split(' ')[1])
        except:
            bot.reply_to(message, "Usage: /code <hours>")
            return

        expire_time = datetime.now() + timedelta(hours=hours)
        expire_str = expire_time.strftime("%Y-%m-%d %H:%M")

        # Generate random key
        key = 'moksha-' + '-'.join(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3))

        # Save key
        with open("data.json", "r") as file:
            data = json.load(file)

        data[key] = {"plan": "𝗩𝗜𝗣", "time": expire_str}

        with open("data.json", "w") as file:
            json.dump(data, file, indent=4)

        bot.reply_to(message, f"<b>Key Created ✅\nPlan: VIP\nExpires: {expire_str}\nKey: /redeem {key}</b>", parse_mode="HTML")

    threading.Thread(target=process_code).start()

# --- Stop Callback ---
@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def stop_check(call):
    stopuser[str(call.from_user.id)]["status"] = "stop"

# --- Webhook Route ---
@app.route('/webhook', methods=['POST'])
def webhook():
    print("Update received")  # DEBUG
    json_str = request.get_data(as_text=True)
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# --- Set webhook at startup ---
url = os.getenv("RENDER_EXTERNAL_URL")
if url:
    bot.remove_webhook()
    bot.set_webhook(url + '/webhook')

# --- Health Check ---
@app.route('/')
def index():
    return "Bot is running via Flask Webhook!", 200
