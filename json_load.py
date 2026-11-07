import json
from database import Database
import globals
import random

db = Database("tg_bot.db")


def json_load(update, context, file_path, clas, time_per_q=10, name="", description="", creator=""):
    with open(f"{file_path}", "r", encoding="utf-8") as file:
        list_json = json.load(file)

    db_user = db.get_user_by_chat_id(update.effective_user.id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    amount_quest = 0
    questions_answers = []

    for obyekt in list_json:
        if obyekt.get("sinf") == clas:
            questions_answers.append(obyekt)
            amount_quest += 1

    random.shuffle(questions_answers)
    context.user_data["savollar_bazasi"] = questions_answers
    context.user_data["savollar_soni"] = amount_quest
    main_time = amount_quest * time_per_q
    minut, seconds = divmod(main_time, 60)
    hour, minut = divmod(minut, 60)
    vaqt_matni = ""
    if hour > 0:
        vaqt_matni += f"{hour} {globals.HOUR[lang_id]} "
    if minut > 0:
        vaqt_matni += f"{minut} {globals.MINUTE[lang_id]} "
    if seconds > 0:
        vaqt_matni += f"{seconds} {globals.SECOND[lang_id]}"

    INSTRUCTION = {
        1: "\n👇 <i>Pastdagi tugmalar orqali har bir savol uchun vaqtni o'zingizga moslab belgilang va testni boshlang!</i>",
        2: "\n👇 <i>Настройте время на каждый вопрос с помощью кнопок ниже и начните тест!</i>",
        3: "\n👇 <i>Set the time per question using the buttons below and start the test!</i>"
    }

    send_message = (
        f"{globals.ABOUT_TEST[lang_id]}\n\n"
        f"{globals.NAME_TEST[lang_id]} <i>{name}</i>\n\n"
        f"{globals.DESCRIPTION_TEST[lang_id]} <i>{description}</i>\n\n"
        f"{globals.AMOUNT_TEST[lang_id]} <i>{amount_quest}</i>\n\n"
        f"<blockquote>{globals.CREATOR_TEST[lang_id]} <i>{creator}</i></blockquote>"
        f"{INSTRUCTION.get(lang_id, INSTRUCTION[1])}"
    )
    context.user_data["amount_quest"] = amount_quest
    return send_message
