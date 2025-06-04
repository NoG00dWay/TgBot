import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('db/finance.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount INTEGER,
            user_id INTEGER,
            date TEXT NOT NULL,
            category TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    conn.commit()
    conn.close()


def show_transaction():
    conn = sqlite3.connect('db/finance.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM transaction WHERE user_id')

    for row in cursor.fetchall():
        print(row)


