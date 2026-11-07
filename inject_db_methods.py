import sys

with open('database.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
methods = '''
    # ══════════════════════════════════════
    #  FEATURES DB METHODS
    # ══════════════════════════════════════
    
    @db_lock
    @db_lock
    def get_daily_reward_status(self, chat_id):
        self.cur.execute('SELECT last_reward_date, reward_cycle_day, current_streak, max_streak FROM user_streaks WHERE chat_id = ?', (chat_id,))
        return dict_fetchone(self.cur)
        
    @db_lock
    @db_lock
    def update_daily_reward_status(self, chat_id, last_reward_date, reward_cycle_day, streak, max_streak):
        self.cur.execute("""
            INSERT OR REPLACE INTO user_streaks (chat_id, current_streak, max_streak, last_date, last_reward_date, reward_cycle_day)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chat_id, streak, max_streak, last_reward_date, last_reward_date, reward_cycle_day))
        self.conn.commit()
        
    # MISSIONS
    @db_lock
    @db_lock
    def get_user_missions(self, chat_id, mission_type, reset_date):
        self.cur.execute('SELECT * FROM user_missions WHERE chat_id = ? AND mission_type = ? AND reset_date = ?', (chat_id, mission_type, reset_date))
        return dict_fetchall(self.cur)
        
    @db_lock
    @db_lock
    def add_user_mission(self, chat_id, mission_type, mission_key, target_value, reward_type, reward_amount, reset_date):
        self.cur.execute("""
            INSERT INTO user_missions (chat_id, mission_type, mission_key, target_value, current_value, reward_type, reward_amount, completed, reset_date)
            VALUES (?, ?, ?, ?, 0, ?, ?, 0, ?)
        """, (chat_id, mission_type, mission_key, target_value, reward_type, reward_amount, reset_date))
        self.conn.commit()
        
    @db_lock
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
    @db_lock
    def get_due_spaced_repetitions(self, chat_id, current_date_str):
        self.cur.execute('SELECT * FROM spaced_repetition WHERE chat_id = ? AND next_review_date <= ?', (chat_id, current_date_str))
        return dict_fetchall(self.cur)
        
    @db_lock
    @db_lock
    def update_spaced_repetition(self, item_id, next_review_date, interval):
        self.cur.execute('UPDATE spaced_repetition SET next_review_date = ?, interval = ? WHERE id = ?', (next_review_date, interval, item_id))
        self.conn.commit()
        
    @db_lock
    @db_lock
    def remove_spaced_repetition(self, item_id):
        self.cur.execute('DELETE FROM spaced_repetition WHERE id = ?', (item_id,))
        self.conn.commit()

    # FRIENDS & REFERRAL
    @db_lock
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
    @db_lock
    def get_friends(self, user_id):
        self.cur.execute('SELECT friend_id FROM friends WHERE user_id = ?', (user_id,))
        return [row[0] for row in self.cur.fetchall()]
        
    @db_lock
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
    @db_lock
    def enter_matchmaking(self, chat_id):
        try:
            self.cur.execute('INSERT INTO matchmaking_queue (chat_id) VALUES (?)', (chat_id,))
            self.conn.commit()
            return True
        except: return False
        
    @db_lock
    @db_lock
    def exit_matchmaking(self, chat_id):
        self.cur.execute('DELETE FROM matchmaking_queue WHERE chat_id = ?', (chat_id,))
        self.conn.commit()
        
    @db_lock
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
    @db_lock
    def create_tournament(self, name, test_id, start_time, duration):
        self.cur.execute("""
            INSERT INTO tournaments (name, test_id, start_time, duration, status)
            VALUES (?, ?, ?, ?, 'draft')
        """, (name, test_id, start_time, duration))
        self.conn.commit()
        return self.cur.lastrowid
        
    @db_lock
    @db_lock
    def get_active_tournaments(self):
        self.cur.execute('SELECT * FROM tournaments WHERE status != "archived" AND status != "cancelled"')
        return dict_fetchall(self.cur)
        
    @db_lock
    @db_lock
    def get_tournament(self, t_id):
        self.cur.execute('SELECT * FROM tournaments WHERE id = ?', (t_id,))
        return dict_fetchone(self.cur)
        
    @db_lock
    @db_lock
    def update_tournament_status(self, t_id, status):
        self.cur.execute('UPDATE tournaments SET status = ? WHERE id = ?', (status, t_id))
        self.conn.commit()
        
    @db_lock
    @db_lock
    def register_tournament(self, t_id, chat_id):
        try:
            self.cur.execute('INSERT INTO tournament_participants (tournament_id, chat_id) VALUES (?, ?)', (t_id, chat_id))
            self.conn.commit()
            return True
        except: return False
        
    @db_lock
    @db_lock
    def get_tournament_participants(self, t_id):
        self.cur.execute('SELECT chat_id FROM tournament_participants WHERE tournament_id = ?', (t_id,))
        return [row[0] for row in self.cur.fetchall()]
        
    @db_lock
    @db_lock
    def update_tournament_score(self, t_id, chat_id, score, time_taken):
        self.cur.execute('UPDATE tournament_participants SET score = ?, time_taken = ?, finished = 1 WHERE tournament_id = ? AND chat_id = ?', (score, time_taken, t_id, chat_id))
        self.conn.commit()
        
    @db_lock
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
    @db_lock
    def get_subject_mastery(self, chat_id, category_id):
        self.cur.execute('SELECT * FROM subject_mastery WHERE chat_id = ? AND category_id = ?', (chat_id, category_id))
        row = dict_fetchone(self.cur)
        if not row:
            return {'xp': 0, 'level': 1, 'tests_completed': 0, 'total_score': 0}
        return row
        
    @db_lock
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
    @db_lock
    def has_sent_weekly_digest(self, chat_id, year_week):
        self.cur.execute('SELECT 1 FROM weekly_digest_log WHERE chat_id = ? AND year_week = ?', (chat_id, year_week))
        return bool(self.cur.fetchone())
        
    @db_lock
    @db_lock
    def log_weekly_digest(self, chat_id, year_week):
        self.cur.execute('INSERT OR IGNORE INTO weekly_digest_log (chat_id, year_week) VALUES (?, ?)', (chat_id, year_week))
        self.conn.commit()
        
    # SEASONAL LEADERBOARDS
    @db_lock
    @db_lock
    def get_active_season(self):
        self.cur.execute('SELECT * FROM seasons WHERE status = "active" ORDER BY id DESC LIMIT 1')
        return dict_fetchone(self.cur)
        
    @db_lock
    @db_lock
    def create_season(self, name_uz, name_ru, name_en, start_date, end_date):
        self.cur.execute('UPDATE seasons SET status = "archived" WHERE status = "active"')
        self.cur.execute("""
            INSERT INTO seasons (name_uz, name_ru, name_en, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?, 'active')
        """, (name_uz, name_ru, name_en, start_date, end_date))
        self.conn.commit()
        
    @db_lock
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
        
'''

insert_marker = 'def dict_fetchall(cursor):'
if insert_marker in content and '# FEATURES DB METHODS' not in content:
    parts = content.split(insert_marker)
    new_content = parts[0] + methods + '\n\n' + insert_marker + parts[1]
    with open('database.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Methods injected successfully!')
else:
    print('Failed to inject or already injected.')
