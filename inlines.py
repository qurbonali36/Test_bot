from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from json_load import json_load
from database import Database
from quest_poll import send_polls
import globals
import time

db = Database("tg_bot.db")


def check_inlines(update, context):
    """Barcha inline callback'larni yo'naltiruvchi markaziy handler."""
    query = update.callback_query
    data = query.data
    user_id = update.effective_user.id
    db.update_last_active(user_id)
    db_user = db.get_user_by_chat_id(user_id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    
    # ── Daily Reward Check ──
    from daily_reward import check_and_give_daily_reward
    check_and_give_daily_reward(context, user_id, lang_id)

    # ── Eskirgan tugma ──
    if not context.user_data and data.startswith("class_"):
        query.answer(globals.BTN_DEPRECATED[lang_id], show_alert=True)
        return
    query.answer()
    if data.startswith("sr_"):
        from spaced_repetition import handle_sr_callback
        handle_sr_callback(update, context)
        return

    if data.startswith("friends_"):
        from friends import handle_friends_callback
        handle_friends_callback(update, context)
        return

    if data.startswith("tourney_"):
        from tournament import handle_tournament_callback
        handle_tournament_callback(update, context)
        return

    # ── Sinf tanlash (class_5, class_6, ...) ──
    if data.startswith("class_"):
        user_class = int(data.split("_")[1])
        user_object = context.user_data.get("object", "")
        test_id_nomi = str(user_object).replace(".json", "").replace("json_files/", "")
        
        context.user_data["test_time_limit"] = 5
        display_time = globals.TEXT_CREATE_TIME_SEC.get(lang_id, globals.TEXT_CREATE_TIME_SEC[1]).format(5)
        
        inline_button = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➖", callback_data=f"take_minus_{test_id_nomi}"),
                InlineKeyboardButton(display_time, callback_data=f"take_curr_{test_id_nomi}"),
                InlineKeyboardButton("➕", callback_data=f"take_plus_{test_id_nomi}")
            ],
            [InlineKeyboardButton(text=globals.WORK_TEST[lang_id], callback_data=f"WORK_TEST_{test_id_nomi}")],
            [InlineKeyboardButton(text=globals.BTN_BACK[lang_id], callback_data="back")],
            [InlineKeyboardButton(text=globals.BTN_HOME[lang_id], callback_data="home")]
        ])
        info = json_load(update, context, user_object, user_class)
        context.bot.send_message(
            text=info, chat_id=update.effective_user.id,
            parse_mode="HTML", reply_markup=inline_button
        )
        context.user_data["current_quest"] = 0
        context.user_data["correct_ans"] = 0
        context.user_data["chat_id"] = update.effective_chat.id
        return

    # ── Test vaqtini o'zgartirish ──
    if data.startswith("take_minus_") or data.startswith("take_plus_"):
        action = data.split("_")[1]
        test_id_nomi = data.split("_", 2)[2]
        
        current = context.user_data.get("test_time_limit", 5)
        
        if action == "minus":
            if current <= 5:
                # O'zbekcha yozib qo'ydim, globaldan olish ham mumkin, hozircha alert shunday bo'laqolsin
                query.answer("Eng kam vaqt: 5 soniya!" if lang_id == 1 else "Минимум: 5 секунд!", show_alert=True)
                return
            current = max(5, current - 5)
        elif action == "plus":
            if current >= 1800:
                query.answer("Eng ko'p vaqt: 30 minut!" if lang_id == 1 else "Максимум: 30 минут!", show_alert=True)
                return
            current = min(1800, current + 5)
            
        context.user_data["test_time_limit"] = current
        
        if current < 60:
            display_time = globals.TEXT_CREATE_TIME_SEC.get(lang_id, globals.TEXT_CREATE_TIME_SEC[1]).format(current)
        else:
            display_time = globals.TEXT_CREATE_TIME_MIN_SEC.get(lang_id, globals.TEXT_CREATE_TIME_MIN_SEC[1]).format(current//60, current%60)
            
        inline_button = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➖", callback_data=f"take_minus_{test_id_nomi}"),
                InlineKeyboardButton(display_time, callback_data=f"take_curr_{test_id_nomi}"),
                InlineKeyboardButton("➕", callback_data=f"take_plus_{test_id_nomi}")
            ],
            [InlineKeyboardButton(text=globals.WORK_TEST[lang_id], callback_data=f"WORK_TEST_{test_id_nomi}")],
            [InlineKeyboardButton(text=globals.BTN_BACK[lang_id], callback_data="back")],
            [InlineKeyboardButton(text=globals.BTN_HOME[lang_id], callback_data="home")]
        ])
        try:
            query.edit_message_reply_markup(reply_markup=inline_button)
        except:
            pass
        return

    # ── Testni boshlash ──
    if data.startswith("WORK_TEST_"):
        test_id = data.replace("WORK_TEST_", "")
        context.user_data["chat_id"] = update.effective_chat.id
        context.user_data["test_id"] = test_id
        query.edit_message_text(globals.READY_3[lang_id])
        time.sleep(1.5)
        query.edit_message_text(globals.READY_2[lang_id])
        time.sleep(1.5)
        query.edit_message_text(globals.READY_1[lang_id])
        time.sleep(1)
        name = update.effective_user.first_name
        user_id = update.effective_user.id
        context.user_data["name_link"] = f'<a href="tg://user?id={user_id}">{name}</a>'
        context.user_data["current_quest"] = 0
        context.user_data["correct_ans"] = 0
        send_polls(context)
        return

    # ── Qaytadan urinish ──
    if data.startswith("WORK_AGAIN_"):
        test_id = data.replace("WORK_AGAIN_", "")
        
        # Test ma'lumotlarini qayta yuklash
        meta = db.get_test_meta(test_id)
        if meta:
            egasi_id = str(meta.get("chat_id", ""))
        else:
            egasi_id = ""
        
        import json, os
        file_path = f'json_files/{egasi_id}.json'
        questions = []
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_questions = json.load(f)
                current_test = None
                for q in all_questions:
                    if q.get('test_id') == test_id:
                        current_test = test_id
                        questions.append(q)
                    elif current_test == test_id and 'test_id' not in q:
                        questions.append(q)
                    elif current_test == test_id and 'test_id' in q:
                        break
            except Exception:
                pass
        
        if not questions:
            query.answer("❌ Savollar topilmadi! / Questions not found!", show_alert=True)
            return
        
        context.user_data['savollar_bazasi'] = questions
        context.user_data['amount_quest'] = len(questions)
        context.user_data['test_id'] = test_id
        context.user_data['current_quest'] = 0
        context.user_data['correct_ans'] = 0
        context.user_data['speed_bonus'] = 0
        context.user_data['chat_id'] = update.effective_chat.id
        name = update.effective_user.first_name
        uid = update.effective_user.id
        context.user_data['name_link'] = f'<a href="tg://user?id={uid}">{name}</a>'
        
        query.message.delete()
        send_polls(context)
        return

    # ── Deep link orqali test boshlash ──
    if data.startswith("deepstart_") or data.startswith("groupstart_"):
        from deeplink import handle_deepstart_callback
        # Make sure deeplink handles groupstart_ identically to deepstart_
        if data.startswith("groupstart_"):
            update.callback_query.data = data.replace('groupstart_', 'deepstart_')
        handle_deepstart_callback(update, context)
        return

    # ── Mening testlarim ──
    if data == "my_tests" or data == "mytests_list_back":
        from my_tests import show_my_tests
        show_my_tests(update, context)
        return

    if data.startswith("mytest_"):
        from my_tests import handle_mytest_callback
        handle_mytest_callback(update, context)
        return

    if data.startswith("del_test_"):
        from my_tests import handle_delete_test
        handle_delete_test(update, context)
        return

    # ── Test tahrirlash ──
    if data.startswith("edit_test_"):
        from edit_test import show_edit_menu
        test_id = data.replace("edit_test_", "")
        show_edit_menu(update, context, test_id)
        return

    if data.startswith("edtt_") or data.startswith("edtd_"):
        from edit_test import handle_edit_callback
        handle_edit_callback(update, context)
        return

    # ── Sozlamalar ──
    if data == "settings_back" or data.startswith("set_") or data.startswith("lang_"):
        from settings import handle_settings_callback
        handle_settings_callback(update, context)
        return

    # ── Qo'llanma — adminga murojaat ──
    if data == "contact_admin":
        from help_command import handle_help_callback
        # Redirect to help_contact_admin
        update.callback_query.data = 'help_contact_admin'
        handle_help_callback(update, context)
        return

    # ── Admin panel ──
    if data.startswith("adm_") or data.startswith("fb") or data.startswith("bc_") or data.startswith("del_inact_") or data.startswith("admlang_") or data.startswith("admin_reply_"):
        from admin import handle_admin_callback
        handle_admin_callback(update, context)
        return

    # ── Guruhda ishlash ──
    if data == "work_group":
        query.answer("⚠️ Ushbu tugma eskirgan! Iltimos, testni qaytadan yeching va yangi guruh tugmasidan foydalaning.", show_alert=True)
        return

    # ── Reyting (Leaderboard) ──
    if data.startswith("lb_"):
        from leaderboard import handle_leaderboard_callback
        handle_leaderboard_callback(update, context)
        return

    if data == "leaderboard":
        from leaderboard import show_leaderboard_menu
        show_leaderboard_menu(update, context)
        return

    # ── Analitika ──
    if data == "analytics":
        from analytics import show_analytics
        show_analytics(update, context)
        return

    # ── Kundalik test ──
    if data == "daily_start":
        from daily_challenge import start_daily_test
        start_daily_test(update, context)
        return

    # ── Xato javoblar ──
    if data == "wrong_answers":
        from wrong_answers import show_wrong_answers
        show_wrong_answers(update, context)
        return

    if data in ("wrong_ans", "wrong_clear"):
        from wrong_answers import handle_wrong_callback
        if data == "wrong_ans":
            from wrong_answers import show_wrong_answers
            show_wrong_answers(update, context)
        else:
            handle_wrong_callback(update, context)
        return

    # ── Duel ──
    if data.startswith("duel_"):
        from duel import handle_duel_callback
        handle_duel_callback(update, context)
        return

    # ── Xatolardan mashq ──
    if data == "practice_mistakes":
        from practice_mistakes import start_practice
        start_practice(update, context)
        return

    # ── Test tarixi ──
    if data.startswith("th_"):
        from test_history import handle_history_callback
        handle_history_callback(update, context)
        return

    # ── Saqlanganlar (Bookmarks) ──
    if data.startswith("bm_"):
        from bookmarks import handle_bookmark_callback
        handle_bookmark_callback(update, context)
        return

    if data.startswith("bookmark_"):
        from bookmarks import toggle_bookmark
        toggle_bookmark(update, context)
        return

    if data.startswith("test_start_"):
        test_id = data.replace("test_start_", "")
        meta = db.get_test_meta(test_id)
        if meta:
            egasi_id = str(meta.get('chat_id', ''))
            from deeplink import handle_deeplink
            handle_deeplink(update, context, egasi_id, test_id)
        else:
            query.answer("Test topilmadi!", show_alert=True)
        return

    # ── Qidiruv ──
    if data.startswith("search_"):
        from search import handle_search_callback
        handle_search_callback(update, context)
        return

    # ── Yordam ──
    if data.startswith("help_") or data.startswith("prob_"):
        from help_command import handle_help_callback
        handle_help_callback(update, context)
        return

    # ── Bildirishnomalar ──
    if data.startswith("notif_"):
        from notifications import handle_notification_callback
        handle_notification_callback(update, context)
        return

    # ── Kategoriyalar ──
    if data == "categories":
        cats = db.get_all_categories()
        lang_key = {1: 'name_uz', 2: 'name_ru', 3: 'name_en'}
        buttons = []
        for cat in cats:
            cat_name = cat.get(lang_key.get(lang_id, 'name_uz'), 'Test')
            emoji = cat.get('emoji', '📚')
            buttons.append([InlineKeyboardButton(f"{emoji} {cat_name}", callback_data=f"cat_{cat['id']}" )])
        buttons.append([InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')])
        text = globals.TEXT_CATEGORIES[lang_id]
        query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(buttons))
        return

    if data.startswith("cat_"):
        cat_id = int(data.replace("cat_", ""))
        tests = db.get_tests_by_category(cat_id, limit=10)
        cats = db.get_all_categories()
        lang_key = {1: 'name_uz', 2: 'name_ru', 3: 'name_en'}
        cat_info = next((c for c in cats if c['id'] == cat_id), None)
        cat_name = cat_info.get(lang_key.get(lang_id, 'name_uz'), '') if cat_info else ''
        cat_emoji = cat_info.get('emoji', '📚') if cat_info else '📚'
        
        if not tests:
            text = globals.TEXT_CAT_EMPTY[lang_id].format(cat=f"{cat_emoji} {cat_name}")
            buttons = [
                [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='categories')],
                [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
            ]
        else:
            text = globals.TEXT_CAT_TESTS[lang_id].format(cat=f"{cat_emoji} {cat_name}", count=len(tests))
            buttons = []
            for t in tests:
                title = t.get('title', 'Nomsiz')
                amount = t.get('amount', 0)
                plays = t.get('play_count', 0)
                creator = f"{t.get('first_name', '')} {t.get('last_name', '')}".strip()
                btn_text = f"📝 {title} ({amount} ta savol • {plays}x)"
                egasi_id = t.get('chat_id', '')
                test_id_val = t.get('test_id', '')
                buttons.append([InlineKeyboardButton(btn_text, callback_data=f"deepstart_{egasi_id}_{test_id_val}")])
            buttons.append([InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='categories')])
            buttons.append([InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')])
        
        query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(buttons))
        return

    # ── Orqaga ──
    if data == "back":
        from methods import send_main_menu
        query.message.delete()
        send_main_menu(context, update.effective_chat.id, lang_id)
        return

    # ── Bosh sahifa ──
    if data == "home":
        from methods import send_main_menu
        query.message.delete()
        send_main_menu(context, update.effective_chat.id, lang_id)
        return
