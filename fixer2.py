with open('database.py', 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

insert_idx = -1
for i, l in enumerate(lines):
    if 'CREATE TABLE IF NOT EXISTS notification_settings(' in l:
        insert_idx = i - 1
        break

if insert_idx != -1:
    methods = """        # Certificates
        cur.execute(\"\"\"
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
        \"\"\")
"""
    lines.insert(insert_idx, methods)

with open('database.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
