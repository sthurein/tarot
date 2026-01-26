import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai
import json
import random
import threading
from flask import Flask, request
from datetime import datetime, timedelta

# ================= 1. SERVER SETUP (Render အတွက်) =================
server = Flask(__name__)

@server.route('/')
def home():
    return "Tarot Bot is Alive & Running!", 200

def run_server():
    # Render က သတ်မှတ်ပေးမယ့် PORT မှာ Run မယ်
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = threading.Thread(target=run_server)
    t.start()

# ================= 2. CONFIGURATION =================
# Environment Variables မှ Key များ ရယူခြင်း
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Admin ID ကို Error မတက်အောင် စစ်ဆေးပြီး ယူခြင်း
try:
    ADMIN_ID = int(os.environ.get("ADMIN_ID"))
except:
    print("Warning: ADMIN_ID not found or invalid.")
    ADMIN_ID = 0 

# AI & Bot Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')
bot = telebot.TeleBot(BOT_TOKEN)
DB_FILE = "users.json"

# ပုံ URL များ
CARD_BACK_URL = "https://upload.wikimedia.org/wikipedia/commons/5/53/RWS_Tarot_16_Tower.jpg"
BASE_URL = "https://www.sacred-texts.com/tarot/pkt/img"

# Bank Info Text
BANK_INFO = """
🔮 <b>Member ဝင်ကြေး - ၅,၀၀၀ ကျပ် (၁ လ)</b>

ငွေလွှဲရန်:
✅ KBZPay: 09-xxxxxxxxx (Name)
✅ WavePay: 09-xxxxxxxxx (Name)

ငွေလွှဲပြီးပါက <b>Screenshot</b> ပို့ပေးပါ။
Admin မှ စစ်ဆေးပြီး ချက်ချင်း ဖွင့်ပေးပါမည်။
"""

