import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai
import json
import random
import threading
from flask import Flask, request
from datetime import datetime, timedelta

# ================= 1. SERVER SETUP =================
server = Flask(__name__)

@server.route('/')
def home():
    return "Tarot Saya Bot is Alive & Running!", 200

def run_server():
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = threading.Thread(target=run_server)
    t.start()

# ================= 2. CONFIGURATION =================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

try:
    ADMIN_ID = int(os.environ.get("ADMIN_ID"))
except:
    print("Warning: ADMIN_ID not found.")
    ADMIN_ID = 0 

# AI Setup (Model ပြင်ဆင်ထားသည်)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

bot = telebot.TeleBot(BOT_TOKEN)
DB_FILE = "users.json"

# Memory
user_questions = {}

# Images
CARD_BACK_URL = "https://i.postimg.cc/fRjsYWf7/Tarot.png"
BASE_URL = "https://www.sacred-texts.com/tarot/pkt/img"

# Bank Info (Booking - 30,000 MMK / 1 Hour)
BANK_INFO = """
🔮 <b>ဆရာ့ထံ ဗေဒင်မေးမြန်းခ (Booking)</b>
💰 <b>နှုန်းထား - ၁၀,၀၀၀ ကျပ် (၁ နာရီ)</b>

ငွေလွှဲရန်:
✅ KBZPay: 09444456145 (Soe Thurein Tun)
✅ WavePay: 09444456145 (Soe Thurein Tun)

ငွေလွှဲပြီးပါက <b>Screenshot</b> ပို့ပေးပါ။
Admin မှ စစ်ဆေးပြီး ၁ နာရီစာ ဖွင့်ပေးပါလိမ့်မယ်။
"""

# ================= 3. TAROT DECK =================
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

# ================= 4. DATABASE & FREE PERIOD LOGIC =================
FREE_START = datetime(2026, 2, 17)
FREE_END = datetime(2026, 2, 23, 23, 59, 59)

def mm_now():
    return datetime.utcnow() + timedelta(hours=6, minutes=30)

def is_free_period():
    return FREE_START <= mm_now() <= FREE_END

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
        expiry_date = datetime.strptime(users[str_id], "%Y-%m-%d %H:%M:%S")
        return expiry_date >= mm_now()
    except:
        return False

def add_subscription(user_id, hours=1):
    users = load_db()
    new_expiry = mm_now() + timedelta(hours=hours)
    users[str(user_id)] = new_expiry.strftime("%Y-%m-%d %H:%M:%S")
    save_db(users)

def claim_daily_free_hour(user_id):
    if not is_free_period():
        return False, "Not free period"
    
    users = load_db()
    today_str = mm_now().strftime("%Y-%m-%d") 
    
    last_claimed = users.get(str(user_id) + "_free_date")
    if last_claimed == today_str:
        return False, "Already claimed today"
    
    new_expiry = mm_now() + timedelta(hours=1)
    users[str(user_id)] = new_expiry.strftime("%Y-%m-%d %H:%M:%S")
    users[str(user_id) + "_free_date"] = today_str 
    save_db(users)
    return True, "Success"

# ================= 5. BOT HANDLERS =================

