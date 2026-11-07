import globals
from database import Database
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

db = Database("tg_bot.db")

def show_edit_menu(update, context, test_id):
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    test_meta = db.get_test_meta(test_id)
    if not test_meta:
        return
    
    context.user_data["state"] = globals.STATES["menu"]
        
    keyboard = [
        [InlineKeyboardButton(globals.BTN_EDIT_TITLE[lang_id], callback_data=f'edtt_{test_id}')],
        [InlineKeyboardButton(globals.BTN_EDIT_DESC[lang_id], callback_data=f'edtd_{test_id}')],
        [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data=f'mytest_{test_id}')],
        [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = globals.TEXT_EDIT_MENU[lang_id]
    
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

def handle_edit_callback(update, context):
    query = update.callback_query
    try:
        query.answer()
    except Exception:
        pass
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    data = query.data
    
    if data.startswith('edtt_'):
        test_id = data.split('_', 1)[1]
        context.user_data['edit_test_id'] = test_id
        context.user_data["state"] = globals.STATES["edit_test_title"]
        
        keyboard = [
            [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data=f'edit_test_{test_id}')],
            [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
        ]
        
        query.edit_message_text(
            text=globals.TEXT_ENTER_NEW_TITLE[lang_id],
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
    elif data.startswith('edtd_'):
        test_id = data.split('_', 1)[1]
        context.user_data['edit_test_id'] = test_id
        context.user_data["state"] = globals.STATES["edit_test_desc"]
        
        keyboard = [
            [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data=f'edit_test_{test_id}')],
            [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
        ]
        
        query.edit_message_text(
            text=globals.TEXT_ENTER_NEW_DESC[lang_id],
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

def handle_edit_input(update, context):
    chat_id = update.effective_user.id
    text = update.message.text
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    state = context.user_data.get("state")
    
    test_id = context.user_data.get('edit_test_id')
    if not test_id:
        return
        
    if state == globals.STATES["edit_test_title"]:
        db.update_test_meta(test_id, "title", text)
        context.bot.send_message(
            chat_id=chat_id,
            text=globals.TEXT_TITLE_UPDATED[lang_id],
            parse_mode='HTML'
        )
    elif state == globals.STATES["edit_test_desc"]:
        db.update_test_meta(test_id, "description", text)
        context.bot.send_message(
            chat_id=chat_id,
            text=globals.TEXT_DESC_UPDATED[lang_id],
            parse_mode='HTML'
        )
        
    context.user_data["state"] = globals.STATES["menu"]
    try:
        from methods import send_main_menu
        send_main_menu(context, chat_id, lang_id)
    except ImportError:
        pass
