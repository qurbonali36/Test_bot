import globals
from database import Database
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

db = Database("tg_bot.db")


def get_xp_for_result(correct, total, percent):
    """Test natijasi uchun XP hisoblash."""
    base_xp = correct * 5
    if percent >= 100:
        base_xp += 50  # Perfect bonus
    elif percent >= 80:
        base_xp += 20
    elif percent >= 60:
        base_xp += 10
    return base_xp


def check_and_award_badges(chat_id, lang_id, context):
    """Yutuqlarni tekshirib, yangi badge berish."""
    db_user = db.get_user_by_chat_id(chat_id)
    stats = db.get_user_analytics(chat_id)
    xp_data = db.get_user_xp_level(chat_id)
    streak_data = db.get_user_streak(chat_id)
    messages = []

    if not stats:
        return messages

    total_tests = stats.get('total_tests', 0)
    best_acc = stats.get('best_accuracy', 0)
    level = xp_data.get('level', 1)
    streak = streak_data.get('current_streak', 0)

    badge_checks = [
        ('first_test', total_tests >= 1),
        ('perfect_100', best_acc >= 100),
        ('streak_7', streak >= 7),
        ('streak_30', streak >= 30),
        ('tests_10', total_tests >= 10),
        ('tests_50', total_tests >= 50),
        ('level_5', level >= 5),
        ('level_10', level >= 10),
    ]

    for badge_key, condition in badge_checks:
        if condition:
            awarded = db.add_user_badge(chat_id, badge_key)
            if awarded:
                badge_name = globals.BADGE_NAMES.get(badge_key, {}).get(lang_id, badge_key)
                messages.append(f"🏅 Yangi yutuq: <b>{badge_name}</b>!")

    return messages


def show_profile(update, context):
    """Foydalanuvchi profilini ko'rsatish."""
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    xp_data = db.get_user_xp_level(chat_id)
    stats = db.get_user_analytics(chat_id)
    streak_data = db.get_user_streak(chat_id)
    rank = db.get_user_global_rank(chat_id)

    level = xp_data.get('level', 1)
    xp = xp_data.get('xp', 0)
    next_xp = level * 100  # Keyingi daraja uchun kerakli XP
    level_name = globals.LEVEL_NAMES.get(level, {}).get(lang_id, "???")
    level_emoji = globals.LEVEL_EMOJIS.get(level, "🌱")
    name = f"{db_user.get('first_name', '')} {db_user.get('last_name', '')}".strip()
    total_tests = stats.get('total_tests', 0) if stats else 0
    avg_acc = round(stats.get('avg_accuracy', 0), 1) if stats else 0
    streak = streak_data.get('current_streak', 0)

    # Badge'lar matni
    badges_str = xp_data.get('badges', '')
    if badges_str:
        badge_list = badges_str.split(',')
        badges_text = "\n".join(
            globals.BADGE_NAMES.get(b.strip(), {}).get(lang_id, b.strip())
            for b in badge_list if b.strip()
        )
    else:
        badges_text = globals.TEXT_NO_BADGES[lang_id]

    text = globals.TEXT_PROFILE[lang_id].format(
        name=name, level_emoji=level_emoji, level_name=level_name,
        level=level, xp=xp, next_xp=next_xp, rank=rank,
        tests=total_tests, accuracy=avg_acc, streak=streak,
        badges=badges_text
    )

    # XP progress bar
    progress = min(xp % 100, 100)
    filled = int(progress / 10)
    bar = "█" * filled + "░" * (10 - filled)
    text += f"\n\n<code>[{bar}] {progress}/100 XP</code>"

    keyboard = [
        [InlineKeyboardButton(globals.BTN_ANALYTICS_MENU[lang_id], callback_data='analytics')],
        [InlineKeyboardButton(globals.BTN_WRONG_ANS[lang_id], callback_data='wrong_ans')],
        [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


def process_test_completion(chat_id, correct, total, test_id, context):
    """Test tugagandan so'ng XP, badge va level yangilash."""
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    percent = (correct / total * 100) if total > 0 else 0

    # XP hisoblash va qo'shish
    xp_earned = get_xp_for_result(correct, total, percent)
    
    add_xp(chat_id, xp_earned, context, lang_id)

    # Badgelarni tekshirish
    check_and_award_badges(chat_id, lang_id, context)

def add_xp(chat_id, xp_earned, context=None, lang_id=1):
    if xp_earned <= 0: return
    
    result = db.add_user_xp(chat_id, xp_earned)
    
    # Mavsumiy reytingga qo'shish
    season = db.get_active_season()
    if season:
        db.add_seasonal_score(season["id"], chat_id, xp_earned)
        
    # Daraja ko'tarildi?
    if result.get('leveled_up') and context:
        new_level = result['level']
        level_name = globals.LEVEL_NAMES.get(new_level, {}).get(lang_id, "???")
        level_emoji = globals.LEVEL_EMOJIS.get(new_level, "🌱")
        msg = globals.TEXT_LEVEL_UP[lang_id].format(
            emoji=level_emoji, level_name=level_name,
            level=new_level, xp=result['xp']
        )
        try:
            context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='HTML')
        except:
            pass

    # Badge tekshirish
    messages = []
    badge_msgs = check_and_award_badges(chat_id, lang_id, context)
    messages.extend(badge_msgs)

    return messages
