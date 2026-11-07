from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from config import ADMIN_ID
from database import Database
import globals

db = Database("tg_bot.db")

def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID) or user_id == ADMIN_ID

def get_admin_menu_keyboard(lang_id=1):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(globals.BTN_BOT_STATS[lang_id], callback_data='adm_stats')],
        [InlineKeyboardButton(globals.BTN_USERS_LIST[lang_id], callback_data='adm_users')],
        [InlineKeyboardButton(globals.BTN_FEEDBACKS_LIST[lang_id], callback_data='adm_feedbacks')],
        [InlineKeyboardButton(globals.BTN_BROADCAST[lang_id], callback_data='adm_broadcast')],
        [InlineKeyboardButton("👤 Oddiy foydalanuvchi rejimi", callback_data='adm_normal')],
        [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
    ])

def admin_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return

    db_user = db.get_user_by_chat_id(user_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    from methods import send_admin_menu
    send_admin_menu(context, user_id, lang_id)
    context.user_data["state"] = globals.STATES["menu"]
    context.user_data["is_admin_mode"] = True

def handle_admin_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        query.answer("Siz admin emassiz!", show_alert=True)
        return

    query.answer()
    data = query.data
    chat_id = update.effective_chat.id

    back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bosh panelga qaytish", callback_data='adm_back')]])

    if data.startswith('fb') or data.startswith('bc_') or data.startswith('del_inact_') or data.startswith('admlang_') or data.startswith('admin_reply_'):
        from admin_ext import handle_admin_callback_ext
        handle_admin_callback_ext(update, context)
        return

    if data == 'adm_stats':
        a = db.get_admin_analytics()

        top_tests_text = ""
        top_tests = a.get('top_tests', [])
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for i, t in enumerate(top_tests):
            medal = medals[i] if i < len(medals) else f"{i+1}."
            title = t.get('title', 'Nomsiz')
            count = t.get('play_count', 0)
            top_tests_text += f"  {medal} <i>{title}</i> — <b>{count}</b> marta\n"
        if not top_tests_text:
            top_tests_text = "  <i>Hali testlar ishlanmagan</i>\n"

        stats_text = (
            "📊 <b>ADMIN ANALITIKA PANELI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👥 <b>FOYDALANUVCHILAR</b>\n"
            f"  ├ 📅 Bugun faol: <b>{a['today_users']}</b>\n"
            f"  ├ 📆 Haftalik: <b>{a['week_users']}</b>\n"
            f"  ├ 🗓 Oylik: <b>{a['month_users']}</b>\n"
            f"  └ 🌍 Umumiy: <b>{a['total_users']}</b>\n\n"
            "📝 <b>TEST FAOLLIGI</b>\n"
            f"  ├ 📅 Bugun ishlangan: <b>{a['today_tests']}</b>\n"
            f"  ├ 📆 Haftalik: <b>{a['week_tests']}</b>\n"
            f"  ├ 🗓 Oylik: <b>{a['month_tests']}</b>\n"
            f"  └ 📊 Jami natijalar: <b>{a['total_results']}</b>\n\n"
            "📚 <b>TESTLAR BAZASI</b>\n"
            f"  ├ Yaratilgan testlar: <b>{a['total_tests_created']}</b>\n"
            f"  └ O'rtacha aniqlik: <b>{a['avg_accuracy']}%</b>\n\n"
            "🏆 <b>TOP-5 MASHHUR TESTLAR</b>\n"
            f"{top_tests_text}\n"
            "💬 <b>FIKRLAR</b>\n"
            f"  └ Jami: <b>{a['feedbacks']}</b> ta\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>💡 Ma'lumotlar real-vaqt rejimida.</i>"
        )
        
        query.edit_message_text(text=stats_text, reply_markup=back_btn, parse_mode='HTML')

    elif data == 'adm_users':
        users = db.get_all_users()[:20]
        if not users:
            text = "⚠️ <b>Bazada foydalanuvchilar topilmadi.</b>"
        else:
            text = "📁 <b>FOYDALANUVCHILAR BAZASI (Top 20)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for i, u in enumerate(users, 1):
                fname = u.get('first_name') or ''
                lname = u.get('last_name') or ''
                phone = u.get('phone_number') or 'Kiritilmagan'
                uid = u.get('chat_id', '')
                text += f"👤 <b>{i}.</b> <a href='tg://user?id={uid}'>{fname} {lname}</a>\n"
                text += f"   └ 📱 <code>{phone}</code>\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        query.edit_message_text(text=text, reply_markup=back_btn, parse_mode='HTML')

    elif data == 'adm_feedbacks':
        feedbacks = db.get_all_feedbacks()
        if not feedbacks:
            text = "📭 <b>Hozircha yangi murojaat yoki fikrlar mavjud emas.</b>"
        else:
            text = "📨 <b>KELIB TUSHKAN FIKRLAR (So'nggi 10 ta)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for f in feedbacks[:10]:
                fname = f.get('first_name') or ''
                lname = f.get('last_name') or ''
                msg = f.get('message', '')
                created = f.get('created_at', '')
                text += f"👤 <b>{fname} {lname}</b>\n"
                text += f" ├ 📝 <i>\"{msg}\"</i>\n"
                text += f" └ 🕒 <code>{created}</code>\n\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━"
                
        query.edit_message_text(text=text, reply_markup=back_btn, parse_mode='HTML')

    elif data == 'adm_broadcast':
        query.message.delete()
        db_user = db.get_user_by_chat_id(user_id)
        lang_id = db_user.get("lang_id", 1) if db_user else 1
        prompt = globals.TEXT_BROADCAST_PROMPT.get(lang_id, "Xabarni yuboring:")
        context.bot.send_message(
            chat_id=chat_id,
            text=prompt,
            parse_mode='HTML'
        )
        context.user_data["state"] = globals.STATES["admin_broadcast"]

    elif data == 'adm_normal':
        query.message.delete()
        from methods import send_main_menu
        db_user = db.get_user_by_chat_id(chat_id)
        lang_id = db_user.get("lang_id", 1) if db_user else 1
        send_main_menu(context, chat_id, lang_id)
        context.user_data["state"] = globals.STATES["menu"]

    elif data == 'adm_back':
        db_user = db.get_user_by_chat_id(chat_id)
        lang_id = db_user.get("lang_id", 1) if db_user else 1
        text = (
            "👑 <b>SISTEMA BOSHQARUV PANELI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👋 <b>Xush kelibsiz, Hurmatli Boshqaruvchi!</b>\n"
            "🟢 Tizim holati: <b>Barqaror (Online)</b>\n\n"
            "<i>Barcha ma'lumotlar va boshqaruv funksiyalari sizning ixtiyoringizda. Quyidagi menyudan kerakli bo'limni tanlang:</i>"
        )
        query.edit_message_text(
            text=text,
            reply_markup=get_admin_menu_keyboard(lang_id),
            parse_mode='HTML'
        )

def handle_admin_broadcast(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return

    chat_id = update.effective_chat.id
    message_text = update.message.text
    
    if not message_text:
        return
        
    users = db.get_all_users()
    success = 0
    fail = 0
    
    for u in users:
        u_chat_id = u.get('chat_id')
        if not u_chat_id:
            continue
        try:
            context.bot.send_message(chat_id=u_chat_id, text=message_text, parse_mode='HTML')
            success += 1
        except Exception:
            fail += 1
            
    result_text = (
        "📢 <b>XABAR YUBORILDI!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>Muvaffaqiyatli:</b> <i>{success} ta foydalanuvchiga</i>\n"
        f"❌ <b>Xatolik (yoki block):</b> <i>{fail} ta</i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    update.message.reply_text(text=result_text, parse_mode='HTML')
    
    context.user_data["state"] = globals.STATES["menu"]
    
    db_user = db.get_user_by_chat_id(user_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    text = (
        "👑 <b>SISTEMA BOSHQARUV PANELI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👋 <b>Xush kelibsiz, Hurmatli Boshqaruvchi!</b>\n"
        "🟢 Tizim holati: <b>Barqaror (Online)</b>\n\n"
        "<i>Barcha ma'lumotlar va boshqaruv funksiyalari sizning ixtiyoringizda. Quyidagi menyudan kerakli bo'limni tanlang:</i>"
    )
    
    # Return to admin menu automatically
    update.message.reply_text(
        text=text,
        reply_markup=get_admin_menu_keyboard(lang_id),
        parse_mode='HTML'
    )
