import sqlite3

def delete_last_record(user_id):
    try:
        with sqlite3.connect('db/finance.db') as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT COUNT(*) FROM transactions
                WHERE user_id = ?
            ''', (user_id,))

            if cursor.fetchone()[0] == 0:
                print('У пользователя не записей для удаления')
                return False

            cursor.execute('''
                DELETE FROM transactions
                WHERE id = (
                    SELECT id FROM transactions
                    WHERE user_id = ?
                    ORDER BY id DESC
                    LIMIT 1)
            ''', (user_id,))

            conn.commit()

            if cursor.rowcount > 0:
                print('Последняя запись пользователя успешно удалена')
                return  True
            else:
                print('Не удалось удалить запись')
                return False

    except sqlite3.Error as e:
        print(f'Ошибка базы данных при удалении: {str(e)}')
        return False
