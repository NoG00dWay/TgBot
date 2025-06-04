import sqlite3

def get_stats_by_category(categories, user_id):
    try:
        conn = sqlite3.connect('db/finance.db')
        cursor = conn.cursor()

        placeholders = ','.join(['?'] * len(categories))
        query = f'''
            SELECT category, ABS(SUM(amount)) 
            FROM transactions 
            WHERE category IN ({placeholders}) 
                AND amount < 0 
                AND user_id = ?
            GROUP BY category
        '''

        params = categories + [user_id]
        cursor.execute(query, params)
        results = dict(cursor.fetchall())
        total = sum(results.values())

        print('\nСтатистикика по категориям:')
        for category, amount in results.items():
            print(f'{category}: {amount} руб.')

        return (results, total)

    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return {}, 0
    finally:
        if conn:
            conn.close()


def view_by_dates(categories, user_id):
    '''Функция для просмотра статистики по датам'''

    print('\nПросмотр расходоа по датам:')
    start_date = input('Введите начальную дату (ГГГГ-ММ-ДД):')
    end_date = input('Введите конечную дату (ГГГГ-ММ-ДД):')

    try:
        conn = sqlite3.connect('db/finance.db')
        cursor = conn.cursor()

        placeholders = ','.join(['?'] * len(categories))
        query = f'''
            SELECT date, category, ABS(amount)
            FROM transactions
            WHERE category IN ({placeholders})
                AND amount < 0
                AND date BETWEEN ? AND ?
                AND user_id = ?
            ORDER BY date
        '''

        cursor.execute(query,categories + [start_date, end_date + user_id])
        transactions = cursor.fetchall()

        if not transactions:
            print('\nНет данных за указанный период.')
            return

        print('\nРасходы по выбранным категориям:')
        current_date = None
        for date, category, amount in transactions:
            if date != current_date:
                print(f'\n{date}:')
                current_date = date
            print(f' {category}: {amount} руб.')

    except sqlite3.Error as e:
        print(f'Ошибка базы данных: {e}')
    except ValueError:
        print('Неверный формат даты. Использкйте ГГГГ-ММ-ДД. Например 2003-01-15')
    finally:
        if conn:
            conn.close()
