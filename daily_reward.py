import datetime
import pytz
from database import Database
import globals

db = Database("tg_bot.db")

def check_and_give_daily_reward(context, chat_id, lang_id):
    """
    Checks if the user is eligible for a daily reward.
    If so, gives XP, updates streak, and sends a notification.
    """
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.datetime.now(tz)
    current_date_str = now.strftime('%Y-%m-%d')
    
    status = db.get_daily_reward_status(chat_id)
    
    if not status:
        # First time getting a reward
        last_reward_date = "2000-01-01"
        reward_cycle_day = 0
        streak = 0
        max_streak = 0
    else:
        last_reward_date = status.get('last_reward_date') or "2000-01-01"
        reward_cycle_day = status.get('reward_cycle_day') or 0
        streak = status.get('current_streak') or 0
        max_streak = status.get('max_streak') or 0
        
    if last_reward_date == current_date_str:
        return False # Already claimed today
        
    last_date_obj = datetime.datetime.strptime(last_reward_date, '%Y-%m-%d').date()
    current_date_obj = now.date()
    
    delta = (current_date_obj - last_date_obj).days
    
    if delta == 1:
        # Streak continues
        streak += 1
        reward_cycle_day += 1
    else:
        # Streak broken
        streak = 1
        reward_cycle_day = 1
        
    if reward_cycle_day > 7:
        reward_cycle_day = 1
        
    if streak > max_streak:
        max_streak = streak
        
    # Calculate XP
    base_xp = 10
    xp_to_give = base_xp * reward_cycle_day
    bonus_xp = 0
    if reward_cycle_day == 7:
        bonus_xp = 50
        xp_to_give += bonus_xp
        
    # Update DB
    db.update_daily_reward_status(chat_id, current_date_str, reward_cycle_day, streak, max_streak)
    
    # Give XP
    from gamification import add_xp
    leveled_up = add_xp(chat_id, xp_to_give)
    
    # Send message
    title = globals.DAILY_REWARD_TITLE.get(lang_id, globals.DAILY_REWARD_TITLE[1])
    streak_msg = globals.DAILY_REWARD_STREAK.get(lang_id, globals.DAILY_REWARD_STREAK[1]).format(streak=streak)
    
    if reward_cycle_day == 7:
        today_msg = globals.DAILY_REWARD_BONUS.get(lang_id, globals.DAILY_REWARD_BONUS[1]).format(xp=xp_to_give)
    else:
        today_msg = globals.DAILY_REWARD_TODAY.get(lang_id, globals.DAILY_REWARD_TODAY[1]).format(xp=xp_to_give)
        
    msg = f"<b>{title}</b>\\n\\n{streak_msg}\\n{today_msg}"
    
    if leveled_up:
        # Gamification module already sends a level up message, but we can just let it do its thing.
        pass
        
    context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='HTML')
    return True
