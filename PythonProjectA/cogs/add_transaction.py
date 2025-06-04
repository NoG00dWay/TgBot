import sqlite3
from datetime import datetime

def add_transaction(user_id, date, category, amount, description = 'other'):
    try:
        datetime.strptime(date, '%Y-%m-%d')

        try:
            conn = sqlite3.connect('db/finance.db')
            cursor = conn.cursor()

            cursor.execute('INSERT INTO transactions (user_id, date, category, description, amount ) VALUES (?, ?, ?, ?, ?)', (user_id, date, category, description, amount))

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            return {'error': f'Ошибка базы данных: {str(e)}'}
        finally:
            if conn:
                conn.close()

    except ValueError:
        return {'error': 'Неверный формат даты или числа. Используйте формат для даты "YYYY-MM-DD"'}
    except Exception as e:
        return {'error': f'Неожиданная ошибка: {str(e)}'}