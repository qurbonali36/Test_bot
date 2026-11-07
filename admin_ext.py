import os
import time
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from database import Database
import globals
import openpyxl

db = Database("tg_bot.db")

def get_json_files_count():
    papka = 'json_files'
    if not os.path.exists(papka):
        return 0
    return len([f for f in os.listdir(papka) if f.endswith('.json')])

def handle_admin_text(update, context):
    text = update.message.text
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    if text == globals.BTN_ADMIN_MONITORING[lang_id]:
        show_monitoring(update, context)
        return True
    elif text == globals.BTN_ADMIN_USERS[lang_id]:
        show_users_menu(update, context)
        return True
    elif text == globals.BTN_ADMIN_FEEDBACKS[lang_id]:
        show_feedbacks_menu(update, context)
        return True
    elif text == globals.BTN_ADMIN_BROADCAST[lang_id]:
        show_broadcast_menu(update, context)
        return True
    elif text == globals.BTN_ADMIN_CLEAR_CACHE[lang_id]:
        clear_cache(update, context)
        return True
    elif text == globals.BTN_SETTINGS[lang_id]:
        show_admin_settings(update, context)
        return True
    elif text == globals.BTN_ADMIN_NORMAL_MODE[lang_id]:
        context.user_data["is_admin_mode"] = False
        from methods import send_main_menu
        send_main_menu(context, chat_id, lang_id)
        return True
    
    return False

