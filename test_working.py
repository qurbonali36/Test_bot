from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
import globals

db = Database("tg_bot.db")

# Fan nomlari → JSON fayl manzillari
FAYLLAR_XARITASI = {
    "📐 Matematika": "json_files/matematika.json", "📐 Математика": "json_files/matematika.json", "📐 Mathematics": "json_files/matematika.json",
    "📖 Adabiyot": "json_files/adabiyot.json", "📖 Литература": "json_files/adabiyot.json", "📖 Literature": "json_files/adabiyot.json",
    "⚛️ Fizika": "json_files/fizika.json", "⚛️ Физика": "json_files/fizika.json", "⚛️ Physics": "json_files/fizika.json",
    "🇬🇧 Ingliz tili": "json_files/ingiliz_tili.json", "🇬🇧 Английский язык": "json_files/ingiliz_tili.json", "🇬🇧 English language": "json_files/ingiliz_tili.json",
    "🏛 Tarix": "json_files/tarix.json", "🏛 История": "json_files/tarix.json", "🏛 History": "json_files/tarix.json",
    "🧬 Biologiya": "json_files/biologiya.json", "🧬 Биология": "json_files/biologiya.json", "🧬 Biology": "json_files/biologiya.json",
    "🧪 Kimyo": "json_files/kimyo.json", "🧪 Химия": "json_files/kimyo.json", "🧪 Chemistry": "json_files/kimyo.json",
}

INLINE_BUTTONS = [
    [InlineKeyboardButton(text="5️⃣", callback_data="class_5"), InlineKeyboardButton(text="6️⃣", callback_data="class_6"), InlineKeyboardButton(text="7️⃣", callback_data="class_7")],
    [InlineKeyboardButton(text="8️⃣", callback_data="class_8"), InlineKeyboardButton(text="9️⃣", callback_data="class_9"), InlineKeyboardButton(text="🔟", callback_data="class_10")],
    [InlineKeyboardButton(text="1️⃣1️⃣", callback_data="class_11")]
]


def check_pressed(update, context):
    """📝 Test ishlash tugmasi bosilganda — fanlar ro'yxatini chiqaradi."""
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    if not db_user:
        return False
    lang_id = db_user["lang_id"] or 1
    buttons = ReplyKeyboardMarkup([
        [KeyboardButton(text=globals.INGLIZ_TILI[lang_id])],
        [KeyboardButton(text=globals.MATEMATIKA[lang_id]), KeyboardButton(text=globals.FIZIKA[lang_id])],
        [KeyboardButton(text=globals.BIOLOGIYA[lang_id]), KeyboardButton(text=globals.KIMYO[lang_id])],
        [KeyboardButton(text=globals.TARIX[lang_id]), KeyboardButton(text=globals.ADABIYOT[lang_id])],
        [KeyboardButton(text=globals.BTN_BACK[lang_id])]
    ], resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(globals.TEXT_OBJECTS[lang_id], parse_mode="HTML", reply_markup=buttons)
    return True


def check_object(update, context):
    """Fan tanlanganda — sinf tanlash inline tugmalarini chiqaradi. True/False qaytaradi."""
    text = update.message.text
    db_user = db.get_user_by_chat_id(update.effective_user.id)
    if not db_user:
        return False
    lang_id = db_user["lang_id"] or 1

    fan_nomlari = [
        globals.INGLIZ_TILI, globals.MATEMATIKA, globals.FIZIKA,
        globals.BIOLOGIYA, globals.KIMYO, globals.TARIX, globals.ADABIYOT
    ]
    matched = False
    for fan in fan_nomlari:
        if text == fan[lang_id]:
            keyboard = INLINE_BUTTONS + [[InlineKeyboardButton(text=globals.BTN_HOME[lang_id], callback_data="home")]]
            update.message.reply_text(globals.TEXT_TEST_WORKING[lang_id], parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            matched = True
            break

    if not matched:
        return False

    # Fan nomi → fayl manzili
    fayl_manzili = FAYLLAR_XARITASI.get(text)
    if fayl_manzili:
        context.user_data["object"] = fayl_manzili

    return True
