import globals
from database import Database
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

db = Database("tg_bot.db")


def start_practice(update, context):
    """Xato javoblardan mini-test tuzish."""
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    wrongs = db.get_wrong_answers(chat_id, 50)
    if not wrongs or len(wrongs) < 2:
        text = globals.TEXT_PRACTICE_NO_DATA[lang_id]
        keyboard = [[InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]]
        if update.callback_query:
            update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            context.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    import random
    selected = random.sample(wrongs, min(len(wrongs), 10))

    # Savollarni quiz formatiga o'girish
    questions = []
    harflar = ["A", "B", "C", "D"]
    for i, w in enumerate(selected):
        correct = w.get('correct_answer', '')
        wrong = w.get('user_answer', '')
        q_text = w.get('question', f'Savol {i+1}')

        options = [correct]
        if wrong and wrong != correct:
            options.append(wrong)
        # Kamida 2 ta variant bo'lishi kerak
        while len(options) < 2:
            options.append("---")

        random.shuffle(options)
        variantlar = {}
        for j, opt in enumerate(options):
            variantlar[harflar[j]] = opt

        javob_index = options.index(correct)
        questions.append({
            "id": i + 1,
            "savol": q_text,
            "variantlar": variantlar,
            "javob": harflar[javob_index]
        })

    # Test ma'lumotlarini o'rnatish
    context.user_data['savollar_bazasi'] = questions
    context.user_data['amount_quest'] = len(questions)
    context.user_data['current_quest'] = 0
    context.user_data['correct_ans'] = 0
    context.user_data['speed_bonus'] = 0
    context.user_data['chat_id'] = chat_id
    context.user_data['test_id'] = 'practice_mistakes'
    name = update.effective_user.first_name
    context.user_data['name_link'] = f'<a href="tg://user?id={chat_id}">{name}</a>'

    text = globals.TEXT_PRACTICE_START[lang_id].format(count=len(questions))
    if update.callback_query:
        update.callback_query.edit_message_text(text, parse_mode='HTML')
    else:
        context.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')

    import time
    time.sleep(2)

    from quest_poll import send_polls
    send_polls(context)