def show_admin_settings(update, context):
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    keyboard = [
        [InlineKeyboardButton(globals.BTN_LANG_UZ, callback_data='admlang_1')],
        [InlineKeyboardButton(globals.BTN_LANG_RU, callback_data='admlang_2')],
        [InlineKeyboardButton(globals.BTN_LANG_EN, callback_data='admlang_3')]
    ]
    update.message.reply_text(globals.ADMIN_CHOOSE_LANG[lang_id], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

def show_monitoring(update, context):
    start_time = time.time()
    
    users_count = db.get_users_count()
    json_count = get_json_files_count()
    
    now = datetime.now()
    active_threshold = now - timedelta(days=30)
    
    with db.lock:
        active_users = db.execute_fetch("SELECT COUNT(*) FROM user WHERE last_active >= ?", (active_threshold.strftime("%Y-%m-%d %H:%M:%S"),), raw_fetchone=True)[0] or 0
    inactive_users = users_count - active_users

    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    text = globals.get_monitoring_text(lang_id, users_count, active_users, inactive_users, json_count, latency)
    update.message.reply_text(text, parse_mode='HTML')

def clear_cache(update, context):
    cleared = 0
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                import shutil
                try:
                    shutil.rmtree(os.path.join(root, dir_name))
                    cleared += 1
                except: pass
    
    context.user_data.clear()
    context.bot_data.clear()
    
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    update.message.reply_text(globals.ADMIN_CACHE_CLEARED[lang_id].format(cleared=cleared), parse_mode='HTML')

def show_users_menu(update, context):
    with db.lock:
        top_users = db.execute_fetch("""
            SELECT u.chat_id, u.first_name, u.last_name, u.phone_number, COALESCE(SUM(ur.point_test), 0) as score 
            FROM user u 
            LEFT JOIN users_results ur ON u.chat_id = ur.chat_id 
            GROUP BY u.chat_id 
            ORDER BY score DESC 
            LIMIT 20
        """, raw_fetchall=True)
    
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    text = globals.ADMIN_TOP_USERS[lang_id]
    for i, u in enumerate(top_users, 1):
        name = f"{u[1] or ''} {u[2] or ''}".strip() or globals.UNKNOWN[lang_id]
        text += f"{i}. 👤 <a href='tg://user?id={u[0]}'>{name}</a> | 📈 {u[4]} ball\n"
    text += globals.ADMIN_CLEAR_INACTIVE[lang_id]
    
    keyboard = [
        [InlineKeyboardButton(globals.BTN_INACT_3[lang_id], callback_data='del_inact_3')],
        [InlineKeyboardButton(globals.BTN_INACT_6[lang_id], callback_data='del_inact_6')],
        [InlineKeyboardButton(globals.BTN_INACT_12[lang_id], callback_data='del_inact_12')],
        [InlineKeyboardButton(globals.BTN_INACT_99[lang_id], callback_data='del_inact_99')]
    ]
    update.message.reply_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

def show_feedbacks_menu(update, context):
    context.user_data["admin_state"] = "wait_year"
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    context.user_data["admin_state"] = "wait_year"
    update.message.reply_text(globals.ADMIN_REPORT_YEAR[lang_id], parse_mode='HTML')

def handle_admin_callback_ext(update, context):
    query = update.callback_query
    data = query.data
    
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    if data.startswith('del_inact_'):
        months = int(data.split('_')[-1])
        if months == 99:
            days = 365
        else:
            days = months * 30
            
        threshold = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        with db.lock:
            feedbacks = db.execute_fetch("SELECT COUNT(*) FROM user WHERE last_active < ?", (threshold,), raw_fetchone=True)[0] or 0
            
            db.execute("DELETE FROM user WHERE last_active < ?", (threshold,))
        
        query.edit_message_text(globals.get_deleted_users_text(lang_id, months, count), parse_mode='HTML')

    elif data.startswith('fbseason_'):
        parts = data.split('_')
        year = parts[1]
        season = parts[2]
        
        if season == "bahor": months = [3, 4, 5]
        elif season == "yoz": months = [6, 7, 8]
        elif season == "kuz": months = [9, 10, 11]
        elif season == "qish": months = [12, 1, 2]
        else: months = []
        
        keyboard = []
        month_names = {1:"Yanvar", 2:"Fevral", 3:"Mart", 4:"Aprel", 5:"May", 6:"Iyun", 7:"Iyul", 8:"Avgust", 9:"Sentabr", 10:"Oktabr", 11:"Noyabr", 12:"Dekabr"}
        for m in months:
            keyboard.append([InlineKeyboardButton(f"{year}-yil, {month_names[m]}", callback_data=f'fbmonth_{year}_{m}')])
            
        query.edit_message_text(globals.ADMIN_CHOOSE_MONTH[lang_id], reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data.startswith('admin_reply_'):
        user_id = data.replace('admin_reply_', '')
        context.user_data["admin_state"] = "wait_reply_msg"
        context.user_data["reply_user_id"] = user_id
        
        text = (f"👤 <b>Foydalanuvchiga (ID: {user_id}) javob yozing:</b>\n\n"
                f"<i>Yuborilgan xabar bevosita foydalanuvchiga yetkaziladi.</i>")
        
        query.message.reply_text(text, parse_mode='HTML')
        query.answer()

    elif data.startswith('fbmonth_'):
        parts = data.split('_')
        year = parts[1]
        month = parts[2]
        
        month_str = f"{int(month):02d}"
        search_pattern = f"{year}-{month_str}-%"
        
        with db.lock:
            db.execute_fetch("""
                SELECT f.created_at, f.chat_id, u.first_name, u.last_name, u.phone_number, f.message
                FROM feedbacks f
                LEFT JOIN user u ON f.chat_id = u.chat_id
                WHERE f.created_at LIKE ?
            """, (search_pattern,), fetchall=True)
        
        month_names = {1:"Yanvar", 2:"Fevral", 3:"Mart", 4:"Aprel", 5:"May", 6:"Iyun", 7:"Iyul", 8:"Avgust", 9:"Sentabr", 10:"Oktabr", 11:"Noyabr", 12:"Dekabr"}
        m_name = month_names[int(month)]
        
        if not feedbacks:
            query.edit_message_text(globals.ADMIN_NO_FEEDBACKS[lang_id].format(year=year, m_name=m_name), parse_mode='HTML')
            return
            
        if len(feedbacks) <= 10:
            query.message.delete()
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=globals.ADMIN_FEEDBACKS_TEXT[lang_id].format(year=year, m_name=m_name),
                parse_mode='HTML'
            )
            for fb in feedbacks:
                name = f"{fb[2] or ''} {fb[3] or ''}".strip() or globals.UNKNOWN[lang_id]
                phone = fb[4] or globals.NO_PHONE[lang_id]
                msg_text = f"👤 <b>{name}</b> (<code>{phone}</code>)\n🕒 <i>{fb[0]}</i>\n💬 {fb[5]}"
                try:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=msg_text, parse_mode='HTML')
                except Exception:
                    pass
            return
            
        file_name = f"Fikrlar_{year}_{month_str}.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Feedbacks"
        
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        
        # 1-qator: Sarlavha
        ws.merge_cells('A1:F1')
        title_cell = ws['A1']
        title_cell.value = f"{year} yil {m_name} oyi"
        title_cell.font = Font(name='Calibri', size=18, bold=True, color='FFFFFF')
        title_cell.fill = PatternFill(start_color='4F81BD', end_color='4F81BD', fill_type='solid')
        title_cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # 2-qator: Sarlavhalar ustuni
        headers = ["Sana va vaqt", "Chat ID", "Ism", "Familiya", "Telefon", "Fikr"]
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=2, column=col_num)
            cell.value = header
            cell.font = Font(name='Calibri', size=12, bold=True, color='FFFFFF')
            cell.fill = PatternFill(start_color='000000', end_color='000000', fill_type='solid')
            cell.alignment = Alignment(horizontal='center', vertical='center')
            
        # Ustun kengliklari
        widths = {'A': 22, 'B': 25, 'C': 22, 'D': 17, 'E': 17, 'F': 37}
        for col, w in widths.items():
            ws.column_dimensions[col].width = w
            
        thin = Side(border_style="thin", color="000000")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        
        # Fikrlarni yozish
        for row_idx, fb in enumerate(feedbacks, 3):
            data_row = [fb[0], fb[1], fb[2], fb[3], fb[4], fb[5]]
            for col_idx, value in enumerate(data_row, 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.value = value
                cell.font = Font(name='Calibri', size=11)
                cell.border = border
                if col_idx == 6:
                    cell.alignment = Alignment(vertical='center', wrap_text=True)
                else:
                    cell.alignment = Alignment(horizontal='center', vertical='center')
            
        wb.save(file_name)
        
        with open(file_name, 'rb') as f:
            context.bot.send_document(
                chat_id=update.effective_chat.id, 
                document=f,
                caption=f"📁 {year}-yil, {m_name} oyidagi jami {len(feedbacks)} ta fikrlar."
            )
        os.remove(file_name)
        query.message.delete()

    elif data == 'bc_user':
        context.user_data["admin_state"] = "bc_wait_user"
        query.edit_message_text(globals.ADMIN_BC_USER[lang_id])
        
    elif data == 'bc_all':
        context.user_data["admin_state"] = "bc_wait_msg_all"
        query.edit_message_text(globals.ADMIN_BC_ALL[lang_id])

    elif data.startswith('admlang_'):
        new_lang = int(data.split('_')[1])
        chat_id = update.effective_chat.id
        db.update_user_data(chat_id, "lang_id", new_lang)
        
        from methods import send_admin_menu
        query.message.delete()
        send_admin_menu(context, chat_id, new_lang)

def show_broadcast_menu(update, context):
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    keyboard = [
        [InlineKeyboardButton(globals.BTN_BC_USER[lang_id], callback_data='bc_user')],
        [InlineKeyboardButton(globals.BTN_BC_ALL[lang_id], callback_data='bc_all')]
    ]
    update.message.reply_text(globals.ADMIN_BC_TYPE[lang_id], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

def handle_admin_text_ext(update, context):
    state = context.user_data.get("admin_state")
    if not state: return False
    
    text = update.message.text
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    if state == "wait_year":
        if text.isdigit() and len(text) == 4:
            keyboard = [
                [InlineKeyboardButton(globals.ADMIN_SEASON_SPRING[lang_id], callback_data=f'fbseason_{text}_bahor')],
                [InlineKeyboardButton(globals.ADMIN_SEASON_SUMMER[lang_id], callback_data=f'fbseason_{text}_yoz')],
                [InlineKeyboardButton(globals.ADMIN_SEASON_AUTUMN[lang_id], callback_data=f'fbseason_{text}_kuz')],
                [InlineKeyboardButton(globals.ADMIN_SEASON_WINTER[lang_id], callback_data=f'fbseason_{text}_qish')]
            ]
            update.message.reply_text(globals.ADMIN_CHOOSE_SEASON[lang_id], reply_markup=InlineKeyboardMarkup(keyboard))
            context.user_data["admin_state"] = None
        else:
            update.message.reply_text(globals.ADMIN_ERR_YEAR[lang_id])
        return True

    elif state == "bc_wait_user":
        context.user_data["bc_target_user"] = text
        context.user_data["admin_state"] = "bc_wait_msg_user"
        update.message.reply_text(globals.ADMIN_BC_SEND_MSG[lang_id])
        return True
        
    elif state in ("bc_wait_msg_user", "bc_wait_msg_all", "wait_reply_msg"):
        return handle_admin_media_ext(update, context)
        
    return False

def handle_admin_media_ext(update, context):
    state = context.user_data.get("admin_state")
    if state not in ("bc_wait_msg_user", "bc_wait_msg_all", "wait_reply_msg"):
        return False
        
    msg = update.message
    targets = []
    
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    
    if state == "bc_wait_msg_user":
        target = context.user_data.get("bc_target_user", "")
        if target.isdigit():
            targets = [int(target)]
        else:
            with db.lock:
                res = db.execute_fetch("SELECT chat_id FROM user WHERE phone_number LIKE ?", (f"%{target}%",), raw_fetchone=True)
            if res: targets = [res[0]]
            else:
                msg.reply_text(globals.ADMIN_USER_NOT_FOUND[lang_id])
                return True
    elif state == "wait_reply_msg":
        targets = [int(context.user_data.get("reply_user_id", 0))]
    else:
        targets = [u['chat_id'] for u in db.get_all_users() if u.get('chat_id')]
        
    success = 0
    fail = 0
    
    reply_prefix = "👨‍💻 <b>Admindan javob:</b>\n\n" if state == "wait_reply_msg" else ""
    
    for t_id in targets:
        if not t_id:
            continue
        try:
            if msg.text:
                context.bot.send_message(t_id, reply_prefix + msg.text, parse_mode='HTML')
            elif msg.photo:
                cap = (reply_prefix + msg.caption) if msg.caption else reply_prefix
                context.bot.send_photo(t_id, msg.photo[-1].file_id, caption=cap, parse_mode='HTML')
            elif msg.video:
                cap = (reply_prefix + msg.caption) if msg.caption else reply_prefix
                context.bot.send_video(t_id, msg.video.file_id, caption=cap, parse_mode='HTML')
            elif msg.audio:
                cap = (reply_prefix + msg.caption) if msg.caption else reply_prefix
                context.bot.send_audio(t_id, msg.audio.file_id, caption=cap, parse_mode='HTML')
            elif msg.document:
                cap = (reply_prefix + msg.caption) if msg.caption else reply_prefix
                context.bot.send_document(t_id, msg.document.file_id, caption=cap, parse_mode='HTML')
            elif msg.voice:
                cap = (reply_prefix + msg.caption) if msg.caption else reply_prefix
                context.bot.send_voice(t_id, msg.voice.file_id, caption=cap, parse_mode='HTML')
            success += 1
        except Exception as e:
            fail += 1
            
    if state == "wait_reply_msg":
        if success > 0:
            msg.reply_text("✅ Javob muvaffaqiyatli yuborildi!")
        else:
            msg.reply_text("❌ Foydalanuvchiga javob yuborib bo'lmadi (Ehtimol u botni bloklagan).")
    else:
        msg.reply_text(globals.get_bc_result(lang_id, success, fail), parse_mode='HTML')
        
    context.user_data["admin_state"] = None
    return True
