import globals
from database import Database
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

db = Database("tg_bot.db")


def show_wrong_answers(update, context):
    """Xato javoblar ro'yxatini ko'rsatish."""
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    count = db.get_wrong_answers_count(chat_id)

    keyboard_btns = []
    if count > 0:
        keyboard_btns.append([InlineKeyboardButton(globals.BTN_PRACTICE_MISTAKES[lang_id], callback_data='practice_mistakes')])
        keyboard_btns.append([InlineKeyboardButton(globals.BTN_WRONG_CLEAR[lang_id], callback_data='wrong_clear')])
    keyboard_btns.append([InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='back')])
    keyboard_btns.append([InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')])
    reply_markup = InlineKeyboardMarkup(keyboard_btns)

    if count == 0:
        text = globals.TEXT_WRONG_TITLE[lang_id] + globals.TEXT_WRONG_EMPTY[lang_id]
    else:
        text = globals.TEXT_WRONG_TITLE[lang_id]
        text += globals.TEXT_WRONG_COUNT[lang_id].format(count=count)
        wrongs = db.get_wrong_answers(chat_id, 10)
        for i, w in enumerate(wrongs, 1):
            q = w.get('question', '???')
            correct = w.get('correct_answer', '???')
            user_a = w.get('user_answer', '???')
            text += f"<b>{i}.</b> {q}\n"
            text += f"   ✅ <i>{correct}</i>\n"
            text += f"   ❌ <s>{user_a}</s>\n\n"

    if update.message:
        update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
    elif update.callback_query:
        try:
            update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
        except:
            update.callback_query.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)


def handle_wrong_callback(update, context):
    """Xato javoblar callback."""
    query = update.callback_query
    query.answer()
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    data = query.data

    if data == 'wrong_clear':
        db.clear_wrong_answers(chat_id)
        query.edit_message_text(
            globals.TEXT_WRONG_CLEARED[lang_id],
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
            ])
        )
    elif data == 'wrong_ans':
        show_wrong_answers(update, context)