# (A) Start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if check_subscription(user_id):
        bot.reply_to(message, "မင်္ဂလာပါဗျာ... ဆရာ့ဆီ ရောက်လာတာ ဝမ်းသာပါတယ်။\nမိတ်ဆွေရဲ့ Booking အချိန်မကုန်ခင်လေး သိချင်တာတွေ မေးနိုင်ပါပြီ။")
    else:
        if is_free_period():
            success, _ = claim_daily_free_hour(user_id)
            if success:
                bot.reply_to(message, "မင်္ဂလာပါဗျာ... ဆရာ့ဆီ ရောက်လာတာ ဝမ်းသာပါတယ်။\n\n🎉 <b>အထူး Promotion အနေဖြင့် ဒီနေ့အတွက် (၁) နာရီ အခမဲ့ ဖွင့်ပေးလိုက်ပါပြီခင်ဗျာ။</b>\n\nစိတ်ထဲ သိချင်တာလေးတွေကို စာရိုက်ပြီး လွတ်လပ်စွာ မေးမြန်းနိုင်ပါပြီ။", parse_mode="HTML")
            else:
                bot.reply_to(message, "မင်္ဂလာပါဗျာ...\n\nဒီနေ့အတွက် (၁) နာရီ Free သုံးပြီးသွားပါပြီဗျာ။ <b>မနက်ဖြန်မှ ထပ်မံ အခမဲ့ ရယူနိုင်ပါတယ်</b> (သို့မဟုတ်) အောက်ပါအတိုင်း ငွေသွင်းပြီး Booking ချက်ချင်း ပြန်ယူနိုင်ပါတယ်။\n\n" + BANK_INFO, parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, f"မင်္ဂလာပါခင်ဗျာ... ဆရာ့ဆီမှာ ဗေဒင်မေးဖို့ Booking အရင်ယူပေးရမှာ ဖြစ်ပါတယ်ဗျ... 🙏\n\n{BANK_INFO}", parse_mode="HTML")

