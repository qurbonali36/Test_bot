from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
import globals


def send_main_menu(context, chat_id, lang_id, message_id=None):
    buttons = [
        [KeyboardButton(text=globals.BTN_TEST_WORKING[lang_id]), KeyboardButton(text=globals.BTN_DAILY[lang_id])],
        [KeyboardButton(text=globals.BTN_CREATE_TEST[lang_id]), KeyboardButton(text=globals.BTN_CREATE_WIZARD[lang_id])],
        [KeyboardButton(text=globals.BTN_LEADERBOARD[lang_id]), KeyboardButton(text=globals.BTN_DUEL[lang_id])],
        [KeyboardButton(text=globals.MENU_MISSIONS[lang_id]), KeyboardButton(text=globals.MENU_TOURNAMENT[lang_id])],
        [KeyboardButton(text=globals.MENU_FRIENDS[lang_id]), KeyboardButton(text=globals.SPACED_REP_TITLE[lang_id])],
        [KeyboardButton(text=globals.BTN_PROFILE[lang_id]), KeyboardButton(text=globals.BTN_HISTORY[lang_id])],
        [KeyboardButton(text=globals.BTN_BOOKMARKS[lang_id]), KeyboardButton(text=globals.BTN_NOTIFICATIONS[lang_id])],
        [KeyboardButton(text=globals.BTN_HELP[lang_id]), KeyboardButton(text=globals.BTN_COMMENTS[lang_id])],
        [KeyboardButton(text=globals.BTN_SETTINGS[lang_id]), KeyboardButton(text=globals.BTN_GUIDE[lang_id])],
        [KeyboardButton(text=globals.BTN_SEARCH[lang_id]), KeyboardButton(text=globals.BTN_CHECK_CERT[lang_id])]
    ]
    if message_id:
        try:
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            pass
            
    context.bot.send_message(
        chat_id=chat_id,
        text=globals.TEXT_MAIN_MENU[lang_id],
        reply_markup=ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )
    )

def send_admin_menu(context, chat_id, lang_id):
    buttons = [
        [KeyboardButton(text=globals.BTN_ADMIN_MONITORING[lang_id])],
        [KeyboardButton(text=globals.BTN_ADMIN_USERS[lang_id]), KeyboardButton(text=globals.BTN_ADMIN_FEEDBACKS[lang_id])],
        [KeyboardButton(text=globals.BTN_ADMIN_BROADCAST[lang_id]), KeyboardButton(text=globals.BTN_ADMIN_CLEAR_CACHE[lang_id])],
        [KeyboardButton(text=globals.BTN_ADMIN_NORMAL_MODE[lang_id]), KeyboardButton(text=globals.BTN_SETTINGS[lang_id])]
    ]
    text = globals.TEXT_ADMIN_MENU[lang_id]
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )
    )