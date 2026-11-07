from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButtonPollType
from telegram.ext import ConversationHandler, MessageHandler, CommandHandler, Filters
import uuid
import json
import os
import globals
from database import Database

db = Database("tg_bot.db")

SARLAVHA, TAVSIF, FAYL_KUTISH, POLL_KUTISH = range(4)


def start_conversation(update, context):
    db_user = db.get_user_by_chat_id(update.effective_user.id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    update.message.reply_text(globals.CREATE_TEST_START[lang_id], parse_mode='HTML')
    return SARLAVHA


def get_title(update, context):
    db_user = db.get_user_by_chat_id(update.effective_user.id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    context.user_data["tittle"] = update.message.text
    buttons = ReplyKeyboardMarkup(
        [[KeyboardButton(text=globals.BTN_SKIP[lang_id])]],
        resize_keyboard=True, one_time_keyboard=True
    )
    update.message.reply_text(
        text=globals.CREATE_TEST_DESC[lang_id],
        reply_markup=buttons, parse_mode="HTML"
    )
    return TAVSIF


def get_description(update, context):
    db_user = db.get_user_by_chat_id(update.effective_user.id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    context.user_data["description"] = update.message.text
    context.user_data["temp_time_limit"] = 10
    
    text = globals.TEXT_CREATE_TIME_LIMIT.get(lang_id, globals.TEXT_CREATE_TIME_LIMIT[1])
    time_str = globals.TEXT_CREATE_TIME_SEC.get(lang_id, globals.TEXT_CREATE_TIME_SEC[1]).format(10)
    btn_save = globals.BTN_SAVE_NEXT.get(lang_id, globals.BTN_SAVE_NEXT[1])
    
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➖", callback_data="time_minus"),
            InlineKeyboardButton(time_str, callback_data="time_current"),
            InlineKeyboardButton("➕", callback_data="time_plus")
        ],
        [InlineKeyboardButton(btn_save, callback_data="time_save")]
    ])
    update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
    return 4


def get_document(update, context):
    db_user = db.get_user_by_chat_id(update.effective_user.id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1

    if update.message.text in (globals.BTN_FINISH_TEST[1], globals.BTN_FINISH_TEST[2], globals.BTN_FINISH_TEST[3]):
        return testni_yakunlash_qadami(update, context)

    if update.message.photo:
        context.user_data["temp_media"] = update.message.photo[-1].file_id
    elif update.message.document:
        context.user_data["temp_media"] = update.message.document.file_id
    else:
        context.user_data["temp_media"] = None

    buttons = ReplyKeyboardMarkup(
        [[KeyboardButton(text=globals.BTN_CREATE_TEST[lang_id], request_poll=KeyboardButtonPollType(type='quiz'))]],
        resize_keyboard=True, one_time_keyboard=True
    )
    update.message.reply_text(globals.CREATE_TEST_POLL[lang_id], reply_markup=buttons, parse_mode="HTML")
    return POLL_KUTISH


def testni_qabul_qilish(update, context):
    db_user = db.get_user_by_chat_id(update.effective_user.id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    poll = update.message.poll

    if not poll:
        update.message.reply_text(globals.ERR_USE_BUTTON_TEST[lang_id], parse_mode="HTML")
        return POLL_KUTISH
    if poll.type != "quiz" or len(poll.options) < 2:
        update.message.reply_text(globals.ERR_NEED_QUIZ[lang_id], parse_mode="HTML")
        return POLL_KUTISH

    if "vaqtinchalik_testlar" not in context.user_data:
        context.user_data["vaqtinchalik_testlar"] = []

    context.user_data["vaqtinchalik_testlar"].append({
        "poll": poll, "media_id": context.user_data.get("temp_media"),
        "explanation": poll.explanation if hasattr(poll, 'explanation') and poll.explanation else None
    })

    n = len(context.user_data["vaqtinchalik_testlar"])
    test_name = context.user_data.get("tittle", "Nomsiz test")
    text = globals.get_test_added_text(lang_id, test_name, n)

    buttons = ReplyKeyboardMarkup([
        [KeyboardButton(text=globals.BTN_SKIP_ARROW[lang_id])],
        [KeyboardButton(text=globals.BTN_FINISH_TEST[lang_id])]
    ], resize_keyboard=True)
    update.message.reply_text(text, parse_mode="HTML", reply_markup=buttons)
    return FAYL_KUTISH


def save_user_test_to_json(chat_id, telegram_polls):
    file_path = f"json_files/{chat_id}.json"
    unikal_kod = uuid.uuid4().hex[:8]
    test_id = f"test_{unikal_kod}"

    eski_baza = []
    oxirgi_id = 0
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                eski_baza = json.load(f)
                if eski_baza:
                    oxirgi_id = eski_baza[-1].get("id", 0)
            except json.JSONDecodeError:
                eski_baza = []

    harflar = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    yangi_savollar = []

    for indeks, item in enumerate(telegram_polls):
        poll = item["poll"] if isinstance(item, dict) and "poll" in item else item
        media_id = item.get("media_id") if isinstance(item, dict) else None

        if isinstance(poll, dict):
            options = poll.get("options", [])
            question = poll.get("question", "")
            correct_id = poll.get("correct_option_id", 0)
        else:
            options, question, correct_id = poll.options, poll.question, poll.correct_option_id

        oxirgi_id += 1
        variantlar = {}
        for i, option in enumerate(options):
            text = option.get("text", "") if isinstance(option, dict) else option.text
            variantlar[harflar[i]] = text

        savol = {"id": oxirgi_id, "savol": question, "variantlar": variantlar, "javob": harflar[correct_id]}
        explanation = item.get("explanation") if isinstance(item, dict) else None
        if explanation:
            savol["explanation"] = explanation
        if media_id:
            savol["media_id"] = media_id
        if indeks == 0:
            savol["test_id"] = test_id
        yangi_savollar.append(savol)

    eski_baza.extend(yangi_savollar)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(eski_baza, f, indent=4, ensure_ascii=False)
    return test_id


def testni_yakunlash_qadami(update, context):
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    yigilgan = context.user_data.get("vaqtinchalik_testlar", [])

    if not yigilgan:
        update.message.reply_text(globals.ERR_NO_QUESTIONS[lang_id], parse_mode="HTML")
        return ConversationHandler.END

    test_id = save_user_test_to_json(chat_id, yigilgan)
    title = context.user_data.get("tittle", "Nomsiz test")
    desc = context.user_data.get("description", "")
    amount = len(yigilgan)
    time_limit = context.user_data.get("temp_time_limit", 10)

    # ── Test meta saqlash ──
    db.save_test_meta(test_id, chat_id, title, desc, amount, 1, time_limit)
    
    # Kategoriyani saqlash (agar tanlangan bo'lsa)
    category_id = context.user_data.get("temp_category_id", 0)
    if category_id:
        db.update_test_category(test_id, category_id)

    # ── Yaratuvchi nomi ──
    creator_name = f'<a href="tg://user?id={chat_id}">{db_user.get("first_name", "")} {db_user.get("last_name", "")}</a>'

    bot_username = context.bot.username
    link = f"https://t.me/{bot_username}?start={chat_id}_{test_id}"
    share_text = globals.get_share_link_text(lang_id)
    ulashish_linki = f"https://t.me/share/url?url={link}&text={share_text}"
    guruh_linki = f"https://t.me/{bot_username}?startgroup={chat_id}_{test_id}"

    inline_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=globals.BTN_SHARE[lang_id], url=ulashish_linki)],
        [InlineKeyboardButton(text=globals.BTN_WORK_GROUP[lang_id], url=guruh_linki)],
        [
            InlineKeyboardButton(text=globals.BTN_EDIT_TEST[lang_id], callback_data=f"edit_test_{test_id}"),
            InlineKeyboardButton(text=globals.BTN_MY_TESTS[lang_id], callback_data="my_tests")
        ],
        [InlineKeyboardButton(text=globals.BTN_HOME[lang_id], callback_data="home")]
    ])

    update.message.reply_text(
        globals.get_test_saved_text(lang_id, test_id, title, amount, creator_name),
        parse_mode="HTML", reply_markup=inline_buttons
    )
    context.user_data.clear()
    return ConversationHandler.END


