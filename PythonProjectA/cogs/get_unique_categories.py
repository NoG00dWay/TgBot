import sqlite3


def get_stats_by_category():

    conn = sqlite3.connect('db/finance.db')
    cursor = conn.cursor()

    cursor.execute('SELECT DISTINCT category FROM transaction')
    unique_categories = cursor.fetchone()

    #Преобразование список кортежей в плоский список
    unique_categories = [item[0] for item in unique_categories]

    print(unique_categories)
    conn.close()
    return unique_categories
