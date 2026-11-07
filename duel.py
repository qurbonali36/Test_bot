import globals
from database import Database
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

db = Database("tg_bot.db")


def show_duel_menu(update, context):
    """Duel menyusini ko'rsatish."""
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    keyboard = [
        [InlineKeyboardButton(globals.BTN_DUEL_CREATE[lang_id], callback_data='duel_create')],
        [InlineKeyboardButton(globals.BTN_RANDOM_MATCH[lang_id], callback_data='duel_random')],
        [InlineKeyboardButton(globals.BTN_DUEL_LIST[lang_id], callback_data='duel_history')],
        [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='back')],
        [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = globals.TEXT_DUEL_MENU[lang_id]

    if update.message:
        update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


def handle_duel_callback(update, context):
    """Duel callback."""
    query = update.callback_query
    query.answer()
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1
    data = query.data

    back_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='duel_menu')],
        [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
    ])

    if data == 'duel_menu':
        show_duel_menu(update, context)
        return
        
    if data == 'duel_random':
        match_id = db.find_random_match(chat_id)
        if match_id:
            # Join the match
            db.accept_duel(match_id, chat_id)
            context.user_data['active_duel_id'] = match_id
            duel = db.get_duel(match_id)
            
            # test_id dan egasi_id ni topish
            test_id = duel['test_id']
            from deeplink import handle_deeplink
            test_meta = db.get_test_meta(test_id)
            if test_meta:
                egasi_id = str(test_meta.get('chat_id', ''))
                query.edit_message_text("✅ Raqib topildi! Test boshlanmoqda...", reply_markup=None)
                handle_deeplink(update, context, egasi_id, test_id)
            else:
                query.edit_message_text("⚠️ Xatolik yuz berdi. Test topilmadi.", reply_markup=back_kb)
        else:
            msg = {
                1: "😔 Hozircha bo'sh raqiblar yo'q. O'zingiz duel yarating!",
                2: "😔 Пока нет свободных противников. Создайте свою дуэль!",
                3: "😔 No available opponents right now. Create your own duel!"
            }[lang_id]
            query.edit_message_text(msg, reply_markup=back_kb)
        return

    if data == 'duel_create':
        # Foydalanuvchi testlarini ko'rsatish
        tests = db.get_user_tests(chat_id)
        if not tests:
            query.edit_message_text(
                globals.TEXT_DUEL_NO_TESTS[lang_id],
                parse_mode='HTML', reply_markup=back_kb
            )
            return

        keyboard = []
        for t in tests[:10]:
            title = t.get('title', 'Test')
            test_id = t.get('test_id', '')
            keyboard.append([InlineKeyboardButton(f"⚔️ {title}", callback_data=f'duel_pick_{test_id}')])
        keyboard.append([InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='duel_menu')])
        keyboard.append([InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')])

        query.edit_message_text(
            globals.TEXT_DUEL_CHOOSE_TEST[lang_id],
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data.startswith('duel_pick_'):
        test_id = data.replace('duel_pick_', '')
        duel_id = db.create_duel(chat_id, test_id)
        bot_username = context.bot.username
        link = f"https://t.me/{bot_username}?start=duel_{duel_id}"

        text = globals.TEXT_DUEL_CREATED[lang_id].format(link=link)
        share_url = f"https://t.me/share/url?url={link}&text=⚔️ Duelga chaqiraman!"
        keyboard = [
            [InlineKeyboardButton(globals.BTN_SHARE[lang_id], url=share_url)],
            [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='duel_menu')],
            [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
        ]
        query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith('duel_test_'):
        test_id = data.replace('duel_test_', '')
        # Yangi duel yaratish
        duel_id = db.create_duel(chat_id, test_id)
        bot_username = context.bot.username
        link = f"https://t.me/{bot_username}?start=duel_{duel_id}"

        text = globals.TEXT_DUEL_CREATED[lang_id].format(link=link)
        import urllib.parse
        share_text = urllib.parse.quote("⚔️ Duelga chaqiraman!")
        share_url = f"https://t.me/share/url?url={link}&text={share_text}"
        keyboard = [
            [InlineKeyboardButton(globals.BTN_SHARE[lang_id], url=share_url)],
            [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='duel_menu')],
            [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
        ]
        query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == 'duel_history':
        duels = db.get_my_duels(chat_id, 10)
        if not duels:
            query.edit_message_text(
                globals.TEXT_DUEL_EMPTY[lang_id],
                parse_mode='HTML', reply_markup=back_kb
            )
            return

        text = "<b>⚔️ Duel tarixi</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for d in duels:
            ch_name = f"{d.get('ch_name', '')} {d.get('ch_lname', '')}".strip() or "???"
            op_name = f"{d.get('op_name', '')} {d.get('op_lname', '')}".strip() or "Kutilmoqda"
            status = d.get('status', 'pending')
            status_emoji = "⏳" if status == 'pending' else "🏁" if status == 'completed' else "▶️"
            ch_score = d.get('challenger_score', 0)
            op_score = d.get('opponent_score', 0)

            text += f"{status_emoji} <b>{ch_name}</b> vs <b>{op_name}</b>\n"
            if status == 'completed':
                text += f"   └ {ch_score} : {op_score}\n"
            text += "\n"

        query.edit_message_text(text, parse_mode='HTML', reply_markup=back_kb)
        return


def handle_duel_deeplink(update, context, duel_id_str):
    """Duel deeplink orqali kelganlarni boshqarish."""
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    try:
        duel_id = int(duel_id_str)
    except:
        return

    duel = db.get_duel(duel_id)
    if not duel:
        return

    if duel['status'] != 'pending':
        context.bot.send_message(chat_id=chat_id, text="⚠️ Bu duel allaqachon boshlangan yoki tugagan.", parse_mode='HTML')
        return

    if duel['challenger_id'] == chat_id:
        context.bot.send_message(chat_id=chat_id, text="⚠️ O'zingiz yaratgan duelga o'zingiz qo'shila olmaysiz!", parse_mode='HTML')
        return

    # Duelni qabul qilish
    db.accept_duel(duel_id, chat_id)
    context.user_data['active_duel_id'] = duel_id

    # Testni boshlash
    test_id = duel['test_id']
    from deeplink import handle_deeplink
    # test_id dan egasi_id ni topish
    test_meta = db.get_test_meta(test_id)
    if test_meta:
        egasi_id = str(test_meta.get('chat_id', ''))
        handle_deeplink(update, context, egasi_id, test_id)
    else:
        context.bot.send_message(chat_id=chat_id, text="⚠️ Test topilmadi.", parse_mode='HTML')
