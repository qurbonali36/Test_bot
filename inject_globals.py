with open('globals.py', 'a', encoding='utf-8') as f:
    f.write("""

# ══════════════════════════════════════
#  FEATURES LOCALIZATION
# ══════════════════════════════════════

# Feature 1: Daily Reward
DAILY_REWARD_TITLE = {1: "🎁 KUNLIK MUKOFOT!", 2: "🎁 ЕЖЕДНЕВНАЯ НАГРАДА!", 3: "🎁 DAILY REWARD!"}
DAILY_REWARD_STREAK = {1: "🔥 Streak: {streak} kun", 2: "🔥 Серия: {streak} дней", 3: "🔥 Streak: {streak} days"}
DAILY_REWARD_TODAY = {1: "✨ Bugungi mukofot: +{xp} XP", 2: "✨ Награда сегодня: +{xp} XP", 3: "✨ Today's reward: +{xp} XP"}
DAILY_REWARD_TOMORROW = {1: "➡️ Ertaga: +{xp} XP", 2: "➡️ Завтра: +{xp} XP", 3: "➡️ Tomorrow: +{xp} XP"}
DAILY_REWARD_BONUS = {1: "🏆 7 KUNLIK STREAK!\\n🎉 BONUS: +{xp} XP", 2: "🏆 7 ДНЕЙ ПОДРЯД!\\n🎉 БОНУС: +{xp} XP", 3: "🏆 7 DAY STREAK!\\n🎉 BONUS: +{xp} XP"}

# Feature 2: Missions
MENU_MISSIONS = {1: "🎯 Maqsadlar", 2: "🎯 Цели", 3: "🎯 Missions"}
MISSIONS_DAILY = {1: "📅 Bugungi vazifalar", 2: "📅 Задачи на сегодня", 3: "📅 Today's missions"}
MISSIONS_WEEKLY = {1: "📆 Haftalik vazifalar", 2: "📆 Задачи на неделю", 3: "📆 Weekly missions"}
MISSION_PROGRESS = {1: "🎁 +{xp} XP", 2: "🎁 +{xp} XP", 3: "🎁 +{xp} XP"}
MISSION_COMPLETED = {1: "✅ Bajarildi!", 2: "✅ Выполнено!", 3: "✅ Completed!"}

# Feature 3: Spaced Repetition
SPACED_REP_TITLE = {1: "🧠 Takrorlash", 2: "🧠 Повторение", 3: "🧠 Review"}
SPACED_REP_REMINDER = {1: "🧠 Takrorlash vaqti keldi!\\n📚 Sizda takrorlash uchun {count} ta savol tayyor!", 2: "🧠 Время повторения!\\n📚 У вас {count} вопросов для повторения!", 3: "🧠 Review time!\\n📚 You have {count} questions ready for review!"}
BTN_START_REVIEW = {1: "🔄 Takrorlashni boshlash", 2: "🔄 Начать повторение", 3: "🔄 Start review"}

# Feature 4: Test Creator Wizard
WIZARD_ENTER_NAME = {1: "📝 Test nomini kiriting:", 2: "📝 Введите название теста:", 3: "📝 Enter test name:"}
WIZARD_ENTER_Q = {1: "❓ {num}-savolni kiriting:", 2: "❓ Введите {num}-й вопрос:", 3: "❓ Enter question {num}:"}
WIZARD_ENTER_OPTIONS = {1: "A, B, C, D variantlarni vergul bilan ajratib yozing:", 2: "Введите варианты A, B, C, D через запятую:", 3: "Enter options A, B, C, D separated by commas:"}
WIZARD_CHOOSE_CORRECT = {1: "✅ To‘g‘ri javobni belgilang:", 2: "✅ Выберите правильный ответ:", 3: "✅ Select the correct answer:"}
BTN_NEXT_QUESTION = {1: "➕ Keyingi savol", 2: "➕ Следующий вопрос", 3: "➕ Next question"}

# Feature 5: Friends & Referral
MENU_FRIENDS = {1: "👥 Do‘stlar", 2: "👥 Друзья", 3: "👥 Friends"}
FRIENDS_LIST = {1: "👤 Do‘stlarim", 2: "👤 Мои друзья", 3: "👤 My friends"}
FRIENDS_LEADERBOARD = {1: "🏆 Do‘stlar reytingi", 2: "🏆 Рейтинг друзей", 3: "🏆 Friends leaderboard"}
ADD_FRIEND = {1: "➕ Do‘st qo‘shish", 2: "➕ Добавить друга", 3: "➕ Add friend"}
SEND_DUEL = {1: "⚔️ Duel yuborish", 2: "⚔️ Отправить дуэль", 3: "⚔️ Send duel"}
MY_REFERRAL = {1: "🔗 Taklif havolam", 2: "🔗 Моя ссылка", 3: "🔗 Referral link"}

# Feature 6: Matchmaking
BTN_RANDOM_MATCH = {1: "🎲 Tasodifiy raqib", 2: "🎲 Случайный соперник", 3: "🎲 Random opponent"}
MATCH_SEARCHING = {1: "🎲 Raqib qidirilmoqda...\\n🔎 Sizga mos raqib topilmoqda...", 2: "🎲 Поиск соперника...\\n🔎 Подбираем подходящего соперника...", 3: "🎲 Searching for opponent...\\n🔎 Finding a suitable opponent..."}
MATCH_FOUND = {1: "⚔️ RAQIB TOPILDI!\\n👤 Raqib: {name}\\n🚀 Duel boshlandi!", 2: "⚔️ СОПЕРНИК НАЙДЕН!\\n👤 Соперник: {name}\\n🚀 Дуэль началась!", 3: "⚔️ OPPONENT FOUND!\\n👤 Opponent: {name}\\n🚀 Duel started!"}

# Feature 7: Tournaments
MENU_TOURNAMENT = {1: "🏟️ TURNIR", 2: "🏟️ ТУРНИР", 3: "🏟️ TOURNAMENT"}
BTN_REGISTER_TOURNAMENT = {1: "✅ Ishtirok etaman", 2: "✅ Буду участвовать", 3: "✅ I will participate"}
TOURNAMENT_START = {1: "🚀 TURNIR BOSHLANDI!", 2: "🚀 ТУРНИР НАЧАЛСЯ!", 3: "🚀 TOURNAMENT STARTED!"}
LIVE_LEADERBOARD_TXT = {1: "🏆 LIVE LEADERBOARD", 2: "🏆 LIVE LEADERBOARD", 3: "🏆 LIVE LEADERBOARD"}

# Feature 8: Subject Mastery
SUBJECT_MASTERY_TITLE = {1: "📚 Fanlar bo‘yicha bilim darajasi", 2: "📚 Уровень знаний по предметам", 3: "📚 Subject Mastery"}

# Feature 9: Weekly Digest
WEEKLY_DIGEST_TITLE = {1: "📈 HAFTALIK HISOBOT", 2: "📈 ЕЖЕНЕДЕЛЬНЫЙ ОТЧЕТ", 3: "📈 WEEKLY DIGEST"}
WEEKLY_DIGEST_NO_DATA = {1: "0 ta test", 2: "0 тестов", 3: "0 tests"}

# Feature 10: Seasonal Leaderboards
SEASONAL_CURRENT = {1: "🏆 Joriy mavsum", 2: "🏆 Текущий сезон", 3: "🏆 Current season"}
SEASONAL_OLD = {1: "📜 Eski mavsumlar", 2: "📜 Прошлые сезоны", 3: "📜 Past seasons"}
SEASONAL_MY_SCORE = {1: "👤 Mening natijam", 2: "👤 Мой результат", 3: "👤 My score"}
""")
print("Globals updated!")
