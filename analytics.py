import globals
from database import Database
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

db = Database("tg_bot.db")


def show_analytics(update, context):
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    stats = db.get_user_analytics(chat_id)
    if not stats or stats.get('total_tests', 0) == 0:
        keyboard = [
            [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='back')],
            [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
        ]
        text = globals.TEXT_ANALYTICS_EMPTY[lang_id]
        if update.message:
            update.message.reply_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        elif update.callback_query:
            update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    rank = db.get_user_global_rank(chat_id)
    text = globals.TEXT_ANALYTICS_TITLE[lang_id].format(
        total_tests=stats['total_tests'],
        total_score=stats['total_score'],
        avg_accuracy=round(stats['avg_accuracy'], 1),
        best_accuracy=round(stats['best_accuracy'], 1),
        worst_accuracy=round(stats['worst_accuracy'], 1),
        rank=rank
    )

    # So'nggi natijalar va fanlar bo'yicha tahlil
    all_results = db.get_user_stats(chat_id)
    subject_stats = {}
    
    recent = []
    if all_results:
        recent = all_results[:5]
        for r in all_results:
            title = r.get('title') or globals.TEXT_ANALYTICS_UNKNOWN.get(lang_id, globals.TEXT_ANALYTICS_UNKNOWN[1])
            acc = r.get('precent_corr_ans', 0)
            if title not in subject_stats:
                subject_stats[title] = []
            subject_stats[title].append(acc)
            
    strong_subject = "-"
    weak_subject = "-"
    if subject_stats:
        avg_subjects = {k: sum(v)/len(v) for k, v in subject_stats.items()}
        strong_subject = max(avg_subjects, key=avg_subjects.get)
        weak_subject = min(avg_subjects, key=avg_subjects.get)
        if len(avg_subjects) == 1:
            weak_subject = "-" # agar faqat 1 ta fan bo'lsa
            
    text += f"{globals.TEXT_ANALYTICS_STRONG.get(lang_id, globals.TEXT_ANALYTICS_STRONG[1])} {strong_subject}\n"
    text += f"{globals.TEXT_ANALYTICS_WEAK.get(lang_id, globals.TEXT_ANALYTICS_WEAK[1])} {weak_subject}\n"
    text += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{globals.TEXT_ANALYTICS_RECENT.get(lang_id, globals.TEXT_ANALYTICS_RECENT[1])}\n"

    medals = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
    for i, r in enumerate(recent):
        icon = medals[i] if i < len(medals) else f"{i+1}."
        title = r.get('title') or 'Test'
        score = r.get('point_test', 0)
        acc = r.get('precent_corr_ans', 0)
        text += f"{icon} <b>{title}</b> — {score} ({acc}%)\n"

    keyboard = [
        [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='back')],
        [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
