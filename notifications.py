from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import Database
from globals import BTN_HOME as GLOBALS_BTN_HOME

db = Database('tg_bot.db')

with db.lock:
    row = db.execute_fetch('''
        CREATE TABLE IF NOT EXISTS notification_settings (
            chat_id INTEGER PRIMARY KEY,
            daily_reminder INTEGER DEFAULT 1,
            weekly_report INTEGER DEFAULT 1,
            new_test_alert INTEGER DEFAULT 1
        )
    ''')
    db.conn.commit()

TEXTS = {
    1: {
        'settings': '🔔 <b>Bildirishnomalar sozlamalari</b>\n\nQuyidagi bildirishnomalarni yoqishingiz yoki o\'chirishingiz mumkin:',
        'daily': 'Kunlik eslatma',
        'weekly': 'Haftalik hisobot',
        'new_test': 'Yangi test xabarnomasi',
        'daily_msg': '🌅 <b>Xayrli tong!</b>\nBugun o\'qish va rivojlanish uchun ajoyib kun. Testlarni ishlashni unutmang!',
        'weekly_msg': '📊 <b>Haftalik hisobot</b>\nSiz bu hafta ajoyib natijalar ko\'rsatdingiz. O\'z ustingizda ishlashda davom eting!',
        'new_test_msg': '🆕 <b>Yangi test qo\'shildi!</b>\nTest ID: <code>{test_id}</code>\n\nO\'z bilimingizni sinab ko\'rish uchun ajoyib imkoniyat!'
    },
    2: {
        'settings': '🔔 <b>Настройки уведомлений</b>\n\nВы можете включить или отключить следующие уведомления:',
        'daily': 'Ежедневное напоминание',
        'weekly': 'Еженедельный отчет',
        'new_test': 'Уведомление о новом тесте',
        'daily_msg': '🌅 <b>Доброе утро!</b>\nСегодня отличный день для учебы и развития. Не забудьте пройти тесты!',
        'weekly_msg': '📊 <b>Еженедельный отчет</b>\nНа этой неделе вы показали отличные результаты. Продолжайте в том же духе!',
        'new_test_msg': '🆕 <b>Добавлен новый тест!</b>\nID теста: <code>{test_id}</code>\n\nОтличная возможность проверить свои знания!'
    },
    3: {
        'settings': '🔔 <b>Notification Settings</b>\n\nYou can enable or disable the following notifications:',
        'daily': 'Daily reminder',
        'weekly': 'Weekly report',
        'new_test': 'New test alert',
        'daily_msg': '🌅 <b>Good morning!</b>\nToday is a great day to learn and grow. Don\'t forget to practice tests!',
        'weekly_msg': '📊 <b>Weekly Report</b>\nYou have shown great results this week. Keep up the good work!',
        'new_test_msg': '🆕 <b>New test added!</b>\nTest ID: <code>{test_id}</code>\n\nA great opportunity to test your knowledge!'
    }
}

BTN_NOTIFICATIONS = {1: '🔔 Bildirishnomalar', 2: '🔔 Уведомления', 3: '🔔 Notifications'}

def get_notification_settings(chat_id):
    with db.lock:
        rows = db.execute_fetch("SELECT * FROM notification_settings WHERE chat_id = ?", (chat_id,), fetchone=True)
        if not row:
            db.execute("INSERT INTO notification_settings (chat_id) VALUES (?)", (chat_id,))
            db.conn.commit()
            return {"chat_id": chat_id, "daily_reminder": 1, "weekly_report": 1, "new_test_alert": 1}
        
        columns = [column[0] for column in db.cur.description]
        return dict(zip(columns, row))

def toggle_notification(chat_id, setting_name):
    settings = get_notification_settings(chat_id)
    new_val = 0 if settings.get(setting_name) == 1 else 1
    if setting_name in ['daily_reminder', 'weekly_report', 'new_test_alert']:
        with db.lock:
            db.execute(f"UPDATE notification_settings SET {setting_name} = ? WHERE chat_id = ?", (new_val, chat_id))
            db.conn.commit()

def get_users_with_setting(setting_name):
    if setting_name in ['daily_reminder', 'weekly_report', 'new_test_alert']:
        with db.lock:
            db.execute(f"SELECT chat_id FROM notification_settings WHERE {setting_name} = 1", fetchall=True)
            return [row[0] for row in rows]
    return []

def get_settings_keyboard(chat_id, lang_id):
    settings = get_notification_settings(chat_id)
    texts = TEXTS[lang_id]
    
    def get_indicator(val):
        return '✅' if val == 1 else '❌'

    keyboard = [
        [InlineKeyboardButton(f"{texts['daily']} {get_indicator(settings['daily_reminder'])}", callback_data="notif_toggle_daily")],
        [InlineKeyboardButton(f"{texts['weekly']} {get_indicator(settings['weekly_report'])}", callback_data="notif_toggle_weekly")],
        [InlineKeyboardButton(f"{texts['new_test']} {get_indicator(settings['new_test_alert'])}", callback_data="notif_toggle_newtest")],
        [InlineKeyboardButton(GLOBALS_BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')]
    ]
    return InlineKeyboardMarkup(keyboard)

def show_notification_settings(update, context):
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
    texts = TEXTS[lang_id]
    
    reply_markup = get_settings_keyboard(chat_id, lang_id)
    
    if update.message:
        update.message.reply_text(texts['settings'], reply_markup=reply_markup, parse_mode='HTML')
    elif update.callback_query:
        update.callback_query.message.edit_text(texts['settings'], reply_markup=reply_markup, parse_mode='HTML')

def handle_notification_callback(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    data = query.data
    
    if data == "notif_toggle_daily":
        toggle_notification(chat_id, 'daily_reminder')
    elif data == "notif_toggle_weekly":
        toggle_notification(chat_id, 'weekly_report')
    elif data == "notif_toggle_newtest":
        toggle_notification(chat_id, 'new_test_alert')
        
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
    reply_markup = get_settings_keyboard(chat_id, lang_id)
    
    query.answer()
    query.edit_message_reply_markup(reply_markup=reply_markup)

def send_weekly_report(context, chat_id):
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
    text = TEXTS[lang_id]['weekly_msg']
    try:
        context.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
    except Exception as e:
        print(f"Failed to send weekly report to {chat_id}: {e}")

def send_daily_reminder(context, chat_id):
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
    text = TEXTS[lang_id]['daily_msg']
    try:
        context.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
    except Exception as e:
        print(f"Failed to send daily reminder to {chat_id}: {e}")

def send_daily_reminders_all(context):
    users = get_users_with_setting('daily_reminder')
    for chat_id in users:
        send_daily_reminder(context, chat_id)

def notify_new_test(context, test_id):
    users = get_users_with_setting('new_test_alert')
    for chat_id in users:
        db_user = db.get_user_by_chat_id(chat_id)
        lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
        text = TEXTS[lang_id]['new_test_msg'].format(test_id=test_id)
        try:
            context.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
        except Exception as e:
            print(f"Failed to notify {chat_id} about new test: {e}")
