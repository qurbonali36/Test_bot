from database import Database
from methods import send_main_menu
import globals

db = Database("tg_bot.db")


def main_messages(update, context):
    """Asosiy xabar yo'naltiruvchisi — state va matn asosida to'g'ri handler ga yuboradi."""
    if not update.message or not update.message.text:
        return

    text = update.message.text
    state = context.user_data.get("state", 0)
    chat_id = update.effective_user.id
    db.update_last_active(chat_id)
    db_user = db.get_user_by_chat_id(chat_id)

    # ── Ro'yxatdan o'tmagan yoki registratsiya jarayonida ──
    if state == globals.STATES["reg"] or not db_user or not db_user.get("lang_id"):
        from messages import message_handler
        message_handler(update, context)
        return

    lang_id = db_user["lang_id"] or 1

    # ── Daily Reward Check ──
    from daily_reward import check_and_give_daily_reward
    check_and_give_daily_reward(context, chat_id, lang_id)

    # ── Fikr bildirish (matn kutilmoqda) ──
    if state == globals.STATES["feedback"]:
        from feedback import handle_feedback_input
        handle_feedback_input(update, context)
        return

    # ── Sozlamalar: ism/familiya/telefon o'zgartirish ──
    if state in (globals.STATES["edit_name"], globals.STATES["edit_lastname"], globals.STATES["edit_phone"]):
        from settings import handle_settings_input
        handle_settings_input(update, context)
        return

    # ── Admin broadcast ──
    if state == globals.STATES["admin_broadcast"]:
        from admin import handle_admin_broadcast
        handle_admin_broadcast(update, context)
        return

    # ── Test tahrirlash: yangi nom/tavsif ──
    if state in (globals.STATES["edit_test_title"], globals.STATES["edit_test_desc"]):
        from edit_test import handle_edit_input
        handle_edit_input(update, context)
        return

    # ── Qidiruv matni kutilmoqda ──
    if state == globals.STATES["search"]:
        from search import handle_search_input
        handle_search_input(update, context)
        return

    # ── Muammo xabar qilish (matn kutilmoqda) ──
    if state == 11:
        from help_command import handle_report_input
        handle_report_input(update, context)
        return

    # ── Sertifikat tekshirish (ID kutilmoqda) ──
    if state == globals.STATES.get("check_cert", 12):
        from cert_check import handle_check_cert_input
        handle_check_cert_input(update, context)
        return

    # ── Asosiy menyu tugmalari ──
    if state == globals.STATES["menu"]:
        # Admin panel buttons
        from config import ADMIN_ID
        if str(chat_id) == str(ADMIN_ID) and context.user_data.get("is_admin_mode"):
            from admin_ext import handle_admin_text, handle_admin_text_ext
            if handle_admin_text(update, context):
                return
            if handle_admin_text_ext(update, context):
                return

        # ⬅️ Orqaga
        if text == globals.BTN_BACK[lang_id]:
            send_main_menu(context, chat_id, lang_id)
            return

        # 📝 Test ishlash
        if text == globals.BTN_TEST_WORKING[lang_id]:
            from test_working import check_pressed
            check_pressed(update, context)
            return

        # 📖 Qo'llanma
        if text == globals.BTN_GUIDE[lang_id]:
            from guide import show_guide
            show_guide(update, context)
            return

        # ✍️ Fikr bildirish
        if text == globals.BTN_COMMENTS[lang_id]:
            from feedback import start_feedback
            start_feedback(update, context)
            return

        # ⚙️ Sozlamalar
        if text == globals.BTN_SETTINGS[lang_id]:
            from settings import show_settings
            show_settings(update, context)
            return

        # 🏆 Reyting
        if text == globals.BTN_LEADERBOARD[lang_id]:
            from leaderboard import show_leaderboard_menu
            show_leaderboard_menu(update, context)
            return

        # 🎯 Kundalik test
        if text == globals.BTN_DAILY[lang_id]:
            from daily_challenge import show_daily_challenge
            show_daily_challenge(update, context)
            return

        # 👤 Profil
        if text == globals.BTN_PROFILE[lang_id]:
            from gamification import show_profile
            show_profile(update, context)
            return

        # ⚔️ Bellashuv
        if text == globals.BTN_DUEL[lang_id]:
            from duel import show_duel_menu
            show_duel_menu(update, context)
            return

        # 🔍 Qidirish
        if text == globals.BTN_SEARCH[lang_id]:
            from search import start_search
            start_search(update, context)
            return

        # 📜 Test tarixi
        if text == globals.BTN_HISTORY[lang_id]:
            from test_history import show_test_history
            show_test_history(update, context)
            return

        # 🔖 Saqlanganlar
        if text == globals.BTN_BOOKMARKS[lang_id]:
            from bookmarks import show_bookmarks
            show_bookmarks(update, context)
            return

        # ❓ Yordam
        if text == globals.BTN_HELP[lang_id]:
            from help_command import show_help
            show_help(update, context)
            return

        # 🔔 Bildirishnomalar
        if text == globals.BTN_NOTIFICATIONS[lang_id]:
            from notifications import show_notification_settings
            show_notification_settings(update, context)
            return

        # 🎓 Sertifikat tekshirish
        if text == globals.BTN_CHECK_CERT[lang_id]:
            from cert_check import start_check_cert
            start_check_cert(update, context)
            return
            
        # 🎯 Maqsadlar
        if text == globals.MENU_MISSIONS[lang_id]:
            from missions import show_missions
            show_missions(update, context)
            return
            
        # 🏟️ Turnir
        if text == globals.MENU_TOURNAMENT[lang_id]:
            from tournament import show_tournaments
            show_tournaments(update, context)
            return

        # 👥 Do'stlar
        if text == globals.MENU_FRIENDS[lang_id]:
            from friends import show_friends_menu
            show_friends_menu(update, context)
            return

        # 🧠 Takrorlash
        if text == globals.SPACED_REP_TITLE[lang_id]:
            from spaced_repetition import show_spaced_repetition
            show_spaced_repetition(update, context)
            return
        # Fan tanlash (Test ishlash jarayonida)
        from test_working import check_object
        if check_object(update, context):
            return

    # ── Default: registratsiya tekshiruvi ──
    from messages import message_handler
    message_handler(update, context)
