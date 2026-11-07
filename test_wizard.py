from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, Filters
from database import Database
import globals
import re

db = Database("tg_bot.db")

W_TITLE, W_DESC, W_TIME, W_QUESTION, W_OPTIONS, W_CORRECT = range(10, 16)

def start_wizard(update, context):
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    context.user_data["w_questions"] = []
    
    msg = globals.WIZARD_ENTER_NAME.get(lang_id, globals.WIZARD_ENTER_NAME[1])
    buttons = ReplyKeyboardMarkup([[KeyboardButton(text=globals.BTN_CANCEL[lang_id])]], resize_keyboard=True)
    
    update.message.reply_text(msg, reply_markup=buttons, parse_mode="HTML")
    return W_TITLE

def get_w_title(update, context):
    text = update.message.text
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    if text == globals.BTN_CANCEL[lang_id]:
        update.message.reply_text(globals.TEST_CANCELLED[lang_id], reply_markup=ReplyKeyboardMarkup([[KeyboardButton(globals.BTN_HOME[lang_id])]], resize_keyboard=True))
        return ConversationHandler.END
        
    context.user_data["w_title"] = text
    
    msg = globals.CREATE_TEST_DESC.get(lang_id, globals.CREATE_TEST_DESC[1])
    buttons = ReplyKeyboardMarkup([[KeyboardButton(text=globals.BTN_SKIP[lang_id])], [KeyboardButton(text=globals.BTN_CANCEL[lang_id])]], resize_keyboard=True)
    
    update.message.reply_text(msg, reply_markup=buttons, parse_mode="HTML")
    return W_DESC

def get_w_desc(update, context):
    text = update.message.text
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    if text == globals.BTN_CANCEL[lang_id]:
        update.message.reply_text(globals.TEST_CANCELLED[lang_id], reply_markup=ReplyKeyboardMarkup([[KeyboardButton(globals.BTN_HOME[lang_id])]], resize_keyboard=True))
        return ConversationHandler.END
        
    if text == globals.BTN_SKIP[lang_id]:
        text = "No description"
        
    context.user_data["w_desc"] = text
    context.user_data["w_time"] = 10
    
    msg = globals.TEXT_CREATE_TIME_LIMIT.get(lang_id, globals.TEXT_CREATE_TIME_LIMIT[1])
    time_str = globals.TEXT_CREATE_TIME_SEC.get(lang_id, globals.TEXT_CREATE_TIME_SEC[1]).format(10)
    btn_save = globals.BTN_SAVE_NEXT.get(lang_id, globals.BTN_SAVE_NEXT[1])
    
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➖", callback_data="wtime_minus"),
            InlineKeyboardButton(time_str, callback_data="wtime_current"),
            InlineKeyboardButton("➕", callback_data="wtime_plus")
        ],
        [InlineKeyboardButton(btn_save, callback_data="wtime_save")]
    ])
    
    update.message.reply_text(msg, reply_markup=reply_markup, parse_mode="HTML")
    return W_TIME

def w_time_callback(update, context):
    query = update.callback_query
    query.answer()
    data = query.data
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    current = context.user_data.get("w_time", 10)
    
    if data == "wtime_minus":
        current = max(10, current - 10)
        context.user_data["w_time"] = current
        time_str = globals.TEXT_CREATE_TIME_SEC.get(lang_id, globals.TEXT_CREATE_TIME_SEC[1]).format(current)
        btn_save = globals.BTN_SAVE_NEXT.get(lang_id, globals.BTN_SAVE_NEXT[1])
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("➖", callback_data="wtime_minus"), InlineKeyboardButton(time_str, callback_data="wtime_current"), InlineKeyboardButton("➕", callback_data="wtime_plus")],
            [InlineKeyboardButton(btn_save, callback_data="wtime_save")]
        ])
        query.edit_message_reply_markup(reply_markup)
        
    elif data == "wtime_plus":
        current = min(1800, current + 10)
        context.user_data["w_time"] = current
        time_str = globals.TEXT_CREATE_TIME_SEC.get(lang_id, globals.TEXT_CREATE_TIME_SEC[1]).format(current)
        btn_save = globals.BTN_SAVE_NEXT.get(lang_id, globals.BTN_SAVE_NEXT[1])
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("➖", callback_data="wtime_minus"), InlineKeyboardButton(time_str, callback_data="wtime_current"), InlineKeyboardButton("➕", callback_data="wtime_plus")],
            [InlineKeyboardButton(btn_save, callback_data="wtime_save")]
        ])
        query.edit_message_reply_markup(reply_markup)
        
    elif data == "wtime_save":
        query.message.delete()
        ask_question(context, chat_id, lang_id)
        return W_QUESTION
        
    return W_TIME

def ask_question(context, chat_id, lang_id):
    num = len(context.user_data.get("w_questions", [])) + 1
    msg = globals.WIZARD_ENTER_Q.get(lang_id, globals.WIZARD_ENTER_Q[1]).format(num=num)
    buttons = ReplyKeyboardMarkup([[KeyboardButton(text=globals.BTN_FINISH_TEST.get(lang_id, "Yakunlash"))], [KeyboardButton(text=globals.BTN_CANCEL[lang_id])]], resize_keyboard=True)
    context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=buttons, parse_mode="HTML")

