import sqlite3
import threading
from functools import wraps

def db_lock(func):
    @wraps(func)
    @db_lock
    def wrapper(self, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)
    return wrapper


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.local = threading.local()
        self.lock = threading.RLock()

    @property
    def cur(self):
        if not hasattr(self.local, 'cursor'):
            self.local.cursor = self.conn.cursor()
        return self.local.cursor

    @db_lock
    def execute(self, sql, params=(), commit=True):
        self.cur.execute(sql, params)
        if commit:
            self.conn.commit()

    @db_lock
    def executescript(self, sql):
        self.cur.executescript(sql)
        self.conn.commit()
            
    @db_lock
    def execute_fetch(self, sql, params=(), fetchall=False, fetchone=False, raw_fetchone=False, raw_fetchall=False):
        self.cur.execute(sql, params)
        if raw_fetchone:
            return self.cur.fetchone()
        if raw_fetchall:
            return self.cur.fetchall()
        if fetchall:
            return dict_fetchall(self.cur)
        if fetchone:
            return dict_fetchone(self.cur)
        return self.cur.fetchall()

    @staticmethod
    def create_database():
        conn = sqlite3.connect("tg_bot.db")
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user(
                id INTEGER NOT NULL PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                phone_number TEXT,
                chat_id INTEGER UNIQUE,
                lang_id INTEGER
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users_results(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                point_test INTEGER,
                precent_corr_ans REAL,
                test_id TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tests_meta(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT UNIQUE,
                chat_id INTEGER,
                title TEXT DEFAULT '',
                description TEXT DEFAULT '',
                amount INTEGER DEFAULT 0,
                point_per_q INTEGER DEFAULT 1,
                time_per_q INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # ── Gamification: XP va daraja ──
        try:
            cur.execute("ALTER TABLE user ADD COLUMN xp INTEGER DEFAULT 0")
        except: pass
        try:
            cur.execute("ALTER TABLE user ADD COLUMN level INTEGER DEFAULT 1")
        except: pass
        try:
            cur.execute("ALTER TABLE user ADD COLUMN badges TEXT DEFAULT ''")
        except: pass
        try:
            cur.execute("ALTER TABLE user ADD COLUMN last_active TIMESTAMP")
        except: pass
        # ── users_results ga vaqt ustuni ──
        try:
            cur.execute("ALTER TABLE users_results ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except: pass
        try:
            cur.execute("ALTER TABLE users_results ADD COLUMN speed_bonus REAL DEFAULT 0")
        except: pass
        # ── Kundalik test ──
        cur.execute("""
            CREATE TABLE IF NOT EXISTS daily_challenges(
                date TEXT PRIMARY KEY,
                test_data TEXT,
                fan TEXT DEFAULT ''
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_streaks(
                chat_id INTEGER PRIMARY KEY,
                current_streak INTEGER DEFAULT 0,
                max_streak INTEGER DEFAULT 0,
                last_date TEXT
            )
        """)
        # ── Xato javoblar ──
        cur.execute("""
            CREATE TABLE IF NOT EXISTS wrong_answers(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                question TEXT,
                correct_answer TEXT,
                user_answer TEXT,
                test_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # ── Kategoriyalar ──
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_uz TEXT,
                name_ru TEXT,
                name_en TEXT,
                emoji TEXT DEFAULT '📚'
            )
        """)
        # Boshlang'ich kategoriyalar
        cur.execute("SELECT COUNT(*) FROM categories")
        if cur.fetchone()[0] == 0:
            categories = [
                ('Matematika', 'Математика', 'Mathematics', '📐'),
                ('Fizika', 'Физика', 'Physics', '⚛️'),
                ('Biologiya', 'Биология', 'Biology', '🧬'),
                ('Kimyo', 'Химия', 'Chemistry', '🧪'),
                ('Tarix', 'История', 'History', '🏛'),
                ('Ingliz tili', 'Английский', 'English', '🇬🇧'),
                ('Adabiyot', 'Литература', 'Literature', '📖'),
                ('Informatika', 'Информатика', 'Computer Science', '💻'),
                ('Geografiya', 'География', 'Geography', '🌍'),
                ('Boshqa', 'Другое', 'Other', '📁'),
            ]
            cur.executemany("INSERT INTO categories (name_uz, name_ru, name_en, emoji) VALUES (?,?,?,?)", categories)

        try:
            cur.execute("ALTER TABLE tests_meta ADD COLUMN category_id INTEGER DEFAULT 0")
        except: pass

        # ── Duellar ──
        cur.execute("""
            CREATE TABLE IF NOT EXISTS duels(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenger_id INTEGER,
                opponent_id INTEGER,
                test_id TEXT,
                challenger_score INTEGER DEFAULT 0,
                opponent_score INTEGER DEFAULT 0,
                challenger_total INTEGER DEFAULT 0,
                opponent_total INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # ── Saqlanganlar (Bookmarks) ──
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                test_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chat_id, test_id)
            )
        """)
        # ── Bildirishnomalar sozlamalari ──
        # Certificates
        cur.execute("""
            CREATE TABLE IF NOT EXISTS certificates(
                certificate_id TEXT PRIMARY KEY,
                chat_id INTEGER,
                test_id TEXT,
                recipient_name TEXT,
                test_name TEXT,
                score REAL,
                issue_date TEXT,
                png_path TEXT,
                pdf_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS notification_settings(
                chat_id INTEGER PRIMARY KEY,
                daily_reminder INTEGER DEFAULT 1,
                weekly_report INTEGER DEFAULT 1,
                new_test_alert INTEGER DEFAULT 1
            )
        """)
        conn.commit()
        conn.close()

    # ── User CRUD ──
    @db_lock
    def create_user(self, chat_id):
        self.cur.execute("INSERT OR IGNORE INTO user(chat_id) VALUES (?)", (chat_id,))
        self.conn.commit()

    @db_lock
    def update_user_data(self, chat_id, key, value):
        allowed = {"first_name", "last_name", "phone_number", "lang_id", "xp", "level", "badges"}
        if key not in allowed:
            return
        self.cur.execute(f"UPDATE user SET {key} = ? WHERE chat_id = ?", (value, chat_id))
        self.conn.commit()

    @db_lock
    def update_last_active(self, chat_id):
        self.cur.execute("UPDATE user SET last_active = CURRENT_TIMESTAMP WHERE chat_id = ?", (chat_id,))
        self.conn.commit()

    @db_lock
    def get_user_by_chat_id(self, chat_id):
        self.cur.execute("SELECT * FROM user WHERE chat_id = ?", (chat_id,))
        return dict_fetchone(self.cur)

    @db_lock
    def get_all_users(self):
        self.cur.execute("SELECT * FROM user ORDER BY id DESC")
        return dict_fetchall(self.cur)

    @db_lock
    def get_users_count(self):
        self.cur.execute("SELECT COUNT(*) FROM user")
        row = self.cur.fetchone()
        return int(row[0]) if row else 0

    @db_lock
    def delete_user(self, chat_id):
        self.cur.execute("DELETE FROM user WHERE chat_id = ?", (chat_id,))
        self.conn.commit()

    # ── Test natijalar ──
    @db_lock
    def insert_stats_users(self, chat_id, point_test, precent, test_id):
        self.cur.execute(
            "INSERT INTO users_results (chat_id, point_test, precent_corr_ans, test_id) VALUES (?,?,?,?)",
            (chat_id, point_test, precent, test_id)
        )
        self.conn.commit()

    @db_lock
    def count_all_users(self):
        self.cur.execute("SELECT COUNT(*) FROM users_results")
        row = self.cur.fetchone()
        return int(row[0]) if row else 0

    @db_lock
    def count_test_users(self, test_id):
        self.cur.execute("SELECT COUNT(*) FROM users_results WHERE test_id = ?", (test_id,))
        row = self.cur.fetchone()
        return int(row[0]) if row else 0

    @db_lock
    def get_place_user(self, test_id, user_point):
        self.cur.execute(
            "SELECT COUNT(*) FROM users_results WHERE test_id = ? AND point_test > ?",
            (test_id, user_point)
        )
        row = self.cur.fetchone()
        return int(row[0]) + 1 if row else 1

    @db_lock
    def check_first_attempt(self, chat_id, test_id):
        self.cur.execute(
            "SELECT 1 FROM users_results WHERE chat_id = ? AND test_id = ?",
            (chat_id, test_id)
        )
        return self.cur.fetchone() is not None

    @db_lock
    def get_user_stats(self, chat_id):
        self.cur.execute(
            """SELECT ur.test_id, ur.point_test, ur.precent_corr_ans, tm.title
               FROM users_results ur
               LEFT JOIN tests_meta tm ON ur.test_id = tm.test_id
               WHERE ur.chat_id = ? ORDER BY ur.rowid DESC""",
            (chat_id,)
        )
        return dict_fetchall(self.cur)

    # ── Test meta ──
    @db_lock
    def save_test_meta(self, test_id, chat_id, title, description, amount, point_per_q=1, time_per_q=10):
        self.cur.execute(
            """INSERT OR REPLACE INTO tests_meta
               (test_id, chat_id, title, description, amount, point_per_q, time_per_q)
               VALUES (?,?,?,?,?,?,?)""",
            (test_id, chat_id, title, description, amount, point_per_q, time_per_q)
        )
        self.conn.commit()

    @db_lock
    def get_test_meta(self, test_id):
        self.cur.execute("SELECT * FROM tests_meta WHERE test_id = ?", (test_id,))
        return dict_fetchone(self.cur)

    @db_lock
    def get_user_tests(self, chat_id):
        self.cur.execute(
            "SELECT * FROM tests_meta WHERE chat_id = ? ORDER BY id DESC", (chat_id,)
        )
        return dict_fetchall(self.cur)

    @db_lock
    def update_test_meta(self, test_id, key, value):
        allowed = {"title", "description", "point_per_q", "time_per_q"}
        if key not in allowed:
            return
        self.cur.execute(f"UPDATE tests_meta SET {key} = ? WHERE test_id = ?", (value, test_id))
        self.conn.commit()

    @db_lock
    def delete_test_meta(self, test_id):
        self.cur.execute("DELETE FROM tests_meta WHERE test_id = ?", (test_id,))
        self.conn.commit()

    # ── Fikrlar ──
    @db_lock
    def save_feedback(self, chat_id, message):
        self.cur.execute(
            "INSERT INTO feedbacks (chat_id, message) VALUES (?,?)", (chat_id, message)
        )
        self.conn.commit()

    @db_lock
    def get_all_feedbacks(self):
        self.cur.execute(
            """SELECT f.*, u.first_name, u.last_name, u.phone_number
               FROM feedbacks f
               LEFT JOIN user u ON f.chat_id = u.chat_id
               ORDER BY f.id DESC"""
        )
        return dict_fetchall(self.cur)

    @db_lock
    def get_feedbacks_count(self):
        self.cur.execute("SELECT COUNT(*) FROM feedbacks")
        row = self.cur.fetchone()
        return int(row[0]) if row else 0

    # ══════════════════════════════════════
    #  LEADERBOARD (Reyting)
    # ══════════════════════════════════════
    @db_lock
    def get_global_leaderboard(self, limit=10):
        self.cur.execute("""
            SELECT u.chat_id, u.first_name, u.last_name, u.xp, u.level,
                   COALESCE(SUM(ur.point_test), 0) as total_score,
                   COUNT(ur.id) as tests_count,
                   COALESCE(AVG(ur.precent_corr_ans), 0) as avg_accuracy
            FROM user u
            LEFT JOIN users_results ur ON u.chat_id = ur.chat_id
            WHERE u.first_name IS NOT NULL
            GROUP BY u.chat_id
            ORDER BY total_score DESC
            LIMIT ?
        """, (limit,))
        return dict_fetchall(self.cur)

    @db_lock
    def get_weekly_leaderboard(self, limit=10):
        self.cur.execute("""
            SELECT u.chat_id, u.first_name, u.last_name,
                   COALESCE(SUM(ur.point_test), 0) as total_score,
                   COUNT(ur.id) as tests_count
            FROM user u
            JOIN users_results ur ON u.chat_id = ur.chat_id
            WHERE ur.created_at >= datetime('now', '-7 days')
            AND u.first_name IS NOT NULL
            GROUP BY u.chat_id
            ORDER BY total_score DESC
            LIMIT ?
        """, (limit,))
        return dict_fetchall(self.cur)

    @db_lock
    def get_leaderboard_by_test(self, test_id, limit=10):
        self.cur.execute("""
            SELECT u.chat_id, u.first_name, u.last_name,
                   ur.point_test, ur.precent_corr_ans
            FROM users_results ur
            JOIN user u ON ur.chat_id = u.chat_id
            WHERE ur.test_id = ?
            ORDER BY ur.point_test DESC
            LIMIT ?
        """, (test_id, limit))
        return dict_fetchall(self.cur)

    # ══════════════════════════════════════
    #  GAMIFICATION (XP, Daraja, Badge)
    # ══════════════════════════════════════
    @db_lock
    def get_user_xp_level(self, chat_id):
        self.cur.execute("SELECT xp, level, badges FROM user WHERE chat_id = ?", (chat_id,))
        row = self.cur.fetchone()
        if row:
            return {"xp": row[0] or 0, "level": row[1] or 1, "badges": row[2] or ""}
        return {"xp": 0, "level": 1, "badges": ""}

    @db_lock
    def add_user_xp(self, chat_id, amount):
        self.cur.execute("SELECT xp, level FROM user WHERE chat_id = ?", (chat_id,))
        row = self.cur.fetchone()
        current_xp = row[0] or 0 if row else 0
        current_level = row[1] or 1 if row else 1
        
        new_xp = current_xp + amount
        # Daraja hisoblash: har 100 XP = 1 daraja, max 10
        new_level = min(10, 1 + new_xp // 100)
        self.cur.execute("UPDATE user SET xp = ?, level = ? WHERE chat_id = ?", (new_xp, new_level, chat_id))
        self.conn.commit()
        return {"xp": new_xp, "level": new_level, "leveled_up": new_level > current_level, "old_level": current_level}

    @db_lock
    def add_user_badge(self, chat_id, badge):
        self.cur.execute("SELECT badges FROM user WHERE chat_id = ?", (chat_id,))
        row = self.cur.fetchone()
        current = row[0] or "" if row else ""
        
        if badge not in current:
            new_badges = f"{current},{badge}" if current else badge
            self.cur.execute("UPDATE user SET badges = ? WHERE chat_id = ?", (new_badges, chat_id))
            self.conn.commit()
            return True
        return False

    # ══════════════════════════════════════
    #  DAILY CHALLENGE (Kundalik test)
    # ══════════════════════════════════════
    @db_lock
    def get_daily_challenge(self, date_str):
        self.cur.execute("SELECT * FROM daily_challenges WHERE date = ?", (date_str,))
        return dict_fetchone(self.cur)

    @db_lock
    def save_daily_challenge(self, date_str, test_data, fan):
        self.cur.execute(
            "INSERT OR REPLACE INTO daily_challenges (date, test_data, fan) VALUES (?,?,?)",
            (date_str, test_data, fan)
        )
        self.conn.commit()

    @db_lock
    def get_user_streak(self, chat_id):
        self.cur.execute("SELECT * FROM user_streaks WHERE chat_id = ?", (chat_id,))
        row = dict_fetchone(self.cur)
        if not row:
            return {"current_streak": 0, "max_streak": 0, "last_date": ""}
        return row

    @db_lock
    def update_user_streak(self, chat_id, date_str):
        self.cur.execute("SELECT * FROM user_streaks WHERE chat_id = ?", (chat_id,))
        row = dict_fetchone(self.cur)
        if not row:
            streak = {"current_streak": 0, "max_streak": 0, "last_date": ""}
        else:
            streak = row
            
        from datetime import datetime, timedelta
        today = datetime.strptime(date_str, "%Y-%m-%d")
        if streak["last_date"]:
            try:
                last = datetime.strptime(streak["last_date"], "%Y-%m-%d")
                diff = (today - last).days
            except:
                diff = 999
        else:
            diff = 999
        if diff == 0:
            return streak
        if diff == 1:
            new_streak = streak["current_streak"] + 1
        else:
            new_streak = 1
        new_max = max(streak["max_streak"], new_streak)
        self.cur.execute(
            "INSERT OR REPLACE INTO user_streaks (chat_id, current_streak, max_streak, last_date) VALUES (?,?,?,?)",
            (chat_id, new_streak, new_max, date_str)
        )
        self.conn.commit()
        return {"current_streak": new_streak, "max_streak": new_max, "last_date": date_str}

    # ══════════════════════════════════════
    #  WRONG ANSWERS (Xato javoblar)
    # ══════════════════════════════════════
    @db_lock
    def save_wrong_answer(self, chat_id, question, correct, user_ans, test_id):
        self.cur.execute(
            "INSERT INTO wrong_answers (chat_id, question, correct_answer, user_answer, test_id) VALUES (?,?,?,?,?)",
            (chat_id, question, correct, user_ans, test_id)
        )
        self.conn.commit()
        # Add to spaced repetition
        import datetime, pytz
        tz = pytz.timezone('Asia/Tashkent')
        next_review = (datetime.datetime.now(tz) + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        # Check if already exists
        self.cur.execute('SELECT id FROM spaced_repetition WHERE chat_id = ? AND question = ? AND test_id = ?', (chat_id, question, test_id))
        if not self.cur.fetchone():
            self.cur.execute("""
                INSERT INTO spaced_repetition (chat_id, question, correct_answer, test_id, next_review_date, interval)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (chat_id, question, correct, test_id, next_review))
            self.conn.commit()

    @db_lock
    def get_wrong_answers(self, chat_id, limit=50):
        self.cur.execute(
            "SELECT * FROM wrong_answers WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
            (chat_id, limit)
        )
        return dict_fetchall(self.cur)

    @db_lock
    def get_wrong_answers_count(self, chat_id):
        self.cur.execute("SELECT COUNT(*) FROM wrong_answers WHERE chat_id = ?", (chat_id,))
        row = self.cur.fetchone()
        return int(row[0]) if row else 0

    @db_lock
    def clear_wrong_answers(self, chat_id):
        self.cur.execute("DELETE FROM wrong_answers WHERE chat_id = ?", (chat_id,))
        self.conn.commit()

    # ══════════════════════════════════════
    #  DUELS (Bellashuv)
    # ══════════════════════════════════════
    @db_lock
    def create_duel(self, challenger_id, test_id):
        self.cur.execute(
            "INSERT INTO duels (challenger_id, test_id) VALUES (?,?)",
            (challenger_id, test_id)
        )
        self.conn.commit()
        return self.cur.lastrowid

    @db_lock
    def get_duel(self, duel_id):
        self.cur.execute("SELECT * FROM duels WHERE id = ?", (duel_id,))
        return dict_fetchone(self.cur)

    @db_lock
    def accept_duel(self, duel_id, opponent_id):
        self.cur.execute(
            "UPDATE duels SET opponent_id = ?, status = 'active' WHERE id = ? AND status = 'pending'",
            (opponent_id, duel_id)
        )
        self.conn.commit()

    @db_lock
    def update_duel_score(self, duel_id, chat_id, score, total):
        duel = self.get_duel(duel_id)
        if not duel:
            return
        if chat_id == duel["challenger_id"]:
            self.cur.execute("UPDATE duels SET challenger_score = ?, challenger_total = ? WHERE id = ?", (score, total, duel_id))
        elif chat_id == duel["opponent_id"]:
            self.cur.execute("UPDATE duels SET opponent_score = ?, opponent_total = ? WHERE id = ?", (score, total, duel_id))
        self.conn.commit()

    @db_lock
    def complete_duel(self, duel_id):
        self.cur.execute("UPDATE duels SET status = 'completed' WHERE id = ?", (duel_id,))
        self.conn.commit()

    @db_lock
    def get_pending_duels_for(self, chat_id):
        self.cur.execute(
            """SELECT d.*, u.first_name, u.last_name FROM duels d
               JOIN user u ON d.challenger_id = u.chat_id
               WHERE d.status = 'pending' AND d.challenger_id != ?
               ORDER BY d.id DESC LIMIT 10""",
            (chat_id,)
        )
        return dict_fetchall(self.cur)

    @db_lock
    def find_random_match(self, chat_id):
        self.cur.execute("SELECT id FROM duels WHERE status = 'pending' AND challenger_id != ? ORDER BY RANDOM() LIMIT 1", (chat_id,))
        res = self.cur.fetchone()
        return res[0] if res else None

    @db_lock
    def get_my_duels(self, chat_id, limit=10):
        self.cur.execute(
            """SELECT d.*,
                      u1.first_name as ch_name, u1.last_name as ch_lname,
                      u2.first_name as op_name, u2.last_name as op_lname
               FROM duels d
               LEFT JOIN user u1 ON d.challenger_id = u1.chat_id
               LEFT JOIN user u2 ON d.opponent_id = u2.chat_id
               WHERE d.challenger_id = ? OR d.opponent_id = ?
               ORDER BY d.id DESC LIMIT ?""",
            (chat_id, chat_id, limit)
        )
        return dict_fetchall(self.cur)

    # ══════════════════════════════════════
    #  ANALYTICS (Batafsil analitika)
    # ══════════════════════════════════════
    @db_lock
    def get_user_analytics(self, chat_id):
        self.cur.execute("""
            SELECT COUNT(*) as total_tests,
                   COALESCE(SUM(point_test), 0) as total_score,
                   COALESCE(AVG(precent_corr_ans), 0) as avg_accuracy,
                   COALESCE(MAX(precent_corr_ans), 0) as best_accuracy,
                   COALESCE(MIN(precent_corr_ans), 0) as worst_accuracy
            FROM users_results WHERE chat_id = ?
        """, (chat_id,))
        return dict_fetchone(self.cur)

    @db_lock
    def get_recent_results(self, chat_id, limit=10):
        self.cur.execute("""
            SELECT ur.*, tm.title FROM users_results ur
            LEFT JOIN tests_meta tm ON ur.test_id = tm.test_id
            WHERE ur.chat_id = ? ORDER BY ur.id DESC LIMIT ?
        """, (chat_id, limit))
        return dict_fetchall(self.cur)

    @db_lock
    def get_user_global_rank(self, chat_id):
        self.cur.execute("""
            SELECT COUNT(*) + 1 FROM (
                SELECT ur2.chat_id, SUM(ur2.point_test) as total
                FROM users_results ur2 GROUP BY ur2.chat_id
            ) ranks WHERE ranks.total > (
                SELECT COALESCE(SUM(point_test), 0) FROM users_results WHERE chat_id = ?
            )
        """, (chat_id,))
        row = self.cur.fetchone()
        return int(row[0]) if row else 1


    # ══════════════════════════════════════
    #  ADMIN ANALYTICS
    # ══════════════════════════════════════
    @db_lock
    def get_admin_analytics(self):
        """Admin uchun batafsil statistika."""
        result = {}
        # Bugungi yangi userlar
        self.cur.execute("SELECT COUNT(*) FROM user WHERE last_active >= date('now')")
        row = self.cur.fetchone()
        result['today_users'] = int(row[0]) if row else 0
        # Haftalik yangi userlar  
        self.cur.execute("SELECT COUNT(*) FROM user WHERE last_active >= date('now', '-7 days')")
        row = self.cur.fetchone()
        result['week_users'] = int(row[0]) if row else 0
        # Oylik
        self.cur.execute("SELECT COUNT(*) FROM user WHERE last_active >= date('now', '-30 days')")
        row = self.cur.fetchone()
        result['month_users'] = int(row[0]) if row else 0
        # Umumiy
        self.cur.execute("SELECT COUNT(*) FROM user")
        row = self.cur.fetchone()
        result['total_users'] = int(row[0]) if row else 0
        # Bugungi testlar
        self.cur.execute("SELECT COUNT(*) FROM users_results WHERE created_at >= date('now')")
        row = self.cur.fetchone()
        result['today_tests'] = int(row[0]) if row else 0
        # Haftalik testlar
        self.cur.execute("SELECT COUNT(*) FROM users_results WHERE created_at >= date('now', '-7 days')")
        row = self.cur.fetchone()
        result['week_tests'] = int(row[0]) if row else 0
        # Oylik testlar
        self.cur.execute("SELECT COUNT(*) FROM users_results WHERE created_at >= date('now', '-30 days')")
        row = self.cur.fetchone()
        result['month_tests'] = int(row[0]) if row else 0
        # Umumiy test natijalari
        self.cur.execute("SELECT COUNT(*) FROM users_results")
        row = self.cur.fetchone()
        result['total_results'] = int(row[0]) if row else 0
        # Yaratilgan testlar
        self.cur.execute("SELECT COUNT(*) FROM tests_meta")
        row = self.cur.fetchone()
        result['total_tests_created'] = int(row[0]) if row else 0
        # O'rtacha aniqlik
        self.cur.execute("SELECT AVG(precent_corr_ans) FROM users_results")
        row = self.cur.fetchone()
        result['avg_accuracy'] = round(float(row[0]), 1) if row and row[0] else 0
        # TOP 5 mashhur testlar
        self.cur.execute("""
            SELECT tm.title, tm.test_id, COUNT(ur.id) as play_count
            FROM users_results ur
            JOIN tests_meta tm ON ur.test_id = tm.test_id
            GROUP BY ur.test_id
            ORDER BY play_count DESC
            LIMIT 5
        """)
        result['top_tests'] = dict_fetchall(self.cur)
        # Fikrlar soni
        self.cur.execute("SELECT COUNT(*) FROM feedbacks")
        row = self.cur.fetchone()
        result['feedbacks'] = int(row[0]) if row else 0
        return result

    @db_lock
    def get_all_categories(self):
        self.cur.execute("SELECT * FROM categories ORDER BY id")
        return dict_fetchall(self.cur)

    @db_lock
    def get_tests_by_category(self, category_id, limit=20):
        self.cur.execute("""
            SELECT tm.*, u.first_name, u.last_name,
                   (SELECT COUNT(*) FROM users_results ur WHERE ur.test_id = tm.test_id) as play_count
            FROM tests_meta tm
            LEFT JOIN user u ON tm.chat_id = u.chat_id
            WHERE tm.category_id = ?
            ORDER BY tm.id DESC LIMIT ?
        """, (category_id, limit))
        return dict_fetchall(self.cur)

    @db_lock 
    def update_test_category(self, test_id, category_id):
        self.cur.execute("UPDATE tests_meta SET category_id = ? WHERE test_id = ?", (category_id, test_id))
        self.conn.commit()


    # Certificates
    @db_lock
    def save_certificate(self, cert_id, chat_id, test_id, recipient_name, test_name, score, issue_date, png_path, pdf_path):
        self.cur.execute("""
            INSERT INTO certificates 
            (certificate_id, chat_id, test_id, recipient_name, test_name, score, issue_date, png_path, pdf_path) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cert_id, chat_id, test_id, recipient_name, test_name, score, issue_date, png_path, pdf_path))
        self.conn.commit()

    @db_lock
    def get_certificate(self, cert_id):
        self.cur.execute("SELECT * FROM certificates WHERE certificate_id = ?", (cert_id,))
        return dict_fetchone(self.cur)



    # ══════════════════════════════════════
    #  FEATURES DB METHODS
    # ══════════════════════════════════════
    
    @db_lock
    def get_daily_reward_status(self, chat_id):
        self.cur.execute('SELECT last_reward_date, reward_cycle_day, current_streak, max_streak FROM user_streaks WHERE chat_id = ?', (chat_id,))
        return dict_fetchone(self.cur)
        
    @db_lock
    def update_daily_reward_status(self, chat_id, last_reward_date, reward_cycle_day, streak, max_streak):
        self.cur.execute("""
            INSERT OR REPLACE INTO user_streaks (chat_id, current_streak, max_streak, last_date, last_reward_date, reward_cycle_day)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chat_id, streak, max_streak, last_reward_date, last_reward_date, reward_cycle_day))
        self.conn.commit()
        
    # MISSIONS
    @db_lock
    def get_user_missions(self, chat_id, mission_type, reset_date):
        self.cur.execute('SELECT * FROM user_missions WHERE chat_id = ? AND mission_type = ? AND reset_date = ?', (chat_id, mission_type, reset_date))
        return dict_fetchall(self.cur)
        
    @db_lock
    def add_user_mission(self, chat_id, mission_type, mission_key, target_value, reward_type, reward_amount, reset_date):
        self.cur.execute("""
            INSERT INTO user_missions (chat_id, mission_type, mission_key, target_value, current_value, reward_type, reward_amount, completed, reset_date)
            VALUES (?, ?, ?, ?, 0, ?, ?, 0, ?)
        """, (chat_id, mission_type, mission_key, target_value, reward_type, reward_amount, reset_date))
        self.conn.commit()
        
    @db_lock
    def update_mission_progress(self, chat_id, mission_key, increment=1):
        self.cur.execute('SELECT id, current_value, target_value, completed FROM user_missions WHERE chat_id = ? AND mission_key = ? AND completed = 0 ORDER BY id DESC LIMIT 1', (chat_id, mission_key))
        row = dict_fetchone(self.cur)
        if not row: return None
        
        new_val = row['current_value'] + increment
        completed = 1 if new_val >= row['target_value'] else 0
        
        self.cur.execute('UPDATE user_missions SET current_value = ?, completed = ? WHERE id = ?', (new_val, completed, row['id']))
        self.conn.commit()
        return completed
        
    # SPACED REPETITION
    @db_lock
    def add_spaced_repetition(self, chat_id, question, correct_answer, test_id, next_review_date):
        # check if it already exists
        self.cur.execute('SELECT id FROM spaced_repetition WHERE chat_id = ? AND question = ? AND test_id = ?', (chat_id, question, test_id))
        if self.cur.fetchone():
            return False
            
        self.cur.execute("""
            INSERT INTO spaced_repetition (chat_id, question, correct_answer, test_id, next_review_date, interval)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (chat_id, question, correct_answer, test_id, next_review_date))
        self.conn.commit()
        return True
        
    @db_lock
    def get_due_spaced_repetitions(self, chat_id, current_date_str):
        self.cur.execute('SELECT * FROM spaced_repetition WHERE chat_id = ? AND next_review_date <= ?', (chat_id, current_date_str))
        return dict_fetchall(self.cur)
        
    @db_lock
    def update_spaced_repetition(self, item_id, next_review_date, interval):
        self.cur.execute('UPDATE spaced_repetition SET next_review_date = ?, interval = ? WHERE id = ?', (next_review_date, interval, item_id))
        self.conn.commit()
        
    @db_lock
    def remove_spaced_repetition(self, item_id):
        self.cur.execute('DELETE FROM spaced_repetition WHERE id = ?', (item_id,))
        self.conn.commit()

    # FRIENDS & REFERRAL
    @db_lock
    def add_friend(self, user_id, friend_id):
        if user_id == friend_id: return False
        try:
            self.cur.execute('INSERT INTO friends (user_id, friend_id) VALUES (?, ?)', (user_id, friend_id))
            self.cur.execute('INSERT INTO friends (user_id, friend_id) VALUES (?, ?)', (friend_id, user_id))
            self.conn.commit()
            return True
        except: return False
        
    @db_lock
    def get_friends(self, user_id):
        self.cur.execute('SELECT friend_id FROM friends WHERE user_id = ?', (user_id,))
        return [row[0] for row in self.cur.fetchall()]
        
    @db_lock
    def get_friends_leaderboard(self, user_id, limit=10):
        self.cur.execute("""
            SELECT u.chat_id, u.first_name, u.last_name, u.xp, u.level
            FROM user u
            JOIN friends f ON u.chat_id = f.friend_id
            WHERE f.user_id = ?
            ORDER BY u.xp DESC
            LIMIT ?
        """, (user_id, limit))
        return dict_fetchall(self.cur)
        
    # MATCHMAKING
    @db_lock
    def enter_matchmaking(self, chat_id):
        try:
            self.cur.execute('INSERT INTO matchmaking_queue (chat_id) VALUES (?)', (chat_id,))
            self.conn.commit()
            return True
        except: return False
        
    @db_lock
    def exit_matchmaking(self, chat_id):
        self.cur.execute('DELETE FROM matchmaking_queue WHERE chat_id = ?', (chat_id,))
        self.conn.commit()
        
    @db_lock
    def find_match(self, chat_id):
        # find someone else in queue
        self.cur.execute('SELECT chat_id FROM matchmaking_queue WHERE chat_id != ? ORDER BY joined_at ASC LIMIT 1', (chat_id,))
        row = self.cur.fetchone()
        if row:
            opponent_id = row[0]
            # remove both from queue
            self.cur.execute('DELETE FROM matchmaking_queue WHERE chat_id IN (?, ?)', (chat_id, opponent_id))
            self.conn.commit()
            return opponent_id
        return None
        
    # TOURNAMENTS
    @db_lock
    def create_tournament(self, name, test_id, start_time, duration):
        self.cur.execute("""
            INSERT INTO tournaments (name, test_id, start_time, duration, status)
            VALUES (?, ?, ?, ?, 'draft')
        """, (name, test_id, start_time, duration))
        self.conn.commit()
        return self.cur.lastrowid
        
    @db_lock
    def get_active_tournaments(self):
        self.cur.execute('SELECT * FROM tournaments WHERE status != "archived" AND status != "cancelled"')
        return dict_fetchall(self.cur)
        
    @db_lock
    def get_tournament(self, t_id):
        self.cur.execute('SELECT * FROM tournaments WHERE id = ?', (t_id,))
        return dict_fetchone(self.cur)
        
    @db_lock
    def update_tournament_status(self, t_id, status):
        self.cur.execute('UPDATE tournaments SET status = ? WHERE id = ?', (status, t_id))
        self.conn.commit()
        
    @db_lock
    def register_tournament(self, t_id, chat_id):
        try:
            self.cur.execute('INSERT INTO tournament_participants (tournament_id, chat_id) VALUES (?, ?)', (t_id, chat_id))
            self.conn.commit()
            return True
        except: return False
        
    @db_lock
    def get_tournament_participants(self, t_id):
        self.cur.execute('SELECT chat_id FROM tournament_participants WHERE tournament_id = ?', (t_id,))
        return [row[0] for row in self.cur.fetchall()]
        
    @db_lock
    def update_tournament_score(self, t_id, chat_id, score, time_taken):
        self.cur.execute('UPDATE tournament_participants SET score = ?, time_taken = ?, finished = 1 WHERE tournament_id = ? AND chat_id = ?', (score, time_taken, t_id, chat_id))
        self.conn.commit()
        
    @db_lock
    def get_tournament_leaderboard(self, t_id, limit=10):
        self.cur.execute("""
            SELECT u.chat_id, u.first_name, u.last_name, tp.score, tp.time_taken
            FROM tournament_participants tp
            JOIN user u ON tp.chat_id = u.chat_id
            WHERE tp.tournament_id = ? AND tp.finished = 1
            ORDER BY tp.score DESC, tp.time_taken ASC
            LIMIT ?
        """, (t_id, limit))
        return dict_fetchall(self.cur)
        
    # SUBJECT MASTERY
    @db_lock
    def get_subject_mastery(self, chat_id, category_id):
        self.cur.execute('SELECT * FROM subject_mastery WHERE chat_id = ? AND category_id = ?', (chat_id, category_id))
        row = dict_fetchone(self.cur)
        if not row:
            return {'xp': 0, 'level': 1, 'tests_completed': 0, 'total_score': 0}
        return row
        
    @db_lock
    def get_all_subject_masteries(self, chat_id):
        self.cur.execute("""
            SELECT sm.*, c.name_uz, c.name_ru, c.name_en, c.emoji
            FROM subject_mastery sm
            JOIN categories c ON sm.category_id = c.id
            WHERE sm.chat_id = ?
        """, (chat_id,))
        return dict_fetchall(self.cur)
        
    @db_lock
    def update_subject_mastery(self, chat_id, category_id, xp_add, score_add):
        current = self.get_subject_mastery(chat_id, category_id)
        new_xp = current['xp'] + xp_add
        new_level = 1 + new_xp // 100
        new_tests = current['tests_completed'] + 1
        new_score = current['total_score'] + score_add
        
        self.cur.execute("""
            INSERT OR REPLACE INTO subject_mastery (chat_id, category_id, xp, level, tests_completed, total_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chat_id, category_id, new_xp, new_level, new_tests, new_score))
        self.conn.commit()
        return new_level > current.get('level', 1)
        
    # WEEKLY DIGEST
    @db_lock
    def has_sent_weekly_digest(self, chat_id, year_week):
        self.cur.execute('SELECT 1 FROM weekly_digest_log WHERE chat_id = ? AND year_week = ?', (chat_id, year_week))
        return bool(self.cur.fetchone())
        
    @db_lock
    def log_weekly_digest(self, chat_id, year_week):
        self.cur.execute('INSERT OR IGNORE INTO weekly_digest_log (chat_id, year_week) VALUES (?, ?)', (chat_id, year_week))
        self.conn.commit()
        
    # SEASONAL LEADERBOARDS
    @db_lock
    def get_active_season(self):
        self.cur.execute('SELECT * FROM seasons WHERE status = "active" ORDER BY id DESC LIMIT 1')
        return dict_fetchone(self.cur)
        
    @db_lock
    def create_season(self, name_uz, name_ru, name_en, start_date, end_date):
        self.cur.execute('UPDATE seasons SET status = "archived" WHERE status = "active"')
        self.cur.execute("""
            INSERT INTO seasons (name_uz, name_ru, name_en, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?, 'active')
        """, (name_uz, name_ru, name_en, start_date, end_date))
        self.conn.commit()
        
    @db_lock
    def add_seasonal_score(self, season_id, chat_id, score_add):
        self.cur.execute('SELECT score FROM seasonal_scores WHERE season_id = ? AND chat_id = ?', (season_id, chat_id))
        row = self.cur.fetchone()
        if row:
            new_score = row[0] + score_add
            self.cur.execute('UPDATE seasonal_scores SET score = ? WHERE season_id = ? AND chat_id = ?', (new_score, season_id, chat_id))
        else:
            self.cur.execute('INSERT INTO seasonal_scores (season_id, chat_id, score) VALUES (?, ?, ?)', (season_id, chat_id, score_add))
        self.conn.commit()
        
    @db_lock
    def get_seasonal_leaderboard(self, season_id, limit=10):
        self.cur.execute("""
            SELECT u.chat_id, u.first_name, u.last_name, ss.score
            FROM seasonal_scores ss
            JOIN user u ON ss.chat_id = u.chat_id
            WHERE ss.season_id = ?
            ORDER BY ss.score DESC
            LIMIT ?
        """, (season_id, limit))
        return dict_fetchall(self.cur)
        


def dict_fetchall(cursor):
    if cursor.description is None:
        return []
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dict_fetchone(cursor):
    if cursor.description is None:
        return False
    row = cursor.fetchone()
    if row is None:
        return False
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))