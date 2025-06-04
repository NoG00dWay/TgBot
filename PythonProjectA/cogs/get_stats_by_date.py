import sqlite3
from datetime import datetime

def get_stats_by_date(start_date, end_date, user_id):

    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')

        if start_date > end_date:
            return {'error': 'Начальная дата не может быть позже конечной'}

        conn = None
        try:
                conn = sqlite3.connect('db/finance.db')
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT 
                        SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
                        SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as expense
                    FROM transactions
                    WHERE 
                        date BETWEEN ? AND ?
                        AND user_id = ?
                ''',(start_date, end_date, user_id))

                result = cursor.fetchone()
                conn.close()
                return {
                    'Доходы': result[0] or 0,
                    'Расходы': abs(result[1]) if result[1] else 0,
                    'Переиод': f'{start_date} - {end_date}'
                }

        except sqlite3.Error as e:
            return {'error': f'Ошибка базы данных: {str(e)}'}
        finally:
            if conn:
                conn.close()

    except ValueError:
        return {'error': 'Неверный формат даты. Использкйте формат "YYYY-MM-DD"'}
    except Exception as e:
        return {'error': f'Неожиданная ошибка: {str(e)}'}