def cancel(update, context):
    db_user = db.get_user_by_chat_id(update.effective_user.id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    update.message.reply_text(text=globals.CREATE_CANCELLED[lang_id], parse_mode='HTML')
    return ConversationHandler.END


from telegram.ext import CallbackQueryHandler

def time_limit_callback(update, context):
    query = update.callback_query
    query.answer()
    data = query.data
    current = context.user_data.get("temp_time_limit", 10)
    
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    
    if data == "time_minus":
        current = max(10, current - 10)
    elif data == "time_plus":
        current = min(1800, current + 10)
    elif data == "time_save":
        query.message.delete()
        buttons = ReplyKeyboardMarkup(
            [[KeyboardButton(text=globals.BTN_NO_PHOTO[lang_id])]],
            resize_keyboard=True, one_time_keyboard=True
        )
        context.bot.send_message(
            chat_id=chat_id,
            text=globals.CREATE_TEST_Q1[lang_id],
            reply_markup=buttons, parse_mode="HTML"
        )
        return FAYL_KUTISH
        
    context.user_data["temp_time_limit"] = current
    
    if current < 60:
        display_time = globals.TEXT_CREATE_TIME_SEC.get(lang_id, globals.TEXT_CREATE_TIME_SEC[1]).format(current)
    else:
        display_time = globals.TEXT_CREATE_TIME_MIN_SEC.get(lang_id, globals.TEXT_CREATE_TIME_MIN_SEC[1]).format(current//60, current%60)
        
    btn_save = globals.BTN_SAVE_NEXT.get(lang_id, globals.BTN_SAVE_NEXT[1])
    
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➖", callback_data="time_minus"),
            InlineKeyboardButton(display_time, callback_data="time_current"),
            InlineKeyboardButton("➕", callback_data="time_plus")
        ],
        [InlineKeyboardButton(btn_save, callback_data="time_save")]
    ])
    try:
        query.edit_message_reply_markup(reply_markup=reply_markup)
    except:
        pass
    return 4

def skip_time_msg(update, context):
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    update.message.reply_text(globals.TEXT_TIME_LIMIT_SKIP.get(lang_id, globals.TEXT_TIME_LIMIT_SKIP[1]))
    return 4

def conv_handler():
    from telegram.ext import CallbackQueryHandler
    regex_pattern = f'^({globals.BTN_CREATE_TEST[1]}|{globals.BTN_CREATE_TEST[2]}|{globals.BTN_CREATE_TEST[3]})$'
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(regex_pattern), start_conversation)],
        states={
            SARLAVHA: [MessageHandler(Filters.text & ~Filters.command, get_title)],
            TAVSIF: [MessageHandler(Filters.text & ~Filters.command, get_description)],
            4: [
                CallbackQueryHandler(time_limit_callback, pattern='^time_'),
                MessageHandler(Filters.text & ~Filters.command, skip_time_msg)
            ],
            FAYL_KUTISH: [MessageHandler((Filters.photo | Filters.document | Filters.text) & ~Filters.command, get_document)],
            POLL_KUTISH: [MessageHandler(Filters.poll | Filters.text & ~Filters.command, testni_qabul_qilish)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )