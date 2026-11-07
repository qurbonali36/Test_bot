from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import Database
from globals import BTN_HOME, BTN_BACK
from config import ADMIN_ID

db = Database('tg_bot.db')

BTN_HELP = {1: '❓ Yordam', 2: '❓ Помощь', 3: '❓ Help'}

# ═══════════════════════════════════════
#  YORDAM MATNLARI
# ═══════════════════════════════════════
HELP_TEXTS = {
    'main': {
        1: ("🌟 <b>YORDAM MARKAZI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi bo'limlardan birini tanlang:\n\n"
            "<blockquote>💡 Agar muammo yuzaga kelsa, pastdagi\n"
            "\"🆘 Muammo xabar qilish\" tugmasidan foydalaning.</blockquote>"),
        2: ("🌟 <b>ЦЕНТР ПОМОЩИ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Выберите один из разделов:\n\n"
            "<blockquote>💡 Если возникла проблема, используйте кнопку\n"
            "\"🆘 Сообщить о проблеме\" ниже.</blockquote>"),
        3: ("🌟 <b>HELP CENTER</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Choose a section below:\n\n"
            "<blockquote>💡 If you encounter an issue, use the\n"
            "\"🆘 Report a problem\" button below.</blockquote>")
    },
    'categories': {
        'help_tests': {
            'btn': {1: '📝 Testlar', 2: '📝 Тесты', 3: '📝 Tests'},
            'text': {
                1: ("📝 <b>TEST ISHLASH BO'YICHA YORDAM</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Siz botda turli xil fanlardan test ishlashingiz mumkin.\n\n"
                    "📌 <b>Qadamlar:</b>\n"
                    "├ 1️⃣ Asosiy menyudan \"Test ishlash\" ni bosing\n"
                    "├ 2️⃣ Fan va qiyinchilik darajasini tanlang\n"
                    "├ 3️⃣ Savollarga javob bering\n"
                    "└ 4️⃣ Natijangizni ko'ring va tahlil qiling\n\n"
                    "<blockquote>⏱ Har bir savolga belgilangan vaqt ichida javob berish kerak!</blockquote>"),
                2: ("📝 <b>ПОМОЩЬ ПО ТЕСТАМ</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Вы можете решать тесты по различным предметам.\n\n"
                    "📌 <b>Шаги:</b>\n"
                    "├ 1️⃣ Нажмите «Решать тесты» в главном меню\n"
                    "├ 2️⃣ Выберите предмет и уровень сложности\n"
                    "├ 3️⃣ Ответьте на вопросы\n"
                    "└ 4️⃣ Узнайте свой результат\n\n"
                    "<blockquote>⏱ На каждый вопрос отведено определённое время!</blockquote>"),
                3: ("📝 <b>TESTS HELP</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "You can take tests on various subjects.\n\n"
                    "📌 <b>Steps:</b>\n"
                    "├ 1️⃣ Press \"Take a test\" from the main menu\n"
                    "├ 2️⃣ Choose a subject and difficulty level\n"
                    "├ 3️⃣ Answer the questions\n"
                    "└ 4️⃣ See your result and analysis\n\n"
                    "<blockquote>⏱ Each question has a time limit!</blockquote>")
            }
        },
        'help_create': {
            'btn': {1: '➕ Test yaratish', 2: '➕ Создать тест', 3: '➕ Create test'},
            'text': {
                1: ("➕ <b>TEST YARATISH BO'YICHA YORDAM</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "O'z testlaringizni yarating va do'stlar bilan ulashing!\n\n"
                    "📌 <b>Qadamlar:</b>\n"
                    "├ 1️⃣ \"Test yaratish\" bo'limiga kiring\n"
                    "├ 2️⃣ Test nomini va tavsifini kiriting\n"
                    "├ 3️⃣ Har bir savol uchun vaqtni belgilang\n"
                    "├ 4️⃣ Quiz formatida savollar yuboring\n"
                    "└ 5️⃣ Tayyor testni do'stlarga ulashing\n\n"
                    "<blockquote>📤 Testni guruhga ham yuborishingiz mumkin!</blockquote>"),
                2: ("➕ <b>ПОМОЩЬ ПО СОЗДАНИЮ ТЕСТОВ</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Создавайте свои тесты и делитесь с друзьями!\n\n"
                    "📌 <b>Шаги:</b>\n"
                    "├ 1️⃣ Зайдите в раздел «Создать тест»\n"
                    "├ 2️⃣ Введите название и описание теста\n"
                    "├ 3️⃣ Установите время на каждый вопрос\n"
                    "├ 4️⃣ Отправьте вопросы в формате Quiz\n"
                    "└ 5️⃣ Поделитесь тестом с друзьями\n\n"
                    "<blockquote>📤 Тест можно отправить в группу!</blockquote>"),
                3: ("➕ <b>CREATE TEST HELP</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Create your own tests and share with friends!\n\n"
                    "📌 <b>Steps:</b>\n"
                    "├ 1️⃣ Enter the \"Create Test\" section\n"
                    "├ 2️⃣ Enter test title and description\n"
                    "├ 3️⃣ Set time limit per question\n"
                    "├ 4️⃣ Send questions in Quiz format\n"
                    "└ 5️⃣ Share the test with friends\n\n"
                    "<blockquote>📤 You can also send the test to groups!</blockquote>")
            }
        },
        'help_profile': {
            'btn': {1: '👤 Profil va Reyting', 2: '👤 Профиль и Рейтинг', 3: '👤 Profile & Rank'},
            'text': {
                1: ("👤 <b>PROFIL VA REYTING</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Test ishlash orqali tajriba (XP) to'plang!\n\n"
                    "📌 <b>Tizim:</b>\n"
                    "├ 🎯 Har bir to'g'ri javob uchun XP beriladi\n"
                    "├ 📈 XP yig'ilsa darajangiz ko'tariladi\n"
                    "├ 🏅 Maxsus yutuqlar va nishonlar\n"
                    "└ 🏆 Reytingda peshqadamlar qatoriga kiring\n\n"
                    "<blockquote>🔥 Streak (ketma-ket kunlar) bonus XP beradi!</blockquote>"),
                2: ("👤 <b>ПРОФИЛЬ И РЕЙТИНГ</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Набирайте опыт (XP) за решение тестов!\n\n"
                    "📌 <b>Система:</b>\n"
                    "├ 🎯 XP за каждый правильный ответ\n"
                    "├ 📈 При накоплении XP уровень повышается\n"
                    "├ 🏅 Особые достижения и значки\n"
                    "└ 🏆 Войдите в число лидеров рейтинга\n\n"
                    "<blockquote>🔥 Серия (дни подряд) даёт бонусный XP!</blockquote>"),
                3: ("👤 <b>PROFILE & RANK</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Gain experience (XP) by taking tests!\n\n"
                    "📌 <b>System:</b>\n"
                    "├ 🎯 XP for each correct answer\n"
                    "├ 📈 Level up when enough XP is accumulated\n"
                    "├ 🏅 Special badges and achievements\n"
                    "└ 🏆 Join the leaderboard\n\n"
                    "<blockquote>🔥 Streaks (consecutive days) give bonus XP!</blockquote>")
            }
        },
        'help_duel': {
            'btn': {1: '⚔️ Duel', 2: '⚔️ Дуэль', 3: '⚔️ Duel'},
            'text': {
                1: ("⚔️ <b>DUEL BO'YICHA YORDAM</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Do'stlaringiz bilan bilimda bellashing!\n\n"
                    "📌 <b>Qadamlar:</b>\n"
                    "├ 1️⃣ Duel menyusidan \"Yangi duel\" ni bosing\n"
                    "├ 2️⃣ O'z testlaringizdan birini tanlang\n"
                    "├ 3️⃣ Havolani do'stingizga yuboring\n"
                    "└ 4️⃣ Kim ko'p to'g'ri javob bersa — g'olib!\n\n"
                    "<blockquote>🏆 G'olib qo'shimcha reyting ballariga ega bo'ladi!</blockquote>"),
                2: ("⚔️ <b>ПОМОЩЬ ПО ДУЭЛЯМ</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Соревнуйтесь с друзьями в знаниях!\n\n"
                    "📌 <b>Шаги:</b>\n"
                    "├ 1️⃣ В меню дуэлей нажмите «Новая дуэль»\n"
                    "├ 2️⃣ Выберите один из ваших тестов\n"
                    "├ 3️⃣ Отправьте ссылку другу\n"
                    "└ 4️⃣ Кто больше правильных ответов — победитель!\n\n"
                    "<blockquote>🏆 Победитель получает дополнительные рейтинговые баллы!</blockquote>"),
                3: ("⚔️ <b>DUEL HELP</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Compete with friends in knowledge!\n\n"
                    "📌 <b>Steps:</b>\n"
                    "├ 1️⃣ Press \"New duel\" in the duel menu\n"
                    "├ 2️⃣ Choose one of your tests\n"
                    "├ 3️⃣ Send the link to a friend\n"
                    "└ 4️⃣ Whoever gets more correct answers wins!\n\n"
                    "<blockquote>🏆 The winner gets extra ranking points!</blockquote>")
            }
        },
        'help_daily': {
            'btn': {1: '🎯 Kunlik vazifa', 2: '🎯 Ежедневное задание', 3: '🎯 Daily challenge'},
            'text': {
                1: ("🎯 <b>KUNLIK VAZIFALAR</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Har kuni maxsus test ishlang va bonus oling!\n\n"
                    "📌 <b>Tizim:</b>\n"
                    "├ 📅 Har kuni yangi test beriladi\n"
                    "├ 🔥 Ketma-ket ishlasangiz streak ortadi\n"
                    "├ 🎁 3+ kun streak = +10 XP bonus\n"
                    "├ 🎁 7+ kun streak = +25 XP bonus\n"
                    "└ 🎁 30+ kun streak = +100 XP bonus\n\n"
                    "<blockquote>🔥 Har kuni kirib streak'ni uzilmasin!</blockquote>"),
                2: ("🎯 <b>ЕЖЕДНЕВНЫЕ ЗАДАНИЯ</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Проходите ежедневный тест и получайте бонусы!\n\n"
                    "📌 <b>Система:</b>\n"
                    "├ 📅 Каждый день новый тест\n"
                    "├ 🔥 Серия растёт при ежедневном прохождении\n"
                    "├ 🎁 3+ дней серия = +10 XP бонус\n"
                    "├ 🎁 7+ дней серия = +25 XP бонус\n"
                    "└ 🎁 30+ дней серия = +100 XP бонус\n\n"
                    "<blockquote>🔥 Заходите каждый день, чтобы не прервать серию!</blockquote>"),
                3: ("🎯 <b>DAILY CHALLENGES</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Take the daily test and earn bonuses!\n\n"
                    "📌 <b>System:</b>\n"
                    "├ 📅 A new test is available every day\n"
                    "├ 🔥 Your streak grows with consecutive days\n"
                    "├ 🎁 3+ days streak = +10 XP bonus\n"
                    "├ 🎁 7+ days streak = +25 XP bonus\n"
                    "└ 🎁 30+ days streak = +100 XP bonus\n\n"
                    "<blockquote>🔥 Come back daily to keep your streak!</blockquote>")
            }
        },
        'help_settings': {
            'btn': {1: '⚙️ Sozlamalar', 2: '⚙️ Настройки', 3: '⚙️ Settings'},
            'text': {
                1: ("⚙️ <b>SOZLAMALAR BO'YICHA YORDAM</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "📌 <b>Sozlamalarda siz:</b>\n"
                    "├ 🌐 Bot tilini o'zgartirishingiz mumkin\n"
                    "│    (O'zbek, Rus, Ingliz)\n"
                    "├ 👤 Ism va familiyangizni tahrirlashingiz\n"
                    "├ 📱 Telefon raqamni yangilashingiz\n"
                    "├ 🔔 Bildirishnomalarni sozlashingiz\n"
                    "└ 📝 Testlaringizni boshqarishingiz mumkin"),
                2: ("⚙️ <b>ПОМОЩЬ ПО НАСТРОЙКАМ</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "📌 <b>В настройках вы можете:</b>\n"
                    "├ 🌐 Изменить язык бота\n"
                    "│    (Узбекский, Русский, Английский)\n"
                    "├ 👤 Редактировать имя и фамилию\n"
                    "├ 📱 Обновить номер телефона\n"
                    "├ 🔔 Настроить уведомления\n"
                    "└ 📝 Управлять вашими тестами"),
                3: ("⚙️ <b>SETTINGS HELP</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "📌 <b>In settings you can:</b>\n"
                    "├ 🌐 Change bot language\n"
                    "│    (Uzbek, Russian, English)\n"
                    "├ 👤 Edit your name and surname\n"
                    "├ 📱 Update your phone number\n"
                    "├ 🔔 Configure notifications\n"
                    "└ 📝 Manage your tests")
            }
        }
    },
    'back': {1: '⬅️ Orqaga', 2: '⬅️ Назад', 3: '⬅️ Back'}
}

# ═══════════════════════════════════════
#  MUAMMO XABARLASH TIZIMI
# ═══════════════════════════════════════
BTN_REPORT_PROBLEM = {1: '🆘 Muammo xabar qilish', 2: '🆘 Сообщить о проблеме', 3: '🆘 Report a problem'}
BTN_CONTACT_ADMIN_HELP = {1: '👨‍💻 Adminga murojaat', 2: '👨‍💻 Связаться с админом', 3: '👨‍💻 Contact admin'}

PROBLEM_CATEGORIES = {
    'prob_tests': {1: '📝 Test ishlash muammosi', 2: '📝 Проблема с тестами', 3: '📝 Test issue'},
    'prob_create': {1: '➕ Test yaratish muammosi', 2: '➕ Проблема с созданием', 3: '➕ Create test issue'},
    'prob_profile': {1: '👤 Profil/Reyting muammosi', 2: '👤 Проблема с профилем', 3: '👤 Profile/Rank issue'},
    'prob_duel': {1: '⚔️ Duel muammosi', 2: '⚔️ Проблема с дуэлями', 3: '⚔️ Duel issue'},
    'prob_settings': {1: '⚙️ Sozlamalar muammosi', 2: '⚙️ Проблема с настройками', 3: '⚙️ Settings issue'},
    'prob_bookmarks': {1: '🔖 Saqlanganlar muammosi', 2: '🔖 Проблема с закладками', 3: '🔖 Bookmarks issue'},
    'prob_other': {1: '❓ Boshqa muammo', 2: '❓ Другая проблема', 3: '❓ Other issue'},
}

TEXT_CHOOSE_PROBLEM = {
    1: ("🆘 <b>MUAMMO XABAR QILISH</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Muammo qaysi bo'limga tegishli ekanligini tanlang:"),
    2: ("🆘 <b>СООБЩИТЬ О ПРОБЛЕМЕ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Выберите раздел, к которому относится проблема:"),
    3: ("🆘 <b>REPORT A PROBLEM</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select the section related to your problem:")
}

TEXT_DESCRIBE_PROBLEM = {
    1: ("✏️ <b>Muammoni tasvirlang</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📂 <b>Bo'lim:</b> {category}\n\n"
        "<i>Iltimos, muammoni batafsil yozing.\n"
        "Nima bo'lganini, qanday xato chiqayotganini aytib bering:</i>"),
    2: ("✏️ <b>Опишите проблему</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📂 <b>Раздел:</b> {category}\n\n"
        "<i>Пожалуйста, подробно опишите проблему.\n"
        "Что произошло, какая ошибка появилась:</i>"),
    3: ("✏️ <b>Describe the problem</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📂 <b>Section:</b> {category}\n\n"
        "<i>Please describe the problem in detail.\n"
        "What happened, what error appeared:</i>")
}

TEXT_PROBLEM_SENT = {
    1: ("✅ <b>Murojaatingiz muvaffaqiyatli yuborildi!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📂 <b>Bo'lim:</b> {category}\n"
        "📝 <b>Xabar:</b> <i>{message}</i>\n\n"
        "<blockquote>💬 Admin tez orada javob beradi. Sabringiz uchun rahmat!</blockquote>"),
    2: ("✅ <b>Ваше обращение успешно отправлено!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📂 <b>Раздел:</b> {category}\n"
        "📝 <b>Сообщение:</b> <i>{message}</i>\n\n"
        "<blockquote>💬 Админ ответит в ближайшее время. Спасибо за терпение!</blockquote>"),
    3: ("✅ <b>Your report has been sent successfully!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📂 <b>Section:</b> {category}\n"
        "📝 <b>Message:</b> <i>{message}</i>\n\n"
        "<blockquote>💬 Admin will respond soon. Thank you for your patience!</blockquote>")
}

