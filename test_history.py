import math
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import Database
from globals import BTN_HOME as GLOBALS_BTN_HOME

db = Database('tg_bot.db')

BTN_HISTORY = {1: '📜 Test tarixi', 2: '📜 История тестов', 3: '📜 Test history'}

HISTORY_TITLE = {
    1: "<b>📜 Sizning test tarixingiz:</b>\n\n",
    2: "<b>📜 Ваша история тестов:</b>\n\n",
    3: "<b>📜 Your test history:</b>\n\n"
}

HISTORY_EMPTY = {
    1: "Siz hali hech qanday test yechmagansiz.",
    2: "Вы еще не проходили никаких тестов.",
    3: "You haven't taken any tests yet."
}

TEST_ITEM = {
    1: "{index}. <b>{title}</b>\n📅 {date}\n✅ Natija: {score} ball ({percent}%)\n\n",
    2: "{index}. <b>{title}</b>\n📅 {date}\n✅ Результат: {score} баллов ({percent}%)\n\n",
    3: "{index}. <b>{title}</b>\n📅 {date}\n✅ Score: {score} points ({percent}%)\n\n"
}

DETAIL_VIEW = {
    1: "<b>📊 Test natijasi tafsilotlari:</b>\n\n🏷 <b>Test nomi:</b> {title}\n📅 <b>Sana:</b> {date}\n\n✅ <b>To'g'ri javoblar:</b> {percent}%\n🎯 <b>To'plangan ball:</b> {score}\n⚡ <b>Tezlik bonusi:</b> {speed_bonus}\n\n🏆 <b>Reytingdagi o'rningiz:</b> {rank}",
    2: "<b>📊 Детали результата теста:</b>\n\n🏷 <b>Название теста:</b> {title}\n📅 <b>Дата:</b> {date}\n\n✅ <b>Правильные ответы:</b> {percent}%\n🎯 <b>Набранный балл:</b> {score}\n⚡ <b>Бонус за скорость:</b> {speed_bonus}\n\n🏆 <b>Ваше место в рейтинге:</b> {rank}",
    3: "<b>📊 Test result details:</b>\n\n🏷 <b>Test title:</b> {title}\n📅 <b>Date:</b> {date}\n\n✅ <b>Correct answers:</b> {percent}%\n🎯 <b>Score:</b> {score}\n⚡ <b>Speed bonus:</b> {speed_bonus}\n\n🏆 <b>Your rank:</b> {rank}"
}

BTN_NEXT = {1: "Keyingi ➡️", 2: "Далее ➡️", 3: "Next ➡️"}
BTN_PREV = {1: "⬅️ Oldingi", 2: "⬅️ Назад", 3: "⬅️ Prev"}
BTN_BACK = {1: "🔙 Orqaga", 2: "🔙 Назад", 3: "🔙 Back"}
BTN_DETAIL = {1: "🔍 {index}", 2: "🔍 {index}", 3: "🔍 {index}"}

def show_test_history(update, context, page=1, edit_message=False):
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
    
    limit = 10
    offset = (page - 1) * limit
    
    with db.lock:
        results = db.execute_fetch('''
            SELECT r.id as result_id, r.test_id, r.point_test, r.precent_corr_ans, 
                   r.created_at, r.speed_bonus, t.title 
            FROM users_results r
            LEFT JOIN tests_meta t ON r.test_id = t.test_id
            WHERE r.chat_id = ?
            ORDER BY r.created_at DESC
            LIMIT ? OFFSET ?
        ''', (chat_id, limit, offset), fetchall=True)
        
        total_count = db.execute_fetch('SELECT COUNT(*) FROM users_results WHERE chat_id = ?', (chat_id,), raw_fetchone=True)[0]
    
    if total_count == 0:
        text = HISTORY_EMPTY.get(lang_id, HISTORY_EMPTY[1])
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(GLOBALS_BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')]])
        if edit_message:
            update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode='HTML')
        return
        
    text = HISTORY_TITLE.get(lang_id, HISTORY_TITLE[1])
    
    keyboard = []
    row_buttons = []
    
    for i, res in enumerate(results):
        index = offset + i + 1
        title = res.get('title') or f"Test #{res['test_id']}"
        date = str(res.get('created_at', ''))[:16]
        score = res.get('point_test', 0)
        percent = res.get('precent_corr_ans', 0)
        
        text += TEST_ITEM[lang_id].format(
            index=index, title=title, date=date, score=score, percent=percent
        )
        
        btn = InlineKeyboardButton(
            BTN_DETAIL[lang_id].format(index=index), 
            callback_data=f"th_detail_{res['result_id']}_{page}"
        )
        row_buttons.append(btn)
        
        if len(row_buttons) == 5:
            keyboard.append(row_buttons)
            row_buttons = []
            
    if row_buttons:
        keyboard.append(row_buttons)
            
    nav_buttons = []
    total_pages = math.ceil(total_count / limit)
    
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(BTN_PREV[lang_id], callback_data=f"th_page_{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(BTN_NEXT[lang_id], callback_data=f"th_page_{page + 1}"))
        
    if nav_buttons:
        keyboard.append(nav_buttons)
        
    keyboard.append([InlineKeyboardButton(GLOBALS_BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if edit_message:
        update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode='HTML')

def handle_history_callback(update, context):
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
    
    if data.startswith("th_page_"):
        page = int(data.split("_")[2])
        show_test_history(update, context, page=page, edit_message=True)
        query.answer()
        
    elif data.startswith("th_detail_"):
        parts = data.split("_")
        result_id = int(parts[2])
        page = int(parts[3])
        
        with db.lock:
            res = db.execute_fetch('''
                SELECT r.id as result_id, r.chat_id, r.test_id, r.point_test, r.precent_corr_ans, 
                       r.created_at, r.speed_bonus, t.title 
                FROM users_results r
                LEFT JOIN tests_meta t ON r.test_id = t.test_id
                WHERE r.id = ?
            ''', (result_id,), fetchone=True)
            
            if res:
                res['rank'] = db.execute_fetch('''
                    SELECT COUNT(*) + 1 
                    FROM users_results 
                    WHERE test_id = ? AND point_test > ?
                ''', (res['test_id'], res['point_test']), raw_fetchone=True)[0]
        
        if not res:
            err_msg = {1: "Ma'lumot topilmadi", 2: "Данные не найдены", 3: "No data found"}
            query.answer(err_msg.get(lang_id, err_msg[1]), show_alert=True)
            return
            
        title = res.get('title') or f"Test #{res['test_id']}"
        date = str(res.get('created_at', ''))[:16]
        score = res.get('point_test', 0)
        percent = res.get('precent_corr_ans', 0)
        speed_bonus = res.get('speed_bonus', 0)
        rank = res.get('rank', "?")
        
        text = DETAIL_VIEW[lang_id].format(
            title=title, date=date, score=score, percent=percent, 
            speed_bonus=speed_bonus, rank=rank
        )
        
        keyboard = [
            [InlineKeyboardButton(BTN_BACK[lang_id], callback_data=f"th_page_{page}")],
            [InlineKeyboardButton(GLOBALS_BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
        query.answer()
