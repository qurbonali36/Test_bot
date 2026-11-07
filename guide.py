from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from database import Database
from globals import *
from config import ADMIN_ID

db = Database("tg_bot.db")

def show_guide(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    
    text = get_guide_text(lang_id)
    
    keyboard = [
        [InlineKeyboardButton(BTN_CONTACT_ADMIN[lang_id], callback_data='contact_admin')],
        [InlineKeyboardButton(BTN_BACK[lang_id], callback_data='back')],
        [InlineKeyboardButton(BTN_HOME[lang_id], callback_data='home')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')

def handle_guide_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == 'contact_admin':
        from feedback import start_feedback
        query.message.delete()
        start_feedback(update, context)
