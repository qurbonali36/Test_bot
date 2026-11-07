import datetime
import pytz
from database import Database
from telegram import ParseMode

db = Database("tg_bot.db")

def send_weekly_digest(context):
    """Sends a weekly progress digest to all users."""
    users = db.get_all_users()
    if not users:
        return
        
    for user in users:
        chat_id = user["chat_id"]
        lang_id = user.get("lang_id") or 1
        
        # Get weekly stats dynamically from users_results
        row = db.execute_fetch("""
            SELECT COALESCE(SUM(point_test), 0) as xp_earned, COUNT(id) as tests_taken 
            FROM users_results 
            WHERE chat_id = ? AND created_at >= datetime('now', '-7 days')
        """, (chat_id,), fetchone=True)
        
        if not row or row[1] == 0:
            continue
            
        xp = row[0]
        tests = row[1]
        
        msg = {
            1: f"📊 <b>Haftalik Hisobot</b>\\n\\nSiz bu hafta <b>{tests}</b> ta test yechdingiz va <b>{xp}</b> XP to'pladingiz! Davom eting!",
            2: f"📊 <b>Еженедельный отчет</b>\\n\\nНа этой неделе вы решили <b>{tests}</b> тестов и заработали <b>{xp}</b> XP! Так держать!",
            3: f"📊 <b>Weekly Digest</b>\\n\\nYou have completed <b>{tests}</b> tests and earned <b>{xp}</b> XP this week! Keep it up!"
        }[lang_id]
        
        try:
            context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML)
        except Exception:
            pass

def process_seasonal_leaderboard(context):
    """Ends the current season, distributes rewards, and starts a new one."""
    current_season = db.get_current_season()
    if not current_season:
        # Create initial season if none exists
        start_date = datetime.datetime.now(pytz.timezone("Asia/Tashkent")).strftime('%Y-%m-%d %H:%M:%S')
        db.create_season(f"Season 1", start_date)
        return
        
    season_id = current_season["id"]
    
    # End current season
    db.end_season(season_id)
    
    # Get top 3 players
    top_players = db.get_seasonal_leaderboard(season_id, limit=3)
    
    for idx, player in enumerate(top_players, 1):
        chat_id = player["chat_id"]
        lang_id = player.get("lang_id") or 1
        xp_reward = 1000 if idx == 1 else (500 if idx == 2 else 250)
        
        from gamification import add_xp
        add_xp(chat_id, xp_reward)
        
        msg = {
            1: f"🏆 <b>Mavsum tugadi!</b>\\n\\nSiz {idx}-o'rinni egalladingiz va {xp_reward} XP yutib oldingiz!",
            2: f"🏆 <b>Сезон завершен!</b>\\n\\nВы заняли {idx} место и выиграли {xp_reward} XP!",
            3: f"🏆 <b>Season ended!</b>\\n\\nYou took #{idx} place and won {xp_reward} XP!"
        }[lang_id]
        
        try:
            context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML)
        except Exception:
            pass
            
    # Create new season
    new_season_name = f"Season {current_season['id'] + 1}"
    start_date = datetime.datetime.now(pytz.timezone("Asia/Tashkent")).strftime('%Y-%m-%d %H:%M:%S')
    db.create_season(new_season_name, start_date)
    
def init_scheduler(job_queue):
    tashkent_tz = pytz.timezone('Asia/Tashkent')
    
    # Send weekly digest every Sunday at 20:00
    job_queue.run_daily(
        send_weekly_digest, 
        datetime.time(hour=20, minute=0, tzinfo=tashkent_tz),
        days=(6,) # Sunday
    )
    
    # End season every 1st of the month? Actually let's just do it every 4 weeks. Or for simplicity, run it at some specific time.
    # The requirement: "Seasonal Leaderboards". I will run it on a specific day of the month or just assume it runs every 30 days.
    # We can schedule a monthly job but `run_monthly` isn't in older apscheduler. We will use `run_daily` and check the date.
    # Send daily reminder every day at 10:00
    from notifications import send_daily_reminders_all
    job_queue.run_daily(
        send_daily_reminders_all,
        datetime.time(hour=10, minute=0, tzinfo=tashkent_tz)
    )
    
    def check_season_end(context):
        now = datetime.datetime.now(tashkent_tz)
        if now.day == 1: # 1st of every month
            process_seasonal_leaderboard(context)
            
    job_queue.run_daily(
        check_season_end,
        datetime.time(hour=0, minute=5, tzinfo=tashkent_tz)
    )