TEXT_CONTACT_ADMIN = {
    1: ("👨‍💻 <b>ADMINGA MUROJAAT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<i>Istalgan savol, taklif yoki murojaatingizni yozing.\n"
        "Admin tez orada javob beradi.</i>"),
    2: ("👨‍💻 <b>СВЯЗЬ С АДМИНОМ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<i>Напишите любой вопрос, предложение или обращение.\n"
        "Админ ответит в ближайшее время.</i>"),
    3: ("👨‍💻 <b>CONTACT ADMIN</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<i>Write any question, suggestion or request.\n"
        "Admin will respond shortly.</i>")
}


# ═══════════════════════════════════════
#  FUNKSIYALAR
# ═══════════════════════════════════════

def show_help(update, context):
    """Asosiy yordam sahifasini ko'rsatish."""
    user = update.effective_user
    if not user:
        return

    chat_id = update.effective_chat.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1

    keyboard = []
    row = []
    for cb_data, info in HELP_TEXTS['categories'].items():
        row.append(InlineKeyboardButton(info['btn'][lang_id], callback_data=cb_data))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Muammo xabar qilish va adminga murojaat
    keyboard.append([InlineKeyboardButton(BTN_REPORT_PROBLEM.get(lang_id, BTN_REPORT_PROBLEM[1]), callback_data='help_report')])
    keyboard.append([InlineKeyboardButton(BTN_CONTACT_ADMIN_HELP.get(lang_id, BTN_CONTACT_ADMIN_HELP[1]), callback_data='help_contact_admin')])
    keyboard.append([InlineKeyboardButton(BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    text = HELP_TEXTS['main'][lang_id]

    if update.message:
        update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
    elif update.callback_query:
        try:
            update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
        except Exception:
            update.callback_query.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)


def handle_help_callback(update, context):
    """Yordam bo'limi callback handler."""
    query = update.callback_query
    if not query:
        return

    chat_id = query.message.chat_id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user['lang_id'] if db_user and db_user.get('lang_id') else 1
    data = query.data

    query.answer()

    # ── Yordam menyusiga qaytish ──
    if data == 'help_back':
        show_help(update, context)
        return

    # ── Muammo xabar qilish — bo'limni tanlash ──
    if data == 'help_report':
        keyboard = []
        for key, names in PROBLEM_CATEGORIES.items():
            keyboard.append([InlineKeyboardButton(names.get(lang_id, names[1]), callback_data=key)])
        keyboard.append([InlineKeyboardButton(HELP_TEXTS['back'][lang_id], callback_data='help_back')])
        keyboard.append([InlineKeyboardButton(BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')])

        query.edit_message_text(
            TEXT_CHOOSE_PROBLEM[lang_id],
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ── Muammo bo'limi tanlandi — foydalanuvchi yozishi kerak ──
    if data.startswith('prob_'):
        cat_name = PROBLEM_CATEGORIES.get(data, {}).get(lang_id, '❓')
        context.user_data['report_category'] = data
        context.user_data['report_category_name'] = cat_name
        context.user_data['state'] = 11  # report_problem state

        keyboard = [
            [InlineKeyboardButton(HELP_TEXTS['back'][lang_id], callback_data='help_report')],
            [InlineKeyboardButton(BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')]
        ]
        query.edit_message_text(
            TEXT_DESCRIBE_PROBLEM[lang_id].format(category=cat_name),
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ── Adminga murojaat (umumiy xabar) ──
    if data == 'help_contact_admin':
        context.user_data['report_category'] = 'general'
        context.user_data['report_category_name'] = {1: '💬 Umumiy murojaat', 2: '💬 Общее обращение', 3: '💬 General message'}.get(lang_id, '💬')
        context.user_data['state'] = 11  # report_problem state

        keyboard = [
            [InlineKeyboardButton(HELP_TEXTS['back'][lang_id], callback_data='help_back')],
            [InlineKeyboardButton(BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')]
        ]
        query.edit_message_text(
            TEXT_CONTACT_ADMIN[lang_id],
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ── Yordam kategoriyalari ──
    if data in HELP_TEXTS['categories']:
        text = HELP_TEXTS['categories'][data]['text'][lang_id]
        keyboard = [
            [InlineKeyboardButton(HELP_TEXTS['back'][lang_id], callback_data='help_back')],
            [InlineKeyboardButton(BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


def handle_report_input(update, context):
    """Foydalanuvchi muammo yozganda — adminga yuborish."""
    chat_id = update.effective_user.id
    text = update.message.text
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user.get("lang_id", 1) if db_user else 1

    cat_name = context.user_data.get('report_category_name', '❓')
    cat_key = context.user_data.get('report_category', 'unknown')

    # Foydalanuvchiga tasdiqlash
    first_name = db_user.get("first_name", "") if db_user else ""
    last_name = db_user.get("last_name", "") if db_user else ""
    phone = db_user.get("phone_number", "") if db_user else ""

    confirm_text = TEXT_PROBLEM_SENT[lang_id].format(category=cat_name, message=text[:200])
    keyboard = [[InlineKeyboardButton(BTN_HOME.get(lang_id, '🏠 Bosh sahifa'), callback_data='home')]]
    update.message.reply_text(confirm_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

    # Adminga to'liq ma'lumot yuborish
    admin_msg = (
        f"🆘 <b>YANGI MUAMMO XABARI!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Foydalanuvchi:</b> <a href='tg://user?id={chat_id}'>{first_name} {last_name}</a>\n"
        f"🆔 <b>ID:</b> <code>{chat_id}</code>\n"
        f"📱 <b>Tel:</b> <code>{phone}</code>\n\n"
        f"📂 <b>Bo'lim:</b> {cat_name}\n"
        f"🏷 <b>Kategoriya kodi:</b> <code>{cat_key}</code>\n\n"
        f"📝 <b>Muammo tavsifi:</b>\n"
        f"<blockquote>{text}</blockquote>"
    )

    reply_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Javob yozish", callback_data=f"admin_reply_{chat_id}")]
    ])

    try:
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_msg,
            parse_mode='HTML',
            reply_markup=reply_kb
        )
    except Exception:
        pass

    # Bazaga ham saqlash
    try:
        db.save_feedback(chat_id, f"[{cat_name}] {text}")
    except Exception:
        pass

    # State ni menyuga qaytarish
    import globals as g
    context.user_data['state'] = g.STATES['menu']
    context.user_data.pop('report_category', None)
    context.user_data.pop('report_category_name', None)
