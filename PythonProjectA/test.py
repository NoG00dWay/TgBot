import sqlite3

def show_transaction():
    conn = sqlite3.connect('db/finance.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM transactions WHERE user_id')

    for row in cursor.fetchall():
        print(row)

def add_transaction(user_id, date, category, amount, description = 'other'):
    conn = sqlite3.connect('db/finance.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO transactions (user_id, date, category, description, amount ) VALUES (?, ?, ?, ?, ?)', (user_id, date, category, description, amount))

    conn.commit()
    conn.close()

add_transaction(1, '2005-12-10', 'Развлечение', 5000)

def get_balance(user_id):
    try:
        conn = sqlite3.connect('db/finance.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) as income,
                COALESCE(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END), 0) as expense 
            FROM transactions 
            WHERE user_id = ?
        ''', (user_id,))

        income, expense = cursor.fetchone()
        balance = income + expense  # Для расходов берем модуль

        return f"Баланс: {balance} руб.\nДоходы: {income} руб.\nРасходы: {abs(expense)} руб."

    except sqlite3.Error as e:
        return f'Ошибка базы данных: {str(e)}'
    finally:
        if conn:
            conn.close()

show_transaction()

print(get_balance(1325758636))