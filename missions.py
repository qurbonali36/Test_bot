import datetime
import pytz
from database import Database
import globals
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

db = Database("tg_bot.db")

DAILY_MISSIONS_TEMPLATE = [
    {"key": "play_test", "target": 3, "reward": 50},
    {"key": "correct_answers", "target": 20, "reward": 30},
    {"key": "play_duel", "target": 1, "reward": 40},
]

WEEKLY_MISSIONS_TEMPLATE = [
    {"key": "play_test", "target": 15, "reward": 300},
    {"key": "correct_answers", "target": 100, "reward": 200},
    {"key": "play_duel", "target": 5, "reward": 250},
]

MISSION_NAMES = {
    "play_test": {1: "Test ishlash ({target} ta)", 2: "Пройти тест ({target} шт)", 3: "Play tests ({target})"},
    "correct_answers": {1: "To'g'ri javob topish ({target} ta)", 2: "Правильные ответы ({target} шт)", 3: "Correct answers ({target})"},
    "play_duel": {1: "Duel o'ynash ({target} ta)", 2: "Сыграть дуэль ({target} шт)", 3: "Play duel ({target})"},
}

def generate_missions(chat_id, m_type, reset_date):
    templates = DAILY_MISSIONS_TEMPLATE if m_type == "daily" else WEEKLY_MISSIONS_TEMPLATE
    for t in templates:
        db.add_user_mission(chat_id, m_type, t["key"], t["target"], "xp", t["reward"], reset_date)
        
def get_or_generate_missions(chat_id, m_type, reset_date):
    missions = db.get_user_missions(chat_id, m_type, reset_date)
    if not missions:
        generate_missions(chat_id, m_type, reset_date)
        missions = db.get_user_missions(chat_id, m_type, reset_date)
    return missions

def show_missions(update, context):
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] or 1
    
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.datetime.now(tz)
    daily_reset = now.strftime('%Y-%m-%d')
    
    # Monday is 0, Sunday is 6
    days_to_monday = now.weekday()
    monday_date = (now - datetime.timedelta(days=days_to_monday)).strftime('%Y-%m-%d')
    
    daily_missions = get_or_generate_missions(chat_id, "daily", daily_reset)
    weekly_missions = get_or_generate_missions(chat_id, "weekly", monday_date)
    
    msg_parts = []
    msg_parts.append(f"🎯 <b>{globals.MENU_MISSIONS.get(lang_id, 'Missions')}</b>\n")
    
    msg_parts.append(f"📅 <b>{globals.MISSIONS_DAILY.get(lang_id, 'Daily')}</b>")
    for m in daily_missions:
        name = MISSION_NAMES.get(m['mission_key'], {}).get(lang_id, m['mission_key']).format(target=m['target_value'])
        status = globals.MISSION_COMPLETED.get(lang_id, '✅') if m['completed'] else f"{m['current_value']}/{m['target_value']}"
        reward = globals.MISSION_PROGRESS.get(lang_id, '+{xp} XP').format(xp=m['reward_amount'])
        msg_parts.append(f"  🔸 {name} [{status}] <i>({reward})</i>")
        
    msg_parts.append(f"\n📆 <b>{globals.MISSIONS_WEEKLY.get(lang_id, 'Weekly')}</b>")
    for m in weekly_missions:
        name = MISSION_NAMES.get(m['mission_key'], {}).get(lang_id, m['mission_key']).format(target=m['target_value'])
        status = globals.MISSION_COMPLETED.get(lang_id, '✅') if m['completed'] else f"{m['current_value']}/{m['target_value']}"
        reward = globals.MISSION_PROGRESS.get(lang_id, '+{xp} XP').format(xp=m['reward_amount'])
        msg_parts.append(f"  🔹 {name} [{status}] <i>({reward})</i>")
        
    context.bot.send_message(chat_id=chat_id, text="\n".join(msg_parts), parse_mode='HTML')

def check_mission_progress(context, chat_id, mission_key, increment=1):
    completed_any = db.update_mission_progress(chat_id, mission_key, increment)
    if completed_any:
        # We need to give the reward if it was JUST completed.
        # However, update_mission_progress sets completed=1. If we just completed it, we should get the reward.
        # But wait, update_mission_progress returns 1 if completed, 0 if not, None if not found.
        # To give reward properly, we need to know the reward amount.
        # Let's adjust `update_mission_progress` in `database.py` or fetch it here.
        # It's easier to fetch all incomplete missions, update them, and give rewards.
        pass

def trigger_mission(chat_id, mission_key, increment=1):
    # This should be called from other modules when an action happens.
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.datetime.now(tz)
    daily_reset = now.strftime('%Y-%m-%d')
    days_to_monday = now.weekday()
    monday_date = (now - datetime.timedelta(days=days_to_monday)).strftime('%Y-%m-%d')
    
    # Daily
    row_daily = _update_and_check(chat_id, mission_key, increment, "daily", daily_reset)
    row_weekly = _update_and_check(chat_id, mission_key, increment, "weekly", monday_date)
    
    return row_daily, row_weekly

def _update_and_check(chat_id, mission_key, increment, m_type, reset_date):
    db.execute('SELECT id, current_value, target_value, completed, reward_amount FROM user_missions WHERE chat_id = ? AND mission_key = ? AND mission_type = ? AND reset_date = ? AND completed = 0', (chat_id, mission_key, m_type, reset_date))
    rows = db.dict_fetchall(db.cur)
    for row in rows:
        new_val = row['current_value'] + increment
        completed = 1 if new_val >= row['target_value'] else 0
        db.execute('UPDATE user_missions SET current_value = ?, completed = ? WHERE id = ?', (new_val, completed, row['id']))
        db.conn.commit()
        if completed:
            from gamification import add_xp
            add_xp(chat_id, row['reward_amount'])