# ================= 3. TAROT DECK (78 Cards Full Set) =================
TAROT_DECK = [
    # Major Arcana
    {"name": "The Fool", "url": f"{BASE_URL}/ar00.jpg"},
    {"name": "The Magician", "url": f"{BASE_URL}/ar01.jpg"},
    {"name": "The High Priestess", "url": f"{BASE_URL}/ar02.jpg"},
    {"name": "The Empress", "url": f"{BASE_URL}/ar03.jpg"},
    {"name": "The Emperor", "url": f"{BASE_URL}/ar04.jpg"},
    {"name": "The Hierophant", "url": f"{BASE_URL}/ar05.jpg"},
    {"name": "The Lovers", "url": f"{BASE_URL}/ar06.jpg"},
    {"name": "The Chariot", "url": f"{BASE_URL}/ar07.jpg"},
    {"name": "Strength", "url": f"{BASE_URL}/ar08.jpg"},
    {"name": "The Hermit", "url": f"{BASE_URL}/ar09.jpg"},
    {"name": "Wheel of Fortune", "url": f"{BASE_URL}/ar10.jpg"},
    {"name": "Justice", "url": f"{BASE_URL}/ar11.jpg"},
    {"name": "The Hanged Man", "url": f"{BASE_URL}/ar12.jpg"},
    {"name": "Death", "url": f"{BASE_URL}/ar13.jpg"},
    {"name": "Temperance", "url": f"{BASE_URL}/ar14.jpg"},
    {"name": "The Devil", "url": f"{BASE_URL}/ar15.jpg"},
    {"name": "The Tower", "url": f"{BASE_URL}/ar16.jpg"},
    {"name": "The Star", "url": f"{BASE_URL}/ar17.jpg"},
    {"name": "The Moon", "url": f"{BASE_URL}/ar18.jpg"},
    {"name": "The Sun", "url": f"{BASE_URL}/ar19.jpg"},
    {"name": "Judgement", "url": f"{BASE_URL}/ar20.jpg"},
    {"name": "The World", "url": f"{BASE_URL}/ar21.jpg"},
    # Wands
    {"name": "Ace of Wands", "url": f"{BASE_URL}/waac.jpg"},
    {"name": "Two of Wands", "url": f"{BASE_URL}/wa02.jpg"},
    {"name": "Three of Wands", "url": f"{BASE_URL}/wa03.jpg"},
    {"name": "Four of Wands", "url": f"{BASE_URL}/wa04.jpg"},
    {"name": "Five of Wands", "url": f"{BASE_URL}/wa05.jpg"},
    {"name": "Six of Wands", "url": f"{BASE_URL}/wa06.jpg"},
    {"name": "Seven of Wands", "url": f"{BASE_URL}/wa07.jpg"},
    {"name": "Eight of Wands", "url": f"{BASE_URL}/wa08.jpg"},
    {"name": "Nine of Wands", "url": f"{BASE_URL}/wa09.jpg"},
    {"name": "Ten of Wands", "url": f"{BASE_URL}/wa10.jpg"},
    {"name": "Page of Wands", "url": f"{BASE_URL}/wapa.jpg"},
    {"name": "Knight of Wands", "url": f"{BASE_URL}/wakn.jpg"},
    {"name": "Queen of Wands", "url": f"{BASE_URL}/waqu.jpg"},
    {"name": "King of Wands", "url": f"{BASE_URL}/waki.jpg"},
    # Cups
    {"name": "Ace of Cups", "url": f"{BASE_URL}/cuac.jpg"},
    {"name": "Two of Cups", "url": f"{BASE_URL}/cu02.jpg"},
    {"name": "Three of Cups", "url": f"{BASE_URL}/cu03.jpg"},
    {"name": "Four of Cups", "url": f"{BASE_URL}/cu04.jpg"},
    {"name": "Five of Cups", "url": f"{BASE_URL}/cu05.jpg"},
    {"name": "Six of Cups", "url": f"{BASE_URL}/cu06.jpg"},
    {"name": "Seven of Cups", "url": f"{BASE_URL}/cu07.jpg"},
    {"name": "Eight of Cups", "url": f"{BASE_URL}/cu08.jpg"},
    {"name": "Nine of Cups", "url": f"{BASE_URL}/cu09.jpg"},
    {"name": "Ten of Cups", "url": f"{BASE_URL}/cu10.jpg"},
    {"name": "Page of Cups", "url": f"{BASE_URL}/cupa.jpg"},
    {"name": "Knight of Cups", "url": f"{BASE_URL}/cukn.jpg"},
    {"name": "Queen of Cups", "url": f"{BASE_URL}/cuqu.jpg"},
    {"name": "King of Cups", "url": f"{BASE_URL}/cuki.jpg"},
    # Swords
    {"name": "Ace of Swords", "url": f"{BASE_URL}/swac.jpg"},
    {"name": "Two of Swords", "url": f"{BASE_URL}/sw02.jpg"},
    {"name": "Three of Swords", "url": f"{BASE_URL}/sw03.jpg"},
    {"name": "Four of Swords", "url": f"{BASE_URL}/sw04.jpg"},
    {"name": "Five of Swords", "url": f"{BASE_URL}/sw05.jpg"},
    {"name": "Six of Swords", "url": f"{BASE_URL}/sw06.jpg"},
    {"name": "Seven of Swords", "url": f"{BASE_URL}/sw07.jpg"},
    {"name": "Eight of Swords", "url": f"{BASE_URL}/sw08.jpg"},
    {"name": "Nine of Swords", "url": f"{BASE_URL}/sw09.jpg"},
    {"name": "Ten of Swords", "url": f"{BASE_URL}/sw10.jpg"},
    {"name": "Page of Swords", "url": f"{BASE_URL}/swpa.jpg"},
    {"name": "Knight of Swords", "url": f"{BASE_URL}/swkn.jpg"},
    {"name": "Queen of Swords", "url": f"{BASE_URL}/swqu.jpg"},
    {"name": "King of Swords", "url": f"{BASE_URL}/swki.jpg"},
    # Pentacles
    {"name": "Ace of Pentacles", "url": f"{BASE_URL}/peac.jpg"},
    {"name": "Two of Pentacles", "url": f"{BASE_URL}/pe02.jpg"},
    {"name": "Three of Pentacles", "url": f"{BASE_URL}/pe03.jpg"},
    {"name": "Four of Pentacles", "url": f"{BASE_URL}/pe04.jpg"},
    {"name": "Five of Pentacles", "url": f"{BASE_URL}/pe05.jpg"},
    {"name": "Six of Pentacles", "url": f"{BASE_URL}/pe06.jpg"},
    {"name": "Seven of Pentacles", "url": f"{BASE_URL}/pe07.jpg"},
    {"name": "Eight of Pentacles", "url": f"{BASE_URL}/pe08.jpg"},
    {"name": "Nine of Pentacles", "url": f"{BASE_URL}/pe09.jpg"},
    {"name": "Ten of Pentacles", "url": f"{BASE_URL}/pe10.jpg"},
    {"name": "Page of Pentacles", "url": f"{BASE_URL}/pepa.jpg"},
    {"name": "Knight of Pentacles", "url": f"{BASE_URL}/pekn.jpg"},
    {"name": "Queen of Pentacles", "url": f"{BASE_URL}/pequ.jpg"},
    {"name": "King of Pentacles", "url": f"{BASE_URL}/peki.jpg"}
]

# ================= 4. DATABASE LOGIC =================
def load_db():
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def check_subscription(user_id):
    users = load_db()
    str_id = str(user_id)
    if str_id not in users: return False
    
    try:
        expiry_date = datetime.strptime(users[str_id], "%Y-%m-%d")
        return expiry_date >= datetime.now()
    except:
        return False

def add_subscription(user_id, days=30):
    users = load_db()
    new_expiry = datetime.now() + timedelta(days=days)
    users[str(user_id)] = new_expiry.strftime("%Y-%m-%d")
    save_db(users)

# ================= 5. BOT HANDLERS =================

# (A) Start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if check_subscription(user_id):
        bot.reply_to(message, "မင်္ဂလာပါ... Member သက်တမ်း ရှိနေပါသေးတယ်။\nဗေဒင်မေးခွန်း စမေးနိုင်ပါပြီ။")
    else:
        bot.send_message(message.chat.id, f"မင်္ဂလာပါခင်ဗျာ... 🙏\n\n{BANK_INFO}", parse_mode="HTML")