# (B) Handle Payment Slips
@bot.message_handler(content_types=['photo'])
def handle_slip(message):
    user_id = message.from_user.id
    bot.reply_to(message, "ကောင်းပါပြီ... ငွေလွှဲပြေစာ ရပါပြီ။ ဆရာ့တပည့် Admin လေးတွေ စစ်ဆေးပေးပါလိမ့်မယ်။ ခဏစောင့်ပေးပါ... ⏳")
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("✅ လက်ခံ (၁ နာရီ)", callback_data=f"app_{user_id}"), InlineKeyboardButton("❌ ငြင်းပယ်", callback_data=f"dec_{user_id}"))
    
    try:
        file_id = message.photo[-1].file_id
        caption = f"🔔 <b>New Booking (10,000 MMK)!</b>\nID: <code>{user_id}</code>\nName: {message.from_user.first_name}"
        bot.send_photo(ADMIN_ID, file_id, caption=caption, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        print(f"Error sending to admin: {e}")

# (C) Admin Decisions
@bot.callback_query_handler(func=lambda call: call.data.startswith(("app_", "dec_")))
def admin_decision(call):
    if call.from_user.id != ADMIN_ID: return
    action, target_id = call.data.split("_")
    
    if action == "app":
        add_subscription(target_id, hours=1)
        bot.edit_message_caption(chat_id=ADMIN_ID, message_id=call.message.message_id, caption=f"✅ Approved User {target_id} for 1 Hour")
        bot.send_message(target_id, "🎉 Booking အောင်မြင်ပါပြီဗျာ။\nအခုချိန်ကစပြီး (၁) နာရီတိတိ မေးခွန်းတွေ မေးနိုင်ပါပြီ။")
        
    elif action == "dec":
        bot.edit_message_caption(chat_id=ADMIN_ID, message_id=call.message.message_id, caption=f"❌ Declined User {target_id}")
        bot.send_message(target_id, "⚠️ ငွေလွှဲပြေစာ မမှန်ကန်ဘူး ဖြစ်နေတယ်။ သေချာပြန်စစ်ပြီး ပြန်ပို့ပေးပါဦး။")

# (D) AI-POWERED CHAT HANDLER
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_text = message.text

    # Access စစ်ဆေးခြင်း
    if not check_subscription(user_id):
        if is_free_period():
            success, _ = claim_daily_free_hour(user_id)
            if success:
                bot.reply_to(message, "🎉 <b>Promotion ကာလဖြစ်လို့ ဒီနေ့အတွက် (၁) နာရီ အခမဲ့ ဖွင့်ပေးလိုက်ပါပြီဗျာ!</b>\n\nအခုချိန်ကစပြီး ၁ နာရီအတွင်း သိချင်တာတွေ မေးနိုင်ပါပြီ။", parse_mode="HTML")
            else:
                bot.reply_to(message, "ဒီနေ့အတွက် (၁) နာရီ Free သုံးပြီးသွားပါပြီဗျာ။\n<b>မနက်ဖြန်မှ ထပ်မံ အခမဲ့ ရယူနိုင်ပါတယ်</b> (သို့မဟုတ်) အောက်ပါအတိုင်း ငွေသွင်းပြီး Booking ချက်ချင်း ပြန်ယူနိုင်ပါတယ်။\n\n" + BANK_INFO, parse_mode="HTML")
                return
        else:
            bot.reply_to(message, "Booking သက်တမ်း ကုန်ဆုံးသွားပါပြီ (သို့) မရှိသေးပါဗျ။\nထပ်မေးလိုပါက /start ကို နှိပ်ပြီး ငွေသွင်းကာ Booking ပြန်ယူပေးပါခင်ဗျာ။")
            return

    user_questions[user_id] = user_text

    # --- ချက်ချင်း ပြန်ပို့မည့် စောင့်ဆိုင်းရန် စာသား (UX) ---
    temp_msg = bot.reply_to(message, "⏳ <i>ဆရာအာရုံပြုနေပါတယ်။ ပြီးတော့ ဟောကြားချက်တွေကို စာစီပေးနေလို့ ခနစောင့်ပေးပါ။</i>", parse_mode="HTML")
    bot.send_chat_action(user_id, 'typing')

    prompt = f"""
    Role: You are 'Saya' (ဆရာ), a wise, warm, and mystical Burmese Tarot Astrologer.
    You are NOT a robot. You are a real person talking to a client.

    User Input: "{user_text}"

    Instructions:
    1. Analyze the User Input.
    2. IF it is a greeting or small talk -> Reply warmly as Saya Gyi.
    3. IF the user asks "what to ask" -> Suggest 3-4 interesting tarot questions.
    4. IF the user asks a ACTUAL FORTUNE QUESTION -> 
       - First, acknowledge the question warmly.
       - THEN, strictly append this secret tag at the very end: [SHOW_CARDS]

    Language: Burmese (Myanmar) only.
    Tone: Polite, authoritative but kind (Use "ဗျ", "နော်", "ခင်ဗျာ"). DO NOT use "ကွယ်".
    """

    try:
        response = model.generate_content(prompt)
        ai_reply = response.text.strip()

        if "[SHOW_CARDS]" in ai_reply:
            clean_reply = ai_reply.replace("[SHOW_CARDS]", "").strip()
            
            markup = InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton("ကတ် (၁)", callback_data="pick_1"), InlineKeyboardButton("ကတ် (၂)", callback_data="pick_2"), InlineKeyboardButton("ကတ် (၃)", callback_data="pick_3"))
            markup.row(InlineKeyboardButton("ကတ် (၄)", callback_data="pick_4"), InlineKeyboardButton("ကတ် (၅)", callback_data="pick_5"))
            
            # ကတ်ရွေးခိုင်းမည်ဆိုပါက ယာယီစာတန်းကို ဖျက်ပစ်မည်
            bot.delete_message(chat_id=user_id, message_id=temp_msg.message_id)
            bot.send_photo(user_id, CARD_BACK_URL, caption=f"{clean_reply}\n\n(အောက်က ကတ် ၅ ကတ်ထဲက တစ်ကတ်ကို ရွေးလိုက်ပါ... 👇)", reply_markup=markup)
        
        else:
            # ရိုးရိုးစကားပြန်ပြောမည်ဆိုပါက ယာယီစာတန်းနေရာတွင် အစားထိုးမည်
            bot.edit_message_text(chat_id=user_id, message_id=temp_msg.message_id, text=ai_reply)

    except Exception as e:
        print(f"AI CHAT ERROR: {e}")
        bot.edit_message_text(chat_id=user_id, message_id=temp_msg.message_id, text="System ပိုင်းဆိုင်ရာ ပြဿနာလေးတွေဖြစ်နေလို့ ပြန်မေးပေးပါခင်ဗျာ... အချိန် ၁ နာရီစာပြန်ထည့်ပေးပါမယ်။ ယခင်ငွေလွှဲထားတဲ့ Screen shoot လေးပြန်ပို့ပေးပါခင်ဗျာ။ အဆင်မပြေမှုအတွက် တောင်းပန်ပါတယ်ခင်ဗျာ")

