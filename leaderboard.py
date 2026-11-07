import globals
from database import Database
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

db = Database("tg_bot.db")

MEDALS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


def show_leaderboard_menu(update, context):
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    keyboard = [
        [InlineKeyboardButton(globals.BTN_LB_GLOBAL[lang_id], callback_data='lb_global')],
        [InlineKeyboardButton(globals.BTN_LB_WEEKLY[lang_id], callback_data='lb_weekly')],
        [InlineKeyboardButton({1: "🌟 Mavsumiy Reyting", 2: "🌟 Сезонный Рейтинг", 3: "🌟 Seasonal Leaderboard"}[lang_id], callback_data='lb_seasonal')],
        [InlineKeyboardButton(globals.BTN_LB_TOP50[lang_id], callback_data='lb_top50')],
        [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='back')],
        [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = globals.TEXT_LEADERBOARD_TITLE[lang_id]

    if update.message:
        update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    elif update.callback_query:
        update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')


def handle_leaderboard_callback(update, context):
    query = update.callback_query
    query.answer()
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    data = query.data

    back_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='lb_menu')],
        [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
    ])

    if data == 'lb_menu':
        show_leaderboard_menu(update, context)
        return

    if data in ('lb_global', 'lb_top50'):
        limit = 50 if data == 'lb_top50' else 10
        users = db.get_global_leaderboard(limit)
        if not users:
            query.edit_message_text(globals.TEXT_LB_EMPTY[lang_id], reply_markup=back_kb, parse_mode='HTML')
            return
        title = "📋 <b>TOP 50</b>" if data == 'lb_top50' else globals.TEXT_LEADERBOARD_TITLE[lang_id]
        text = f"{title}\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for i, u in enumerate(users):
            medal = MEDALS[i] if i < len(MEDALS) else f"{i+1}."
            name = f"{u.get('first_name', '')} {u.get('last_name', '')}".strip()
            score = u.get('total_score', 0)
            tests = u.get('tests_count', 0)
            acc = round(u.get('avg_accuracy', 0), 1)
            level = u.get('level', 1) or 1
            lvl_emoji = globals.LEVEL_EMOJIS.get(level, "🌱")
            text += f"\n{medal} {lvl_emoji} <b>{name}</b>\n"
            text += f"    ├ 🏆 {score} ball | 📝 {tests} test\n"
            text += f"    └ 📈 {acc}%\n"
        rank = db.get_user_global_rank(chat_id)
        text += globals.TEXT_LB_YOUR_RANK[lang_id].format(rank=rank)
        query.edit_message_text(text, reply_markup=back_kb, parse_mode='HTML')

    elif data == 'lb_weekly':
        users = db.get_weekly_leaderboard(10)
        if not users:
            query.edit_message_text(globals.TEXT_LB_EMPTY[lang_id], reply_markup=back_kb, parse_mode='HTML')
            return
        text = globals.TEXT_LB_WEEKLY_TITLE[lang_id]
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for i, u in enumerate(users):
            medal = MEDALS[i] if i < len(MEDALS) else f"{i+1}."
            name = f"{u.get('first_name', '')} {u.get('last_name', '')}".strip()
            score = u.get('total_score', 0)
            text += f"{medal} <b>{name}</b> — {score} ball\n"
        rank = db.get_user_global_rank(chat_id)
        text += globals.TEXT_LB_YOUR_RANK[lang_id].format(rank=rank)
        query.edit_message_text(text, reply_markup=back_kb, parse_mode='HTML')

    elif data == 'lb_seasonal':
        season = db.get_active_season()
        if not season:
            query.edit_message_text({1: "🌟 Faol mavsum yo'q.", 2: "🌟 Нет активного сезона.", 3: "🌟 No active season."}[lang_id], reply_markup=back_kb, parse_mode='HTML')
            return
            
        users = db.get_seasonal_leaderboard(season["id"], 10)
        if not users:
            query.edit_message_text(globals.TEXT_LB_EMPTY[lang_id], reply_markup=back_kb, parse_mode='HTML')
            return
            
        lang_code = {1: 'uz', 2: 'ru', 3: 'en'}.get(lang_id, 'uz')
        season_name = season[f"name_{lang_code}"] or season["name_uz"]
        
        text = f"🌟 <b>{season_name} - Reyting</b>\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for i, u in enumerate(users):
            medal = MEDALS[i] if i < len(MEDALS) else f"{i+1}."
            name = f"{u.get('first_name', '')} {u.get('last_name', '')}".strip()
            score = u.get('score', 0)
            text += f"{medal} <b>{name}</b> — {score} XP\n"
            
        query.edit_message_text(text, reply_markup=back_kb, parse_mode='HTML')