# (B) Handle Payment Slips (Photos)
@bot.message_handler(content_types=['photo'])
def handle_slip(message):
    user_id = message.from_user.id
    
    # User ကို စောင့်ခိုင်းစာပို့
    bot.reply_to(message, "ငွေလွှဲပြေစာ ရပါပြီ။ Admin စစ်ဆေးနေပါသည်။ ⏳")
    
    # Admin Approval Buttons
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ လက်ခံ (၁ လ)", callback_data=f"app_{user_id}"),
        InlineKeyboardButton("❌ ငြင်းပယ်", callback_data=f"dec_{user_id}")
    )
    
    # Admin ဆီ ပုံ Forward လုပ်ခြင်း
    try:
        file_id = message.photo[-1].file_id
        caption = f"🔔 <b>New Payment!</b>\nID: <code>{user_id}</code>\nName: {message.from_user.first_name}"
        bot.send_photo(ADMIN_ID, file_id, caption=caption, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        print(f"Error sending to admin: {e}")

# (C) Admin Button Logic
@bot.callback_query_handler(func=lambda call: call.data.startswith(("app_", "dec_")))
def admin_decision(call):
    if call.from_user.id != ADMIN_ID: return
    
    action, target_id = call.data.split("_")
    
    if action == "app":
        add_subscription(target_id)
        bot.edit_message_caption(chat_id=ADMIN_ID, message_id=call.message.message_id, caption=f"✅ Approved User {target_id}")
        bot.send_message(target_id, "🎉 Member ဝင်ခြင်း အောင်မြင်ပါသည်။\nမေးခွန်း စမေးနိုင်ပါပြီ။")
        
    elif action == "dec":
        bot.edit_message_caption(chat_id=ADMIN_ID, message_id=call.message.message_id, caption=f"❌ Declined User {target_id}")
        bot.send_message(target_id, "⚠️ ငွေလွှဲပြေစာ မမှန်ကန်ပါ။ ပြန်စစ်ပေးပါ။")

# (D) User Card Selection Logic (Show Face-down Cards)
@bot.message_handler(func=lambda message: True)
def ask_user_to_pick_card(message):
    user_id = message.from_user.id
    
    # Member စစ်ဆေးခြင်း
    if not check_subscription(user_id):
        bot.reply_to(message, "Member ဝင်ကြေး ပေးသွင်းရန် လိုအပ်ပါသည်။ /start ကို နှိပ်ပါ။")
        return

    # ခလုတ်များ ဖန်တီးခြင်း
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("ကတ် (၁)", callback_data="pick_1"), InlineKeyboardButton("ကတ် (၂)", callback_data="pick_2"), InlineKeyboardButton("ကတ် (၃)", callback_data="pick_3"))
    markup.row(InlineKeyboardButton("ကတ် (၄)", callback_data="pick_4"), InlineKeyboardButton("ကတ် (၅)", callback_data="pick_5"))
    
    # ကတ်အမှောက်ပုံ ပို့ပေးခြင်း
    bot.send_photo(user_id, CARD_BACK_URL, caption="မိတ်ဆွေရဲ့ မေးခွန်းကို အာရုံပြုပြီး...\nအောက်ပါ ကတ် ၅ ကတ်အနက် တစ်ကတ်ကို ရွေးချယ်လိုက်ပါ 👇", reply_markup=markup)

# (E) Handle Card Reveal & Gemini Interpretation
@bot.callback_query_handler(func=lambda call: call.data.startswith("pick_"))
def handle_card_picked(call):
    user_id = call.from_user.id
    
    # ခလုတ်ဟောင်းများကို ဖျက်ခြင်း
    try:
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
    except:
        pass
    
    # ကတ်ကျပန်း ရွေးခြင်း
    card = random.choice(TAROT_DECK)
    
    # ကတ်ပုံ ပို့ခြင်း
    bot.send_chat_action(user_id, 'upload_photo')
    bot.send_photo(user_id, card['url'], caption=f"🔮 ကျရောက်သောကတ်: <b>{card['name']}</b>", parse_mode="HTML")
    
    # Gemini ကို ဟောခိုင်းခြင်း
    bot.send_chat_action(user_id, 'typing')
    
    prompt = f"""
    You are a mystical Tarot Reader speaking Burmese.
    User Question context: They just picked a card for their fortune.
    Card Drawn: "{card['name']}"
    
    Explain this card's meaning in Burmese. 
    Focus on general fortune, love, and career advice.
    Tone: Warm, mystical, and supportive. Use emojis.
    """
    
    try:
        response = model.generate_content(prompt)
        bot.send_message(user_id, response.text)
    except Exception as e:
        bot.send_message(user_id, "System Error: AI is busy. Please try again.")
        print(f"Gemini Error: {e}")

# Run Server & Bot
if __name__ == "__main__":
    keep_alive() # Start Flask Server
    print("Bot is running...")
    bot.infinity_polling()
