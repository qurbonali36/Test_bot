import globals
from database import Database
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

db = Database("tg_bot.db")

def show_my_tests(update, context):
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    tests = db.get_user_tests(chat_id)
    if not tests:
        keyboard = [
            [InlineKeyboardButton(globals.BTN_SETTINGS_BACK[lang_id], callback_data='settings_back')],
            [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            update.callback_query.edit_message_text(text=globals.TEXT_NO_TESTS[lang_id], parse_mode='HTML', reply_markup=reply_markup)
        else:
            context.bot.send_message(chat_id=chat_id, text=globals.TEXT_NO_TESTS[lang_id], parse_mode='HTML', reply_markup=reply_markup)
        return
        
    text = globals.TEXT_MY_TESTS_HEADER[lang_id]
    keyboard = []
    
    for i, t in enumerate(tests, 1):
        title = str(t.get("title", "Test"))
        amount = t.get("amount", 0)
        test_id = t.get("test_id", "")
        if lang_id == 2:
            text += f'\n{i}. 📌 <b>{title}</b> — <i>{amount} вопросов</i>'
        elif lang_id == 3:
            text += f'\n{i}. 📌 <b>{title}</b> — <i>{amount} questions</i>'
        else:
            text += f'\n{i}. 📌 <b>{title}</b> — <i>{amount} ta savol</i>'
        keyboard.append([InlineKeyboardButton(title, callback_data=f'mytest_{test_id}')])
    keyboard.append([InlineKeyboardButton(globals.BTN_SETTINGS_BACK[lang_id], callback_data='settings_back')])
    keyboard.append([InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        update.callback_query.edit_message_text(
            text=text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

def handle_mytest_callback(update, context):
    query = update.callback_query
    query.answer()
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    test_id = query.data.split('_', 1)[1]
    test_meta = db.get_test_meta(test_id)
    
    if not test_meta:
        return
        
    creator = db.get_user_by_chat_id(test_meta.get('chat_id', chat_id))
    creator_name = f"{creator.get('first_name', '')} {creator.get('last_name', '')}".strip() if creator else "Admin"
    
    time_per_q = test_meta.get("time_per_q", 0)
    amount = test_meta.get("amount", 0)
    total_seconds = time_per_q * amount
    
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    time_parts = []
    if hours > 0: time_parts.append(f"{hours} {globals.HOUR[lang_id]}")
    if minutes > 0: time_parts.append(f"{minutes} {globals.MINUTE[lang_id]}")
    if seconds > 0 or total_seconds == 0: time_parts.append(f"{seconds} {globals.SECOND[lang_id]}")
    time_text = " ".join(time_parts)
    
    info_text = globals.get_deeplink_test_info(
        lang_id, 
        test_meta.get('title', ''), 
        test_meta.get('description', ''), 
        amount, 
        time_text, 
        creator_name, 
        test_meta.get('point_per_q', 0)
    )
    
    bot_username = context.bot.username
    link = f'https://t.me/{bot_username}?start={chat_id}_{test_id}'
    if lang_id == 2: share_text = "Пройдите этот тест!"
    elif lang_id == 3: share_text = "Take this test!"
    else: share_text = "Ushbu testni ishlashni tavsiya qilaman!"
        
    share_url = f'https://t.me/share/url?url={link}&text={share_text}'
    group_url = f'https://t.me/{bot_username}?startgroup={chat_id}_{test_id}'
    
    keyboard = [
        [InlineKeyboardButton(globals.BTN_SHARE[lang_id], url=share_url)],
        [InlineKeyboardButton(globals.BTN_WORK_GROUP[lang_id], url=group_url)],
        [
            InlineKeyboardButton(globals.BTN_EDIT_TEST[lang_id], callback_data=f'edit_test_{test_id}'),
            InlineKeyboardButton(globals.BTN_DELETE_TEST[lang_id], callback_data=f'del_test_{test_id}')
        ],
        [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='mytests_list_back')],
        [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        text=info_text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

def handle_delete_test(update, context):
    query = update.callback_query
    query.answer()
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    test_id = query.data.split('_', 2)[2]
    db.delete_test_meta(test_id)
    
    context.bot.send_message(
        chat_id=chat_id,
        text=globals.TEXT_TEST_DELETED[lang_id],
        parse_mode='HTML'
    )
    
    show_my_tests(update, context)
