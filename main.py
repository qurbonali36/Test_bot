from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, PollAnswerHandler
from database import Database
from register import check
from main_messages import main_messages
from inlines import check_inlines
from quest_poll import cancel_test, get_poll_answers, send_polls
from get_poll_answers import conv_handler
from deeplink import handle_deeplink
import globals
import time
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

from config import TOKEN

Database.create_database()

db = Database("tg_bot.db")


def start_handler(update, context):
    chat_type = update.message.chat.type
    args = context.args
    user_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(user_id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1

    # ── Guruhda /start ──
    if chat_type in ['group', 'supergroup']:
        if args:
            yashirin_soz = args[0]
            qismlar = yashirin_soz.split("_", 1)
            if len(qismlar) == 2:
                egasi_id = qismlar[0]
                test_id = qismlar[1]
                
                # Load test info
                test_meta = db.get_test_meta(test_id)
                creator = db.get_user_by_chat_id(int(egasi_id))
                creator_name = f"{creator.get('first_name', '')} {creator.get('last_name', '')}".strip() if creator else "Noma'lum"
                
                amount = test_meta.get("amount", 0) if test_meta else 0
                title = test_meta.get("title", "Test") if test_meta else test_id
                desc = test_meta.get("description", "") if test_meta else ""
                point = test_meta.get("point_per_q", 1) if test_meta else 1
                time_per_q = test_meta.get("time_per_q", 10) if test_meta else 10
                
                total_seconds = time_per_q * amount
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                time_parts = []
                if hours > 0: time_parts.append(f"{hours} {globals.HOUR[lang_id]}")
                if minutes > 0: time_parts.append(f"{minutes} {globals.MINUTE[lang_id]}")
                if seconds > 0 or total_seconds == 0: time_parts.append(f"{seconds} {globals.SECOND[lang_id]}")
                time_text = " ".join(time_parts)
                
                info_text = globals.get_deeplink_test_info(lang_id, title, desc, amount, time_text, creator_name, point)
                
                from telegram import InlineKeyboardMarkup, InlineKeyboardButton
                keyboard = [
                    [InlineKeyboardButton(globals.BTN_START_TEST[lang_id], callback_data=f'groupstart_{egasi_id}_{test_id}')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                update.message.reply_text(
                    text=info_text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
        else:
            update.message.reply_text(
                globals.TEST_MUST_BE_FORWARDED[lang_id], parse_mode="HTML"
            )
        return

    # ── Shaxsiy chatda /start ──
    if chat_type == 'private':
        # Deep link bilan kelgan bo'lsa
        if args:
            yashirin_soz = args[0]
            # ── Duel deeplink ──
            if yashirin_soz.startswith("duel_"):
                duel_id_str = yashirin_soz.replace("duel_", "")
                if not db_user or not db_user.get("phone_number"):
                    check(update, context)
                    context.user_data["pending_deeplink"] = yashirin_soz
                    return
                from duel import handle_duel_deeplink
                handle_duel_deeplink(update, context, duel_id_str)
                return
            # ── Certificate deeplink ──
            if yashirin_soz.startswith("cert_"):
                cert_id = yashirin_soz.replace("cert_", "")
                from deeplink import handle_cert_deeplink
                handle_cert_deeplink(update, context, cert_id)
                return
            # ── Referral deeplink ──
            if yashirin_soz.startswith("ref_"):
                if not db_user or not db_user.get("phone_number"):
                    check(update, context)
                    context.user_data["pending_deeplink"] = yashirin_soz
                    return
                from friends import process_referral
                process_referral(update, context, yashirin_soz)
                return
            qismlar = yashirin_soz.split("_", 1)
            if len(qismlar) == 2:
                egasi_id = qismlar[0]
                test_id = qismlar[1]
                # Avval registratsiyani tekshirish
                if not db_user or not db_user.get("phone_number"):
                    check(update, context)
                    # Deep link ma'lumotini saqlab qo'yamiz
                    context.user_data["pending_deeplink"] = f"{egasi_id}_{test_id}"
                    return
                handle_deeplink(update, context, egasi_id, test_id)
                return
        check(update, context)


def contact_handler(update, context):
    message = update.message.contact.phone_number
    user = update.message.from_user
    db.update_user_data(user.id, "phone_number", message)

    # Agar pending deeplink bo'lsa, test infoni ko'rsatamiz
    pending = context.user_data.get("pending_deeplink")
    if pending:
        del context.user_data["pending_deeplink"]
        qismlar = pending.split("_", 1)
        if len(qismlar) == 2:
            handle_deeplink(update, context, qismlar[0], qismlar[1])
            return
    check(update, context)


def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Buyruqlar
    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(CommandHandler('stop', cancel_test))

    # Admin buyrug'i
    from admin import admin_command
    dispatcher.add_handler(CommandHandler('admin', admin_command))

    # Test yaratish (ConversationHandler)
    dispatcher.add_handler(conv_handler())
    
    from test_wizard import get_wizard_handler
    dispatcher.add_handler(get_wizard_handler())

    # Matnli xabarlar
    dispatcher.add_handler(MessageHandler(Filters.text, main_messages))
    dispatcher.add_handler(MessageHandler(Filters.contact, contact_handler))

    # Barcha turdagi media xabarlarni tutish uchun
    from admin_ext import handle_admin_media_ext
    dispatcher.add_handler(MessageHandler(Filters.photo | Filters.video | Filters.audio | Filters.document | Filters.voice, handle_admin_media_ext))

    # Inline tugmalar
    dispatcher.add_handler(CallbackQueryHandler(check_inlines))

    # So'rovnoma javoblari
    dispatcher.add_handler(PollAnswerHandler(get_poll_answers))

    # ── Run Web Server in Background ──
    from threading import Thread
    import web_app
    import os

    def run_flask():
        port = int(os.getenv('PORT', 5000))
        # use_reloader=False is crucial when running inside a thread
        web_app.app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logging.info(f"Flask Web Server started on port {os.getenv('PORT', 5000)}")

    from scheduler import init_scheduler
    init_scheduler(updater.job_queue)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
