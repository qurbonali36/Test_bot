from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
from gamification import add_xp
import globals
import datetime
import pytz

db = Database("tg_bot.db")

def show_tournaments(update, context):
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] or 1
    
    tournaments = db.get_active_tournaments()
    
    if not tournaments:
        msg = {
            1: "🏟️ Hozircha faol turnirlar yo'q.",
            2: "🏟️ Пока нет активных турниров.",
            3: "🏟️ No active tournaments at the moment."
        }[lang_id]
        if update.callback_query:
            update.callback_query.message.edit_text(msg)
        else:
            context.bot.send_message(chat_id=chat_id, text=msg)
        return
        
    title = globals.MENU_TOURNAMENT.get(lang_id, globals.MENU_TOURNAMENT[1])
    text = f"<b>{title}</b>\\n\\n"
    
    keyboard = []
    
    for t in tournaments:
        t_id = t["id"]
        t_name = t["name"]
        t_status = t["status"]
        
        status_text = "🟢" if t_status == "active" else "⏳"
        keyboard.append([InlineKeyboardButton(text=f"{status_text} {t_name}", callback_data=f"tourney_view_{t_id}")])
        
    keyboard.append([InlineKeyboardButton(text=globals.BTN_BACK.get(lang_id, "⬅️ Orqaga"), callback_data="home")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        update.callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=reply_markup)

def handle_tournament_callback(update, context):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] or 1
    
    if data == "tourney_list":
        show_tournaments(update, context)
        return
        
    if data.startswith("tourney_view_"):
        t_id = int(data.split("_")[2])
        t = db.get_tournament(t_id)
        if not t:
            query.answer("Error", show_alert=True)
            return
            
        participants = db.get_tournament_participants(t_id)
        is_registered = any(p["chat_id"] == chat_id for p in participants)
        
        text = f"🏆 <b>{t['name']}</b>\\n\\n"
        text += f"Boshlanish: {t['start_time']}\\n"
        text += f"Ishtirokchilar: {len(participants)}\\n"
        text += f"Holat: {t['status']}\\n\\n"
        
        keyboard = []
        if not is_registered and t['status'] == 'pending':
            btn_reg = {1: "📝 Ro'yxatdan o'tish", 2: "📝 Регистрация", 3: "📝 Register"}[lang_id]
            keyboard.append([InlineKeyboardButton(text=btn_reg, callback_data=f"tourney_reg_{t_id}")])
        elif is_registered and t['status'] == 'active':
            btn_start = {1: "▶️ Boshlash", 2: "▶️ Начать", 3: "▶️ Start"}[lang_id]
            keyboard.append([InlineKeyboardButton(text=btn_start, callback_data=f"tourney_start_{t_id}")])
            
        btn_lb = {1: "📊 Reyting", 2: "📊 Рейтинг", 3: "📊 Leaderboard"}[lang_id]
        keyboard.append([InlineKeyboardButton(text=btn_lb, callback_data=f"tourney_lb_{t_id}")])
        keyboard.append([InlineKeyboardButton(text=globals.BTN_BACK.get(lang_id, "⬅️ Orqaga"), callback_data="tourney_list")])
        
        query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data.startswith("tourney_reg_"):
        t_id = int(data.split("_")[2])
        db.register_tournament(t_id, chat_id)
        msg = {1: "✅ Ro'yxatdan o'tdingiz!", 2: "✅ Вы зарегистрированы!", 3: "✅ Registered successfully!"}[lang_id]
        query.answer(msg, show_alert=True)
        # Refresh view
        query.data = f"tourney_view_{t_id}"
        handle_tournament_callback(update, context)
        
    elif data.startswith("tourney_lb_"):
        t_id = int(data.split("_")[2])
        t = db.get_tournament(t_id)
        lb = db.get_tournament_leaderboard(t_id)
        
        text = f"📊 <b>{t['name']} - Reyting</b>\\n\\n"
        for idx, row in enumerate(lb, 1):
            name = f"{row.get('first_name','')} {row.get('last_name','')}".strip()
            score = row.get("score", 0)
            time = row.get("time_taken", 0)
            text += f"{idx}. {name} - {score} ball ({time}s)\\n"
            
        keyboard = [[InlineKeyboardButton(text=globals.BTN_BACK.get(lang_id, "⬅️ Orqaga"), callback_data=f"tourney_view_{t_id}")]]
        query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data.startswith("tourney_start_"):
        t_id = int(data.split("_")[2])
        t = db.get_tournament(t_id)
        if not t or t['status'] != 'active':
            query.answer("Turnir hozir faol emas!", show_alert=True)
            return
            
        # Start test
        test_id = t["test_id"]
        from deeplink import handle_deeplink
        test_meta = db.get_test_meta(test_id)
        if test_meta:
            egasi_id = str(test_meta.get('chat_id', ''))
            query.message.delete()
            # Save tournament context to user_data so quest_poll knows it's a tournament
            context.user_data['active_tournament_id'] = t_id
            handle_deeplink(update, context, egasi_id, test_id)
        else:
            query.answer("Test topilmadi!", show_alert=True)
