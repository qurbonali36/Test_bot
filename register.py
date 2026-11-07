from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from database import Database
import globals
import methods
import json
import uuid
import os
db = Database("tg_bot.db")


def check(update, context):
    user = update.message.from_user
    db_user = db.get_user_by_chat_id(user.id)

    if not db_user:
        db.create_user(user.id)
        buttons = [
            [KeyboardButton(text=globals.BTN_LANG_UZ), KeyboardButton(text=globals.BTN_LANG_RU)],
            [KeyboardButton(text=globals.BTN_LANG_EN)]
        ]
        update.message.reply_text(text=globals.WELCOME_TEXT)
        update.message.reply_text(
            text=globals.CHOOSE_LANG,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=buttons,
                resize_keyboard=True
            )
        )
        context.user_data["state"] = globals.STATES["reg"]

    elif not db_user["lang_id"]:
        buttons = [
            [KeyboardButton(text=globals.BTN_LANG_UZ), KeyboardButton(text=globals.BTN_LANG_RU)],
            [KeyboardButton(text=globals.BTN_LANG_EN)]
        ]
        update.message.reply_text(
            text=globals.CHOOSE_LANG,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=buttons,
                resize_keyboard=True
            )
        )
        context.user_data["state"] = globals.STATES["reg"]

    elif not db_user["first_name"]:
        update.message.reply_text(
            text=globals.TEXT_ENTER_FIRST_NAME[db_user['lang_id']],
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["state"] = globals.STATES["reg"]

    elif not db_user["last_name"]:
        update.message.reply_text(
            text=globals.TEXT_ENTER_LAST_NAME[db_user['lang_id']],
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["state"] = globals.STATES["reg"]

    elif not db_user["phone_number"]:
        buttons = [
            [KeyboardButton(text=globals.BTN_SEND_CONTACT[db_user['lang_id']], request_contact=True)]
        ]
        update.message.reply_text(
            text=globals.TEXT_ENTER_CONTACT[db_user['lang_id']],
            reply_markup=ReplyKeyboardMarkup(
                keyboard=buttons,
                resize_keyboard=True
            )
        )
        context.user_data["state"] = globals.STATES["reg"]

    else:
        from config import ADMIN_ID
        if str(user.id) == str(ADMIN_ID):
            from admin import admin_command
            return admin_command(update, context)

        pending = context.user_data.get("pending_deeplink")
        if pending:
            del context.user_data["pending_deeplink"]
            if pending.startswith("duel_"):
                from duel import handle_duel_deeplink
                duel_id_str = pending.replace("duel_", "")
                handle_duel_deeplink(update, context, duel_id_str)
                return
            elif pending.startswith("ref_"):
                from friends import process_referral
                process_referral(update, context, pending)
                return

        methods.send_main_menu(context, user.id, db_user['lang_id'])
        context.user_data["state"] = globals.STATES["menu"]


def check_data_decorator(func):
    def inner(update, context):
        user = update.message.from_user
        db_user = db.get_user_by_chat_id(user.id)
        state = context.user_data.get("state", 0)

        if state != globals.STATES['reg']:

            if not db_user:
                db.create_user(user.id)
                buttons = [
                    [KeyboardButton(text=globals.BTN_LANG_UZ), KeyboardButton(text=globals.BTN_LANG_RU)],
                    [KeyboardButton(text=globals.BTN_LANG_EN)]
                ]
                update.message.reply_text(text=globals.WELCOME_TEXT)
                update.message.reply_text(
                    text=globals.CHOOSE_LANG,
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=buttons,
                        resize_keyboard=True
                    )
                )
                context.user_data["state"] = globals.STATES["reg"]

            elif not db_user["lang_id"]:
                buttons = [
                    [KeyboardButton(text=globals.BTN_LANG_UZ), KeyboardButton(text=globals.BTN_LANG_RU)],
                    [KeyboardButton(text=globals.BTN_LANG_EN)]
                ]
                update.message.reply_text(
                    text=globals.CHOOSE_LANG,
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=buttons,
                        resize_keyboard=True
                    )
                )
                context.user_data["state"] = globals.STATES["reg"]

            elif not db_user["first_name"]:
                update.message.reply_text(
                    text=globals.TEXT_ENTER_FIRST_NAME[db_user['lang_id']],
                    reply_markup=ReplyKeyboardRemove()
                )
                context.user_data["state"] = globals.STATES["reg"]

            elif not db_user["last_name"]:
                update.message.reply_text(
                    text=globals.TEXT_ENTER_LAST_NAME[db_user['lang_id']],
                    reply_markup=ReplyKeyboardRemove()
                )
                context.user_data["state"] = globals.STATES["reg"]

            elif not db_user["phone_number"]:
                buttons = [
                    [KeyboardButton(text=globals.BTN_SEND_CONTACT[db_user['lang_id']], request_contact=True)]
                ]
                update.message.reply_text(
                    text=globals.TEXT_ENTER_CONTACT[db_user['lang_id']],
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=buttons,
                        resize_keyboard=True
                    )
                )
                context.user_data["state"] = globals.STATES["reg"]

            else:
                return func(update, context)

            return False

        else:
            return func(update, context)
    return inner

def check_json():
    papka_nomi = 'json_files' 

    for fayl_nomi in os.listdir(papka_nomi):
        if fayl_nomi.endswith('.json'):
            fayl_manzili = os.path.join(papka_nomi, fayl_nomi)
            
            with open(fayl_manzili, 'r', encoding='utf-8') as f:
                malumot = json.load(f)
                
            if 'test_id' not in malumot:
                yangi_id = f"test_{uuid.uuid4().hex[:8]}"
                
                yangi_malumot = {"test_id": yangi_id}
                yangi_malumot.update(malumot)
                
                with open(fayl_manzili, 'w', encoding='utf-8') as f:
                    json.dump(yangi_malumot, f, indent=4, ensure_ascii=False)
                    
                print(f"✅ {fayl_nomi} fayliga ID qo'shildi: {yangi_id}")
            else:
                print(f"⚠️ {fayl_nomi} faylida allaqachon ID bor.")