import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from database import Database
from globals import *
from methods import send_main_menu
from my_tests import show_my_tests

db = Database("tg_bot.db")

def show_settings(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    
    keyboard = [
        [InlineKeyboardButton(BTN_CHANGE_NAME[lang_id], callback_data='set_name'), 
         InlineKeyboardButton(BTN_CHANGE_LASTNAME[lang_id], callback_data='set_lastname')],
        [InlineKeyboardButton(BTN_CHANGE_PHONE[lang_id], callback_data='set_phone'),
         InlineKeyboardButton(BTN_CHANGE_LANG[lang_id], callback_data='set_lang')],
        [InlineKeyboardButton(BTN_STATISTICS[lang_id], callback_data='set_stats')],
        [InlineKeyboardButton(BTN_MY_TESTS[lang_id], callback_data='my_tests')],
        [InlineKeyboardButton(BTN_HOME[lang_id], callback_data='home')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = TEXT_SETTINGS_MENU[lang_id]
    
    if update.message:
        try:
            update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
        except Exception as e:
            update.message.reply_text(f"Error: {e}")
    else:
        try:
            update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
        except Exception as e:
            update.callback_query.message.reply_text(f"Error in edit_message_text: {e}")

def handle_settings_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    try:
        query.answer()
    except Exception:
        pass
    chat_id = update.effective_chat.id
    data = query.data
    
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    
    back_home_kb = [
        [InlineKeyboardButton(BTN_SETTINGS_BACK[lang_id], callback_data='settings_back')],
        [InlineKeyboardButton(BTN_HOME[lang_id], callback_data='home')]
    ]
    
    if data == 'set_name':
        context.user_data["state"] = STATES["edit_name"]
        query.edit_message_text(TEXT_ENTER_NEW_NAME[lang_id], reply_markup=InlineKeyboardMarkup(back_home_kb), parse_mode='HTML')
    elif data == 'set_lastname':
        context.user_data["state"] = STATES["edit_lastname"]
        query.edit_message_text(TEXT_ENTER_NEW_LASTNAME[lang_id], reply_markup=InlineKeyboardMarkup(back_home_kb), parse_mode='HTML')
    elif data == 'set_phone':
        context.user_data["state"] = STATES["edit_phone"]
        text = TEXT_ENTER_NEW_PHONE[lang_id]
        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_home_kb), parse_mode='HTML')
    elif data == 'set_lang':
        keyboard = [
            [InlineKeyboardButton(BTN_LANG_UZ, callback_data='lang_1')],
            [InlineKeyboardButton(BTN_LANG_RU, callback_data='lang_2')],
            [InlineKeyboardButton(BTN_LANG_EN, callback_data='lang_3')],
            [InlineKeyboardButton(BTN_SETTINGS_BACK[lang_id], callback_data='settings_back')],
            [InlineKeyboardButton(BTN_HOME[lang_id], callback_data='home')]
        ]
        text = TEXT_CHOOSE_LANG[lang_id]
        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    elif data == 'set_stats':
        stats = db.get_user_stats(chat_id)
        if not stats:
            query.edit_message_text(TEXT_NO_STATS[lang_id], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(back_home_kb))
        else:
            text = get_user_stats_text(lang_id, db_user.get('first_name', ''), db_user.get('last_name', ''), stats)
            query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(back_home_kb))
    elif data == 'settings_back':
        context.user_data["state"] = STATES["menu"]
        try:
            show_settings(update, context)
        except Exception as e:
            query.message.reply_text(f"Error calling show_settings: {e}")
    elif data == 'my_tests':
        show_my_tests(update, context)
    elif data.startswith('lang_'):
        new_lang = int(data.split('_')[1])
        db.update_user_data(chat_id, "lang_id", new_lang)
        query.answer(TEXT_LANG_UPDATED[new_lang], show_alert=True)
        query.message.delete()
        send_main_menu(context, chat_id, new_lang)

def handle_settings_input(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    text = update.message.text
    db_user = db.get_user_by_chat_id(chat_id)
    if not db_user:
        return
    
    lang_id = db_user.get("lang_id", 1)
    state = context.user_data.get("state", 0)
    
    if state == STATES["edit_name"]:
        db.update_user_data(chat_id, "first_name", text)
        context.user_data["state"] = STATES["menu"]
        update.message.reply_text(TEXT_NAME_UPDATED[lang_id], parse_mode='HTML')
        send_main_menu(context, chat_id, lang_id)
    elif state == STATES["edit_lastname"]:
        db.update_user_data(chat_id, "last_name", text)
        context.user_data["state"] = STATES["menu"]
        update.message.reply_text(TEXT_LASTNAME_UPDATED[lang_id], parse_mode='HTML')
        send_main_menu(context, chat_id, lang_id)
    elif state == STATES["edit_phone"]:
        db.update_user_data(chat_id, "phone_number", text)
        context.user_data["state"] = STATES["menu"]
        update.message.reply_text(TEXT_PHONE_UPDATED[lang_id], parse_mode='HTML')
        send_main_menu(context, chat_id, lang_id)