# (E) Handle Card & Interpretation
@bot.callback_query_handler(func=lambda call: call.data.startswith("pick_"))
def handle_card_picked(call):
    user_id = call.from_user.id
    try:
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
    except: pass
    
    card = random.choice(TAROT_DECK)
    
    bot.send_chat_action(user_id, 'upload_photo')
    # --- ကတ်ပြရင်း စောင့်ဆိုင်းရန် စာသား ထပ်ထည့်ထားပါသည် ---
    card_msg = bot.send_photo(user_id, card['url'], caption=f"🔮 ကျရောက်သောနိမိတ်: <b>{card['name']}</b>\n\n⏳ <i>ဆရာအာရုံပြုနေပါတယ်။ ပြီးတော့ ဟောကြားချက်တွေကို စာစီပေးနေလို့ ခနစောင့်ပေးပါ။</i>", parse_mode="HTML")
    
    user_question = user_questions.get(user_id, "General Fortune")

    bot.send_chat_action(user_id, 'typing')
    
    prompt = f"""
    Role: You are 'Saya' (ဆရာ), a wise, experienced Burmese male Tarot Astrologer. 
    
    IMPORTANT: Do NOT use "ကွယ်" "ခင်ဗျား" "မင်း" . Use "ဗျ", "ခင်ဗျာ", "နော်" naturally. နာမ်စားတွေကို "သင်" "သင့်" သုံးပါ။ 

    Client's Question: "{user_question}"
    Tarot Card Drawn: "{card['name']}"

    Instructions:
    1. Interpret the card strictly based on the client's question in Burmese.
    2. Use a spoken, warm, and authoritative male tone.
    3. Analyze like a wise counselor.
    4. CRITICAL: End with a follow-up question to keep them engaged.

    Language: Burmese (Myanmar) only.
    """
    
    try:
        response = model.generate_content(prompt)
        bot.send_message(user_id, response.text)
        # အဖြေပို့ပြီးပါက ကတ်ပုံအောက်က စောင့်ဆိုင်းရန်စာသားကို ဖျက်ပေးမည်
        bot.edit_message_caption(chat_id=user_id, message_id=card_msg.message_id, caption=f"🔮 ကျရောက်သောနိမိတ်: <b>{card['name']}</b>", parse_mode="HTML")
    except Exception as e:
        print(f"GEMINI ERROR: {e}") 
        bot.send_message(user_id, "System Error: System ပိုင်းဆိုင်ရာ ပြဿနာလေးတွေဖြစ်နေလို့ ပြန်မေးပေးပါခင်ဗျာ... အချိန် ၁ နာရီစာပြန်ထည့်ပေးပါမယ်။ ယခင်ငွေလွှဲထားတဲ့ Screen shoot လေးပြန်ပို့ပေးပါခင်ဗျာ။ အဆင်မပြေမှုအတွက် တောင်းပန်ပါတယ်ခင်ဗျ")

# ================= 6. MAIN EXECUTION =================
if __name__ == "__main__":
    keep_alive()
    print("Removing old webhooks...")
    bot.remove_webhook()
    import time
    time.sleep(1)
    print("Bot is starting polling...")
    try:
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"Critical Error: {e}")
