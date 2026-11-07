import json
import os
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import globals
from database import Database

db = Database("tg_bot.db")

def handle_deeplink(update, context, egasi_id, test_id):
    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1

    meta = db.get_test_meta(test_id)
    
    amount = 0
    title = test_id
    description = ""
    point_per_q = 1
    time_per_q = 10
    
    if meta:
        title = meta.get("title", title)
        description = meta.get("description", description)
        amount = meta.get("amount", amount)
        point_per_q = meta.get("point_per_q", point_per_q)
        time_per_q = meta.get("time_per_q", time_per_q)
    
    if not meta or amount == 0:
        file_path = f'json_files/{egasi_id}.json'
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_questions = json.load(f)
                current_test = None
                questions = []
                for q in all_questions:
                    if q.get('test_id') == test_id:
                        current_test = test_id
                        questions.append(q)
                    elif current_test == test_id and 'test_id' not in q:
                        questions.append(q)
                    elif current_test == test_id and 'test_id' in q:
                        break
                amount = len(questions)
            except Exception as e:
                amount = 0
                
    creator_user = db.get_user_by_chat_id(int(egasi_id))
    if creator_user:
        creator_name = f'<a href="tg://user?id={egasi_id}">{creator_user["first_name"]} {creator_user.get("last_name","")}</a>'
    else:
        creator_name = f'ID: {egasi_id}'
        
    total_time = time_per_q * amount
    h, r = divmod(total_time, 3600)
    m, s = divmod(r, 60)
    
    time_parts = []
    if h > 0: time_parts.append(f"{h} {globals.HOUR[lang_id]}")
    if m > 0: time_parts.append(f"{m} {globals.MINUTE[lang_id]}")
    if s > 0 or len(time_parts) == 0: time_parts.append(f"{s} {globals.SECOND[lang_id]}")
    time_text = " ".join(time_parts)
    
    text = globals.get_deeplink_test_info(lang_id, title, description, amount, time_text, creator_name, point_per_q)
    
    keyboard = [
        [InlineKeyboardButton(globals.BTN_START_TEST[lang_id], callback_data=f'deepstart_{egasi_id}_{test_id}')],
        [InlineKeyboardButton(globals.BTN_HOME[lang_id], callback_data='home')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


def handle_deepstart_callback(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    
    data = query.data
    parts = data.split('_')
    if len(parts) >= 3:
        egasi_id = parts[1]
        test_id = '_'.join(parts[2:])
    else:
        query.answer("Error parsing callback data", show_alert=True)
        return
        
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
        except Exception as e:
            pass

    if not questions:
        query.answer("Questions not found or file missing", show_alert=True)
        return
        
    context.user_data['savollar_bazasi'] = questions
    context.user_data['amount_quest'] = len(questions)
    context.user_data['current_quest'] = 0
    context.user_data['correct_ans'] = 0
    context.user_data['chat_id'] = chat_id
    context.user_data['test_id'] = test_id
    
    user = update.effective_user
    name = user.first_name
    user_id = user.id
    context.user_data['name_link'] = f'<a href="tg://user?id={user_id}">{name}</a>'
    
    meta = db.get_test_meta(test_id)
    point = meta['point_per_q'] if meta and 'point_per_q' in meta else 1
    
    query.answer()
    
    active_duel_id = context.user_data.get('active_duel_id')
    duel = None
    challenger_id = None
    challenger_ud = None
    ch_msg = None
    
    if active_duel_id:
        duel = db.get_duel(active_duel_id)
        if duel and duel['status'] == 'active':
            challenger_id = duel['challenger_id']
            challenger_ud = context.dispatcher.user_data.get(challenger_id, {})
            challenger_ud['savollar_bazasi'] = questions
            challenger_ud['amount_quest'] = len(questions)
            challenger_ud['current_quest'] = 0
            challenger_ud['correct_ans'] = 0
            challenger_ud['chat_id'] = challenger_id
            challenger_ud['test_id'] = test_id
            challenger_ud['active_duel_id'] = active_duel_id
            ch_user = db.get_user_by_chat_id(challenger_id)
            ch_name = ch_user.get('first_name', 'Foydalanuvchi') if ch_user else 'Foydalanuvchi'
            challenger_ud['name_link'] = f'<a href="tg://user?id={challenger_id}">{ch_name}</a>'
            context.dispatcher.user_data[challenger_id] = challenger_ud

    try:
        query.edit_message_text(text=globals.READY_3[lang_id], parse_mode='HTML')
        if challenger_id:
            ch_msg = context.bot.send_message(chat_id=challenger_id, text=globals.READY_3.get(lang_id, globals.READY_3[1]), parse_mode='HTML')
        
        time.sleep(1.5)
        
        query.edit_message_text(text=globals.READY_2[lang_id], parse_mode='HTML')
        if ch_msg:
            context.bot.edit_message_text(chat_id=challenger_id, message_id=ch_msg.message_id, text=globals.READY_2.get(lang_id, globals.READY_2[1]), parse_mode='HTML')
            
        time.sleep(1.5)
        
        query.edit_message_text(text=globals.READY_1[lang_id], parse_mode='HTML')
        if ch_msg:
            context.bot.edit_message_text(chat_id=challenger_id, message_id=ch_msg.message_id, text=globals.READY_1.get(lang_id, globals.READY_1[1]), parse_mode='HTML')
            
        time.sleep(1)
        query.message.delete()
        if ch_msg:
            context.bot.delete_message(chat_id=challenger_id, message_id=ch_msg.message_id)
    except Exception:
        pass
        
    from quest_poll import send_polls
    
    if challenger_id and challenger_ud is not None:
        class DummyContext:
            def __init__(self, bot, job_queue, bot_data, user_data, dispatcher):
                self.bot = bot
                self.job_queue = job_queue
                self.bot_data = bot_data
                self.user_data = user_data
                self.dispatcher = dispatcher
                self.job = None
        
        ch_ctx = DummyContext(context.bot, context.job_queue, context.bot_data, challenger_ud, context.dispatcher)
        send_polls(ch_ctx, point=point)
        
    send_polls(context, point=point)


def handle_cert_deeplink(update, context, cert_id):
    chat_id = update.effective_chat.id
    cert = db.get_certificate(cert_id)
    if not cert:
        update.message.reply_text('Sertifikat topilmadi!')
        return
    png_path = cert.get('png_path', '')
    pdf_path = cert.get('pdf_path', '')
    import os
    # Prefer sending PDF (high quality) if available, otherwise fallback to PNG
    if pdf_path and os.path.exists(pdf_path):
        try:
            with open(pdf_path, 'rb') as doc:
                msg = 'Sertifikat egasi: ' + cert.get('recipient_name', '') + '\nTest: ' + cert.get('test_name', '') + '\nNatija: ' + str(cert.get('score', 0)) + '%\nID: ' + cert_id
                update.message.reply_document(document=doc, caption=msg)
                return
        except Exception:
            pass
    # Fallback to PNG
    if not os.path.exists(png_path):
        update.message.reply_text('Sertifikat fayli topilmadi!')
        return
    try:
        with open(png_path, 'rb') as photo:
            msg = 'Sertifikat egasi: ' + cert.get('recipient_name', '') + '\nTest: ' + cert.get('test_name', '') + '\nNatija: ' + str(cert.get('score', 0)) + '%\nID: ' + cert_id
            update.message.reply_photo(photo=photo, caption=msg)
    except Exception:
        update.message.reply_text('Xatolik yuz berdi.')