def get_w_question(update, context):
    text = update.message.text
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    if text == globals.BTN_CANCEL[lang_id]:
        update.message.reply_text(globals.TEST_CANCELLED[lang_id], reply_markup=ReplyKeyboardMarkup([[KeyboardButton(globals.BTN_HOME[lang_id])]], resize_keyboard=True))
        return ConversationHandler.END
        
    if text == globals.BTN_FINISH_TEST.get(lang_id, "Yakunlash"):
        return save_wizard_test(update, context, chat_id, lang_id)
        
    context.user_data["current_w_q"] = text
    msg = globals.WIZARD_ENTER_OPTIONS.get(lang_id, globals.WIZARD_ENTER_OPTIONS[1])
    update.message.reply_text(msg, parse_mode="HTML")
    return W_OPTIONS

def get_w_options(update, context):
    text = update.message.text
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    if text == globals.BTN_CANCEL[lang_id]:
        update.message.reply_text(globals.TEST_CANCELLED[lang_id], reply_markup=ReplyKeyboardMarkup([[KeyboardButton(globals.BTN_HOME[lang_id])]], resize_keyboard=True))
        return ConversationHandler.END
        
    options = [opt.strip() for opt in text.split(",") if opt.strip()]
    if len(options) < 2:
        update.message.reply_text("Kamida 2 ta variant kiriting, vergul bilan ajratib (masalan: A, B, C, D):")
        return W_OPTIONS
        
    context.user_data["current_w_opts"] = options
    
    msg = globals.WIZARD_CHOOSE_CORRECT.get(lang_id, globals.WIZARD_CHOOSE_CORRECT[1])
    kb = []
    for idx, opt in enumerate(options):
        kb.append([InlineKeyboardButton(text=opt, callback_data=f"wcorr_{idx}")])
        
    update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    return W_CORRECT

def w_correct_callback(update, context):
    query = update.callback_query
    query.answer()
    data = query.data
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    if data.startswith("wcorr_"):
        correct_idx = int(data.split("_")[1])
        question = context.user_data["current_w_q"]
        options = context.user_data["current_w_opts"]
        
        context.user_data["w_questions"].append({
            "question": question,
            "options": options,
            "correct_option_id": correct_idx
        })
        
        query.edit_message_text(f"✅ Saqlandi! Jami savollar: {len(context.user_data['w_questions'])}")
        ask_question(context, chat_id, lang_id)
        return W_QUESTION

def save_wizard_test(update, context, chat_id, lang_id):
    questions = context.user_data.get("w_questions", [])
    if len(questions) < 1:
        update.message.reply_text("Testda kamida 1 ta savol bo'lishi kerak!", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(globals.BTN_HOME[lang_id])]], resize_keyboard=True))
        return ConversationHandler.END
        
    title = context.user_data.get("w_title", "Nomsiz")
    desc = context.user_data.get("w_desc", "")
    time_limit = context.user_data.get("w_time", 10)
    
    # Generate unique test ID
    import random
    test_id = str(random.randint(100000, 999999))
    while db.get_test_meta(test_id):
        test_id = str(random.randint(100000, 999999))
        
    # Save to JSON
    import json
    import os
    formatted_polls = []
    for q in questions:
        formatted_polls.append({
            "question": q["question"],
            "options": q["options"],
            "correct_option_id": q["correct_option_id"],
            "type": "quiz"
        })
        
    os.makedirs("tests", exist_ok=True)
    with open(f"tests/{test_id}.json", "w", encoding="utf-8") as f:
        json.dump(formatted_polls, f, ensure_ascii=False, indent=4)
        
    # Save meta to DB
    db.save_test_meta(test_id, chat_id, title, desc, len(questions), time_limit)
    
    # Generate deep link
    link = f"https://t.me/{context.bot.username}?start={chat_id}_{test_id}"
    
    msg = globals.get_test_saved_text(lang_id, test_id, title, len(questions), "You")
    msg += f"\\n\\n🔗 Link: {link}"
    
    update.message.reply_text(msg, parse_mode="HTML", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(globals.BTN_HOME[lang_id])]], resize_keyboard=True))
    
    return ConversationHandler.END

def cancel_wizard(update, context):
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    update.message.reply_text(globals.TEST_CANCELLED[lang_id], reply_markup=ReplyKeyboardMarkup([[KeyboardButton(globals.BTN_HOME[lang_id])]], resize_keyboard=True))
    return ConversationHandler.END

def get_wizard_handler():
    regex_pattern = f'^({globals.BTN_CREATE_WIZARD[1]}|{globals.BTN_CREATE_WIZARD[2]}|{globals.BTN_CREATE_WIZARD[3]})$'
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(regex_pattern), start_wizard)],
        states={
            W_TITLE: [MessageHandler(Filters.text & ~Filters.command, get_w_title)],
            W_DESC: [MessageHandler(Filters.text & ~Filters.command, get_w_desc)],
            W_TIME: [
                CallbackQueryHandler(w_time_callback, pattern='^wtime_'),
                MessageHandler(Filters.text & ~Filters.command, w_time_callback)
            ],
            W_QUESTION: [MessageHandler(Filters.text & ~Filters.command, get_w_question)],
            W_OPTIONS: [MessageHandler(Filters.text & ~Filters.command, get_w_options)],
            W_CORRECT: [CallbackQueryHandler(w_correct_callback, pattern='^wcorr_')]
        },
        fallbacks=[CommandHandler('cancel', cancel_wizard)],
        per_message=False
    )
