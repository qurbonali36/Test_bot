with open('C:/Users/Xotin-qizlar faoli/Desktop/Dasturlash_Darslari/Python_TelegramBot_Lessons/Test_bot/globals.py', 'a', encoding='utf-8') as f:
    f.write('''\n
# ═══════════════════════════════════════
#  SHARE RESULT (Natijani ulashish)
# ═══════════════════════════════════════
BTN_SHARE_RESULT = {1: "📤 Natijani ulashish", 2: "📤 Поделиться результатом", 3: "📤 Share result"}

def get_share_result_text(lang_id):
    texts = {
        1: "🎯 Men test ishladim! Sen ham sinab ko'r!",
        2: "🎯 Я прошел тест! Попробуй и ты!",
        3: "🎯 I took a test! Try it too!"
    }
    return texts.get(lang_id, texts[1])

# ═══════════════════════════════════════
#  PRACTICE MISTAKES (Xatolardan mashq)
# ═══════════════════════════════════════
BTN_PRACTICE_MISTAKES = {1: "🎯 Xatolardan mashq", 2: "🎯 Практика по ошибкам", 3: "🎯 Practice from mistakes"}
TEXT_PRACTICE_NO_DATA = {
    1: "📭 <b>Xato javoblar topilmadi!</b>\\n\\n<i>Avval biror test ishlang, shunda xato javoblaringizdan mashq qilishingiz mumkin bo'ladi.</i>",
    2: "📭 <b>Ошибок не найдено!</b>\\n\\n<i>Сначала пройдите тест, тогда вы сможете практиковаться на своих ошибках.</i>",
    3: "📭 <b>No wrong answers found!</b>\\n\\n<i>Take a test first, then you can practice from your mistakes.</i>"
}
TEXT_PRACTICE_START = {
    1: "🎯 <b>Xatolardan mashq boshlanmoqda!</b>\\n\\n<i>Sizning xato javoblaringizdan {count} ta savol tanlandi.\\nTayyorlaning...</i>",
    2: "🎯 <b>Практика по ошибкам начинается!</b>\\n\\n<i>Из ваших ошибок выбрано {count} вопросов.\\nПриготовьтесь...</i>",
    3: "🎯 <b>Practice from mistakes starting!</b>\\n\\n<i>{count} questions selected from your mistakes.\\nGet ready...</i>"
}

# ═══════════════════════════════════════
#  CATEGORIES (Kategoriyalar)
# ═══════════════════════════════════════
BTN_CATEGORIES = {1: "📂 Kategoriyalar", 2: "📂 Категории", 3: "📂 Categories"}
TEXT_CATEGORIES = {
    1: "📂 <b>Test kategoriyalarini tanlang:</b>\\n\\n<i>Qiziqtirgan fan yoki yo'nalishni tanlang:</i>",
    2: "📂 <b>Выберите категорию тестов:</b>\\n\\n<i>Выберите интересующий предмет:</i>",
    3: "📂 <b>Select test category:</b>\\n\\n<i>Choose a subject or topic:</i>"
}
TEXT_CAT_EMPTY = {
    1: "📭 <b>{cat}</b> kategoriyasida hali testlar mavjud emas.\\n\\n<i>Birinchi bo'lib test yarating!</i>",
    2: "📭 В категории <b>{cat}</b> пока нет тестов.\\n\\n<i>Будьте первым — создайте тест!</i>",
    3: "📭 No tests in <b>{cat}</b> category yet.\\n\\n<i>Be the first to create one!</i>"
}
TEXT_CAT_TESTS = {
    1: "📂 <b>{cat}</b>\\n\\n📊 <i>Jami {count} ta test topildi:</i>\\n━━━━━━━━━━━━━━━━━━━━━━━━━",
    2: "📂 <b>{cat}</b>\\n\\n📊 <i>Найдено {count} тестов:</i>\\n━━━━━━━━━━━━━━━━━━━━━━━━━",
    3: "📂 <b>{cat}</b>\\n\\n📊 <i>{count} tests found:</i>\\n━━━━━━━━━━━━━━━━━━━━━━━━━"
}
''')
