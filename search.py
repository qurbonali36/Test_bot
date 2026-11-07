from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import Database
from globals import BTN_HOME as GLOBALS_BTN_HOME

db = Database('tg_bot.db')

STATES = {'search': 10}
BTN_SEARCH = {1: '🔍 Qidirish', 2: '🔍 Поиск', 3: '🔍 Search'}

TEXT_SEARCH_PROMPT = {
    1: "<b>🔍 Qidirish</b>\n\nTest nomini, yaratuvchi ismini yoki test ID sini kiriting:",
    2: "<b>🔍 Поиск</b>\n\nВведите название теста, имя создателя или ID теста:",
    3: "<b>🔍 Search</b>\n\nEnter test title, creator name or test ID:"
}

TEXT_NO_RESULTS = {
    1: "❌ Hech narsa topilmadi. Boshqa so'z bilan urinib ko'ring.",
    2: "❌ Ничего не найдено. Попробуйте другое слово.",
    3: "❌ Nothing found. Try another word."
}

TEXT_SEARCH_RESULTS = {
    1: "<b>🔍 Qidiruv natijalari:</b>\n\n",
    2: "<b>🔍 Результаты поиска:</b>\n\n",
    3: "<b>🔍 Search results:</b>\n\n"
}

TEXT_TEST_INFO = {
    1: "<b>🆔 ID:</b> {test_id}\n<b>📚 Nomi:</b> {title}\n<b>❓ Savollar:</b> {amount}\n<b>👤 Yaratuvchi:</b> {creator}\n",
    2: "<b>🆔 ID:</b> {test_id}\n<b>📚 Название:</b> {title}\n<b>❓ Вопросы:</b> {amount}\n<b>👤 Создатель:</b> {creator}\n",
    3: "<b>🆔 ID:</b> {test_id}\n<b>📚 Title:</b> {title}\n<b>❓ Questions:</b> {amount}\n<b>👤 Creator:</b> {creator}\n"
}

BTN_START_TEST = {
    1: "▶️ Boshlash",
    2: "▶️ Начать",
    3: "▶️ Start"
}

def start_search(update, context):
    chat_id = update.message.chat_id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
    
    context.user_data['state'] = STATES['search']
    
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(GLOBALS_BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')]])
    update.message.reply_text(
        TEXT_SEARCH_PROMPT.get(lang_id, TEXT_SEARCH_PROMPT[1]),
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

def handle_search_input(update, context):
    chat_id = update.message.chat_id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
    query = update.message.text
    
    show_search_results(update.message, context, query, page=0, lang_id=lang_id)

def show_search_results(message, context, query, page, lang_id):
    limit = 5
    offset = page * limit
    
    with db.lock:
        sql = """
            SELECT t.test_id, t.title, t.description, t.amount, t.created_at, 
                   t.chat_id as creator_id, u.first_name, u.last_name
            FROM tests_meta t
            JOIN user u ON t.chat_id = u.chat_id
            WHERE t.title LIKE ? OR u.first_name LIKE ? OR u.last_name LIKE ? OR CAST(t.test_id AS TEXT) = ?
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        """
        like_query = f"%{query}%"
        results = db.execute_fetch(sql, (like_query, like_query, like_query, query, limit, offset), raw_fetchall=True)
        
        count_sql = """
            SELECT COUNT(*)
            FROM tests_meta t
            JOIN user u ON t.chat_id = u.chat_id
            WHERE t.title LIKE ? OR u.first_name LIKE ? OR u.last_name LIKE ? OR CAST(t.test_id AS TEXT) = ?
        """
        total = db.execute_fetch(count_sql, (like_query, like_query, like_query, query), raw_fetchone=True)[0]
    
    if total == 0:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(GLOBALS_BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')]])
        message.reply_text(TEXT_NO_RESULTS.get(lang_id, TEXT_NO_RESULTS[1]), reply_markup=reply_markup, parse_mode='HTML')
        return

    text = TEXT_SEARCH_RESULTS.get(lang_id, TEXT_SEARCH_RESULTS[1])
    keyboard = []
    
    for row in results:
        test_id, title, desc, amount, created_at, creator_id, f_name, l_name = row
        creator = f"{f_name or ''} {l_name or ''}".strip()
        
        text += TEXT_TEST_INFO.get(lang_id, TEXT_TEST_INFO[1]).format(
            test_id=test_id, title=title or "Nomsiz", amount=amount or 0, creator=creator
        )
        text += "------------------------\n"
        
        # deepstart_ formati — mavjud handler to'g'ridan-to'g'ri ishlaydi
        btn_text = f"{BTN_START_TEST.get(lang_id, BTN_START_TEST[1])} - {(title or 'Test')[:20]}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"deepstart_{creator_id}_{test_id}")])
        
    nav_buttons = []
    context.user_data['search_query'] = query
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"search_page_{page-1}"))
    if offset + limit < total:
        nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"search_page_{page+1}"))
        
    if nav_buttons:
        keyboard.append(nav_buttons)
        
    keyboard.append([InlineKeyboardButton(GLOBALS_BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # state ni menuga qaytarish
    import globals as g
    context.user_data['state'] = g.STATES['menu']
    
    if hasattr(message, 'text') and message.text and not hasattr(message, 'edit_text'):
        message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        try:
            message.edit_text(text, reply_markup=reply_markup, parse_mode='HTML')
        except Exception:
            context.bot.send_message(chat_id=message.chat_id, text=text, reply_markup=reply_markup, parse_mode='HTML')

def handle_search_callback(update, context):
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
    
    if data.startswith("search_page_"):
        page = int(data.replace("search_page_", ""))
        search_query = context.user_data.get('search_query', '')
        if not search_query:
            query.answer("Search query expired.", show_alert=True)
            return
            
        show_search_results(query.message, context, search_query, page, lang_id)
        query.answer()

