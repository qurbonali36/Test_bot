from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import Database
from globals import BTN_HOME as GLOBALS_BTN_HOME

db = Database('tg_bot.db')

with db.lock:
    db.execute("""
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        test_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(chat_id, test_id)
    );
    
    CREATE TABLE IF NOT EXISTS certificates (
        certificate_id TEXT PRIMARY KEY,
        chat_id INTEGER NOT NULL,
        test_id TEXT,
        recipient_name TEXT,
        test_name TEXT,
        score INTEGER,
        issue_date TEXT,
        png_path TEXT,
        pdf_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    db.conn.commit()

BTN_BOOKMARKS = {1: '🔖 Saqlanganlar', 2: '🔖 Сохранённые', 3: '🔖 Bookmarks'}
BTN_BOOKMARK_ADD = {1: '🔖 Saqlash', 2: '🔖 Сохранить', 3: '🔖 Save'}
BTN_BOOKMARK_REMOVE = {1: '❌ O\'chirish', 2: '❌ Удалить', 3: '❌ Remove'}

MSG_BOOKMARK_ADDED = {
    1: "✅ Test saqlandi!",
    2: "✅ Тест сохранен!",
    3: "✅ Test saved!"
}
MSG_BOOKMARK_REMOVED = {
    1: "❌ Test saqlanganlardan o'chirildi!",
    2: "❌ Тест удален из сохраненных!",
    3: "❌ Test removed from bookmarks!"
}
MSG_NO_BOOKMARKS = {
    1: "📭 Sizda saqlangan testlar yo'q.",
    2: "📭 У вас нет сохраненных тестов.",
    3: "📭 You don't have any saved tests."
}
MSG_YOUR_BOOKMARKS = {
    1: "<b>🔖 Sizning saqlangan testlaringiz:</b>\n",
    2: "<b>🔖 Ваши сохраненные тесты:</b>\n",
    3: "<b>🔖 Your saved tests:</b>\n"
}

def toggle_bookmark(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
    
    data = query.data
    # bookmark_123 yoki boshqa formatdan test_id ni ajratish
    test_id = data.replace("bookmark_", "")
    if not test_id:
        query.answer("Error")
        return
        
    with db.lock:
        is_bookmarked = db.execute_fetch('SELECT 1 FROM bookmarks WHERE chat_id = ? AND test_id = ?', (chat_id, test_id), raw_fetchone=True) is not None

    if is_bookmarked:
        with db.lock:
            total_count = db.execute_fetch('DELETE FROM bookmarks WHERE chat_id = ? AND test_id = ?', (chat_id, test_id))
            db.conn.commit()
        query.answer(MSG_BOOKMARK_REMOVED.get(lang_id, MSG_BOOKMARK_REMOVED[1]))
    else:
        with db.lock:
            try:
                bookmarks = db.execute_fetch('INSERT INTO bookmarks (chat_id, test_id) VALUES (?, ?)', (chat_id, test_id))
                db.conn.commit()
            except Exception:
                pass
        query.answer(MSG_BOOKMARK_ADDED.get(lang_id, MSG_BOOKMARK_ADDED[1]))

def show_bookmarks(update, context, page=1):
    if update.callback_query:
        query = update.callback_query
        message = query.message
        chat_id = message.chat_id
        is_callback = True
    else:
        message = update.message
        chat_id = message.chat_id
        is_callback = False
        
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
    
    limit = 5
    offset = (page - 1) * limit
    
    with db.lock:
        db.execute_fetch('SELECT test_id, created_at FROM bookmarks WHERE chat_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?', (chat_id, limit, offset), fetchall=True)
        
        db.execute_fetch('SELECT COUNT(*) FROM bookmarks WHERE chat_id = ?', (chat_id,), raw_fetchone=True)[0]
    
    if not bookmarks:
        text = MSG_NO_BOOKMARKS.get(lang_id, MSG_NO_BOOKMARKS[1])
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(GLOBALS_BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')]])
        if is_callback:
            query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
        return
        
    text = MSG_YOUR_BOOKMARKS.get(lang_id, MSG_YOUR_BOOKMARKS[1])
    keyboard = []
    
    for b in bookmarks:
        test_id = b[0]
        test_meta = db.get_test_meta(test_id)
        test_title = test_meta['title'] if test_meta and 'title' in test_meta else f"Test #{test_id}"
        
        text += f"\n🔹 <b>{test_title}</b>"
        
        # deepstart_ formatida — inlines.py dagi mavjud handler ishlaydi
        creator_id = test_meta.get('chat_id', '') if test_meta else ''
        btn_start = InlineKeyboardButton(f"▶️ {test_title}", callback_data=f"deepstart_{creator_id}_{test_id}")
        btn_remove = InlineKeyboardButton(BTN_BOOKMARK_REMOVE.get(lang_id, BTN_BOOKMARK_REMOVE[1]), callback_data=f"bm_remove_{test_id}")
        keyboard.append([btn_start, btn_remove])
        
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️", callback_data=f"bm_page_{page-1}"))
    if total_count > offset + limit:
        nav_row.append(InlineKeyboardButton("➡️", callback_data=f"bm_page_{page+1}"))
        
    if nav_row:
        keyboard.append(nav_row)
        
    keyboard.append([InlineKeyboardButton(GLOBALS_BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_callback:
        query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')

def handle_bookmark_callback(update, context):
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
    
    if data == "bm_list":
        show_bookmarks(update, context, page=1)
    
    elif data.startswith("bm_page_"):
        try:
            page = int(data.split('_')[2])
            show_bookmarks(update, context, page=page)
        except (IndexError, ValueError):
            query.answer("Error")
            
    elif data.startswith("bm_remove_"):
        try:
            test_id = data.replace("bm_remove_", "")
            with db.lock:
                exists = db.execute_fetch('DELETE FROM bookmarks WHERE chat_id = ? AND test_id = ?', (chat_id, test_id))
                db.conn.commit()
            query.answer(MSG_BOOKMARK_REMOVED.get(lang_id, MSG_BOOKMARK_REMOVED[1]))
            show_bookmarks(update, context, page=1)
        except Exception:
            query.answer("Error")
    
    elif data.startswith("bm_toggle_"):
        # Natija sahifasidan saqlash/o'chirish
        try:
            test_id_str = data.replace("bm_toggle_", "")
            with db.lock:
                db.execute_fetch('SELECT 1 FROM bookmarks WHERE chat_id = ? AND test_id = ?', (chat_id, test_id_str), raw_fetchone=True) is not None
            
            if exists:
                with db.lock:
                    db.execute_fetch('DELETE FROM bookmarks WHERE chat_id = ? AND test_id = ?', (chat_id, test_id_str))
                    db.conn.commit()
                query.answer(MSG_BOOKMARK_REMOVED.get(lang_id, MSG_BOOKMARK_REMOVED[1]), show_alert=True)
            else:
                with db.lock:
                    try:
                        db.execute_fetch('INSERT INTO bookmarks (chat_id, test_id) VALUES (?, ?)', (chat_id, test_id_str))
                        db.conn.commit()
                    except Exception:
                        pass
                query.answer(MSG_BOOKMARK_ADDED.get(lang_id, MSG_BOOKMARK_ADDED[1]), show_alert=True)
        except Exception:
            query.answer("Error")
