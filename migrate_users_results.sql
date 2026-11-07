CREATE TABLE users_results_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    point_test INTEGER,
    precent_corr_ans REAL,
    test_id TEXT,
    speed_bonus REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chat_id) REFERENCES user(chat_id) ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO users_results_new (chat_id, point_test, precent_corr_ans, test_id, speed_bonus)
SELECT chat_id, point_test, precent_corr_ans, test_id, speed_bonus FROM users_results;
DROP TABLE users_results;
ALTER TABLE users_results_new RENAME TO users_results;
