import threading
from functools import wraps

def db_lock(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with self.lock:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                # To prevent silent failures in db, print or log, then raise
                raise
    return wrapper

with open('database.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'import threading' not in content:
    content = content.replace('import sqlite3', 'import sqlite3\nimport threading\nfrom functools import wraps\n\ndef db_lock(func):\n    @wraps(func)\n    def wrapper(self, *args, **kwargs):\n        with self.lock:\n            return func(self, *args, **kwargs)\n    return wrapper')

if 'self.lock = threading.Lock()' not in content:
    content = content.replace('self.cur = self.conn.cursor()', 'self.cur = self.conn.cursor()\n        self.lock = threading.Lock()')

new_content = []
lines = content.split('\n')
inside_db = False
for i, line in enumerate(lines):
    if line.startswith('class Database:'):
        inside_db = True
    if inside_db and line.startswith('    def ') and 'def __init__' not in line and 'def create_database' not in line:
        if lines[i-1].strip() not in ('@db_lock', '@staticmethod'):
            new_content.append('    @db_lock')
    new_content.append(line)

with open('database.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_content))
