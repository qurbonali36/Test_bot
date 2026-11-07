import globals
from database import Database
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import os

db = Database("tg_bot.db")

def start_check_cert(update, context):
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    
    context.user_data["state"] = globals.STATES["check_cert"]
    
    texts = {
        1: "🎓 <b>Sertifikat tekshirish</b>\n\nSertifikat ID sini kiriting (masalan, CERT-261004-123456):",
        2: "🎓 <b>Проверка сертификата</b>\n\nВведите ID сертификата (например, CERT-261004-123456):",
        3: "🎓 <b>Check certificate</b>\n\nEnter the Certificate ID (e.g., CERT-261004-123456):"
    }
    
    update.message.reply_text(texts.get(lang_id, texts[1]), parse_mode='HTML')

def handle_check_cert_input(update, context):
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    
    cert_id = update.message.text.strip()
    cert = db.get_certificate(cert_id)
    
    if not cert:
        texts_err = {
            1: "❌ Sertifikat topilmadi! ID ni to'g'ri kiritganingizga ishonch hosil qiling.",
            2: "❌ Сертификат не найден! Убедитесь, что вы правильно ввели ID.",
            3: "❌ Certificate not found! Make sure you entered the ID correctly."
        }
        update.message.reply_text(texts_err.get(lang_id, texts_err[1]))
        return
        
    png_path = cert.get('png_path', '')
    pdf_path = cert.get('pdf_path', '')
    
    msg = f"🎓 <b>Sertifikat topildi!</b>\n\n👤 Egasi: <b>{cert.get('recipient_name', '')}</b>\n📝 Test: <b>{cert.get('test_name', '')}</b>\n📊 Natija: <b>{cert.get('score', 0)}%</b>\n🆔 ID: <code>{cert_id}</code>"
    
    if pdf_path and os.path.exists(pdf_path):
        try:
            with open(pdf_path, 'rb') as doc:
                update.message.reply_document(document=doc, caption=msg, parse_mode='HTML')
            context.user_data["state"] = globals.STATES["menu"]
            from methods import send_main_menu
            send_main_menu(context, chat_id, lang_id)
            return
        except Exception:
            pass
            
    if png_path and os.path.exists(png_path):
        try:
            with open(png_path, 'rb') as photo:
                update.message.reply_photo(photo=photo, caption=msg, parse_mode='HTML')
            context.user_data["state"] = globals.STATES["menu"]
            from methods import send_main_menu
            send_main_menu(context, chat_id, lang_id)
        except Exception:
            update.message.reply_text("Xatolik yuz berdi faylni yuborishda.")
    else:
        update.message.reply_text("Fayllar topilmadi.")
