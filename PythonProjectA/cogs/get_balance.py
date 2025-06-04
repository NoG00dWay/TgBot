import sqlite3

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