import globals
from database import Database
from config import ADMIN_ID
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

db = Database("tg_bot.db")

def start_feedback(update, context):
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    context.user_data["state"] = globals.STATES["feedback"]
    
    keyboard = [[globals.BTN_BACK[lang_id]]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    context.bot.send_message(
        chat_id=chat_id,
        text=globals.TEXT_FEEDBACK_PROMPT[lang_id],
        parse_mode='HTML',
        reply_markup=reply_markup
    )

def handle_feedback_input(update, context):
    chat_id = update.effective_user.id
    text = update.message.text
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    if text == globals.BTN_BACK[lang_id]:
        context.user_data["state"] = globals.STATES["menu"]
        try:
            from methods import send_main_menu
            send_main_menu(context, chat_id, lang_id)
        except ImportError:
            pass
        return

    db.save_feedback(chat_id, text)
    
    context.bot.send_message(
        chat_id=chat_id,
        text=globals.TEXT_FEEDBACK_SENT[lang_id],
        parse_mode='HTML'
    )
    
    first_name = db_user.get("first_name", "")
    last_name = db_user.get("last_name", "")
    phone = db_user.get("phone_number", "")
    
    admin_msg = (f'<b>💬 Yangi fikr!</b>\n\n'
                 f'<b>👤 Foydalanuvchi:</b> <a href="tg://user?id={chat_id}">{first_name} {last_name}</a>\n'
                 f'<b>📱 Tel:</b> <i>{phone}</i>\n\n'
                 f'<b>💬 Xabar:</b>\n<i>{text}</i>')
    
    reply_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Javob yozish", callback_data=f"admin_reply_{chat_id}")]
    ])
    
    try:
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_msg,
            parse_mode='HTML',
            reply_markup=reply_kb
        )
    except Exception:
        pass
        
    context.user_data["state"] = globals.STATES["menu"]
    try:
        from methods import send_main_menu
        send_main_menu(context, chat_id, lang_id)
    except ImportError:
        pass
