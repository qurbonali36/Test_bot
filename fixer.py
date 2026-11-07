with open('database.py', 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

insert_idx = -1
for i, l in enumerate(lines):
    if l.startswith('def dict_fetchall'):
        insert_idx = i
        break

if insert_idx != -1:
    methods = """    # Certificates
    @db_lock
    def save_certificate(self, cert_id, chat_id, test_id, recipient_name, test_name, score, issue_date, png_path, pdf_path):
        self.cur.execute(\"\"\"
            INSERT INTO certificates 
            (certificate_id, chat_id, test_id, recipient_name, test_name, score, issue_date, png_path, pdf_path) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (cert_id, chat_id, test_id, recipient_name, test_name, score, issue_date, png_path, pdf_path))
        self.conn.commit()

    @db_lock
    def get_certificate(self, cert_id):
        self.cur.execute("SELECT * FROM certificates WHERE certificate_id = ?", (cert_id,))
        return dict_fetchone(self.cur)
"""
    lines.insert(insert_idx, methods)

with open('database.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
