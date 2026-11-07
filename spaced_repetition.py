import datetime
import pytz
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
import globals

db = Database("tg_bot.db")

def show_spaced_repetition(update, context):
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] or 1
    
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.datetime.now(tz)
    current_date_str = now.strftime('%Y-%m-%d')
    
    due_items = db.get_due_spaced_repetitions(chat_id, current_date_str)
    
    if not due_items:
        msg = {
            1: "📚 Takrorlash uchun savollar yo'q! Dam oling.",
            2: "📚 Нет вопросов для повторения! Отдохните.",
            3: "📚 No questions to review! Take a rest."
        }
        context.bot.send_message(chat_id=chat_id, text=msg[lang_id])
        return
        
    title = globals.SPACED_REP_TITLE.get(lang_id, globals.SPACED_REP_TITLE[1])
    text = globals.SPACED_REP_REMINDER.get(lang_id, globals.SPACED_REP_REMINDER[1]).format(count=len(due_items))
    
    btn_text = globals.BTN_START_REVIEW.get(lang_id, globals.BTN_START_REVIEW[1])
    keyboard = [[InlineKeyboardButton(text=btn_text, callback_data="sr_start")]]
    
    context.bot.send_message(chat_id=chat_id, text=f"<b>{title}</b>\\n\\n{text}", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

def handle_sr_callback(update, context):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] or 1
    
    if data == "sr_start":
        tz = pytz.timezone('Asia/Tashkent')
        current_date_str = datetime.datetime.now(tz).strftime('%Y-%m-%d')
        due_items = db.get_due_spaced_repetitions(chat_id, current_date_str)
        if not due_items:
            query.answer("No items", show_alert=True)
            query.message.delete()
            return
        
        # Save state
        context.user_data['sr_items'] = due_items
        context.user_data['sr_index'] = 0
        send_sr_question(update, context, lang_id)
        
    elif data == "sr_show_ans":
        show_sr_answer(update, context, lang_id)
        
    elif data.startswith("sr_rate_"):
        rate = int(data.split("_")[2])
        process_sr_rate(update, context, lang_id, rate)

def send_sr_question(update, context, lang_id):
    items = context.user_data.get('sr_items', [])
    index = context.user_data.get('sr_index', 0)
    
    if index >= len(items):
        msg = {
            1: "✅ Barcha takrorlashlar tugadi! +20 XP",
            2: "✅ Все повторения завершены! +20 XP",
            3: "✅ All reviews completed! +20 XP"
        }
        update.callback_query.message.edit_text(msg[lang_id])
        from gamification import add_xp
        add_xp(update.effective_user.id, 20)
        return
        
    item = items[index]
    
    q_lbl = {1: "❓ Savol:", 2: "❓ Вопрос:", 3: "❓ Question:"}[lang_id]
    ans_btn = {1: "👁 Javobni ko'rish", 2: "👁 Показать ответ", 3: "👁 Show answer"}[lang_id]
    
    text = f"<b>{q_lbl}</b>\\n{item['question']}"
    kb = [[InlineKeyboardButton(text=ans_btn, callback_data="sr_show_ans")]]
    
    update.callback_query.message.edit_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))

def show_sr_answer(update, context, lang_id):
    items = context.user_data.get('sr_items', [])
    index = context.user_data.get('sr_index', 0)
    item = items[index]
    
    q_lbl = {1: "❓ Savol:", 2: "❓ Вопрос:", 3: "❓ Question:"}[lang_id]
    a_lbl = {1: "✅ Javob:", 2: "✅ Ответ:", 3: "✅ Answer:"}[lang_id]
    
    text = f"<b>{q_lbl}</b>\\n{item['question']}\\n\\n<b>{a_lbl}</b>\\n{item['correct_answer']}"
    
    btn_labels = {
        1: ["🔴 Qiyin", "🟡 O'rtacha", "🟢 Oson"],
        2: ["🔴 Сложно", "🟡 Средне", "🟢 Легко"],
        3: ["🔴 Hard", "🟡 Good", "🟢 Easy"]
    }
    
    kb = [
        [
            InlineKeyboardButton(text=btn_labels[lang_id][0], callback_data="sr_rate_1"),
            InlineKeyboardButton(text=btn_labels[lang_id][1], callback_data="sr_rate_2"),
            InlineKeyboardButton(text=btn_labels[lang_id][2], callback_data="sr_rate_3"),
        ]
    ]
    update.callback_query.message.edit_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))

def process_sr_rate(update, context, lang_id, rate):
    items = context.user_data.get('sr_items', [])
    index = context.user_data.get('sr_index', 0)
    item = items[index]
    
    # Calculate new interval
    interval = item['interval']
    if rate == 1: # Hard
        interval = max(1, interval // 2)
    elif rate == 2: # Good
        interval = int(interval * 1.5)
    else: # Easy
        interval = interval * 2 + 1
        
    tz = pytz.timezone('Asia/Tashkent')
    next_review = (datetime.datetime.now(tz) + datetime.timedelta(days=interval)).strftime('%Y-%m-%d')
    
    db.update_spaced_repetition(item['id'], next_review, interval)
    
    context.user_data['sr_index'] += 1
    send_sr_question(update, context, lang_id)
