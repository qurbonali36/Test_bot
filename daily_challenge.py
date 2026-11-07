import json
import os
import random
from datetime import datetime
import globals
from database import Database
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

db = Database("tg_bot.db")

FAN_FILES = {
    "matematika": "json_files/matematika.json",
    "fizika": "json_files/fizika.json",
    "biologiya": "json_files/biologiya.json",
    "kimyo": "json_files/kimyo.json",
    "tarix": "json_files/tarix.json",
    "adabiyot": "json_files/adabiyot.json",
    "ingiliz_tili": "json_files/ingiliz_tili.json",
}

FAN_NAMES = {
    "matematika": {1: "📐 Matematika", 2: "📐 Математика", 3: "📐 Mathematics"},
    "fizika": {1: "⚛️ Fizika", 2: "⚛️ Физика", 3: "⚛️ Physics"},
    "biologiya": {1: "🧬 Biologiya", 2: "🧬 Биология", 3: "🧬 Biology"},
    "kimyo": {1: "🧪 Kimyo", 2: "🧪 Химия", 3: "🧪 Chemistry"},
    "tarix": {1: "🏛 Tarix", 2: "🏛 История", 3: "🏛 History"},
    "adabiyot": {1: "📖 Adabiyot", 2: "📖 Литература", 3: "📖 Literature"},
    "ingiliz_tili": {1: "🇬🇧 Ingliz tili", 2: "🇬🇧 Английский", 3: "🇬🇧 English"},
}


def get_or_create_daily(lang_id):
    """Bugungi kundalik testni olish yoki yaratish."""
    today = datetime.now().strftime("%Y-%m-%d")
    existing = db.get_daily_challenge(today)
    if existing:
        return existing

    # Random fan tanlash
    available_fans = []
    for fan_key, file_path in FAN_FILES.items():
        if os.path.exists(file_path):
            available_fans.append(fan_key)

    if not available_fans:
        return None

    fan_key = random.choice(available_fans)
    try:
        with open(FAN_FILES[fan_key], 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
        if not all_questions:
            return None
        # Random 5-10 ta savol tanlash
        count = min(random.randint(5, 10), len(all_questions))
        selected = random.sample(all_questions, count)
        test_data = json.dumps(selected, ensure_ascii=False)
        db.save_daily_challenge(today, test_data, fan_key)
        return {"date": today, "test_data": test_data, "fan": fan_key}
    except Exception:
        return None


def show_daily_challenge(update, context):
    """Kundalik test sahifasini ko'rsatish."""
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    today = datetime.now().strftime("%Y-%m-%d")
    streak_data = db.get_user_streak(chat_id)
    streak = streak_data.get('current_streak', 0)

    # Bugun allaqachon ishlaganmi?
    if streak_data.get('last_date') == today:
        keyboard = [
            [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='back')],
            [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
        ]
        text = globals.TEXT_DAILY_DONE[lang_id].format(streak=streak)
        if update.message:
            update.message.reply_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        elif update.callback_query:
            update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    daily = get_or_create_daily(lang_id)
    if not daily:
        text = globals.TEXT_LB_EMPTY[lang_id]
        if update.message:
            update.message.reply_text(text, parse_mode='HTML')
        return

    fan_key = daily.get('fan', '')
    fan_name = FAN_NAMES.get(fan_key, {}).get(lang_id, fan_key)
    test_data = json.loads(daily['test_data'])
    amount = len(test_data)

    text = globals.TEXT_DAILY_TITLE[lang_id]
    text += globals.TEXT_DAILY_INFO[lang_id].format(fan=fan_name, amount=amount, streak=streak)

    keyboard = [
        [InlineKeyboardButton(globals.BTN_DAILY_START[lang_id], callback_data='daily_start')],
        [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='back')],
        [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


def start_daily_test(update, context):
    """Kundalik testni boshlash."""
    query = update.callback_query
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    today = datetime.now().strftime("%Y-%m-%d")
    streak_data = db.get_user_streak(chat_id)
    if streak_data.get('last_date') == today:
        query.answer(globals.TEXT_DAILY_DONE[lang_id].replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '').format(streak=streak_data['current_streak']), show_alert=True)
        return

    daily = db.get_daily_challenge(today)
    if not daily:
        return

    test_data = json.loads(daily['test_data'])

    context.user_data['savollar_bazasi'] = test_data
    context.user_data['amount_quest'] = len(test_data)
    context.user_data['current_quest'] = 0
    context.user_data['correct_ans'] = 0
    context.user_data['chat_id'] = chat_id
    context.user_data['test_id'] = f'daily_{today}'
    context.user_data['is_daily'] = True

    user = update.effective_user
    context.user_data['name_link'] = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'

    query.answer()
    try:
        import time
        query.edit_message_text(text=globals.READY_3[lang_id], parse_mode='HTML')
        time.sleep(1.5)
        query.edit_message_text(text=globals.READY_2[lang_id], parse_mode='HTML')
        time.sleep(1.5)
        query.edit_message_text(text=globals.READY_1[lang_id], parse_mode='HTML')
        time.sleep(1)
        query.message.delete()
    except:
        pass

    from quest_poll import send_polls
    send_polls(context)


def process_daily_completion(chat_id, context):
    """Kundalik test tugagandan so'ng streak yangilash."""
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    today = datetime.now().strftime("%Y-%m-%d")

    streak_result = db.update_user_streak(chat_id, today)
    streak = streak_result.get('current_streak', 0)

    # Streak bonuslari
    bonus_xp = 0
    if streak >= 30:
        bonus_xp = 100
    elif streak >= 7:
        bonus_xp = 25
    elif streak >= 3:
        bonus_xp = 10

    if bonus_xp > 0:
        db.add_user_xp(chat_id, bonus_xp)
        try:
            text = globals.TEXT_STREAK_BONUS[lang_id].format(xp=bonus_xp, streak=streak)
            context.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
        except:
            pass

    return streak
