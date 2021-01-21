import sqlite3
from contextlib import closing

def get_times(user_id):
    with closing(sqlite3.connect('CrosswordDB.db')) as conn:
        with closing(conn.cursor()) as c:
            c.execute('SELECT date, time FROM DATES_TIMES WHERE user_id = ?', user_id)
            date_times = c.fetchall()
    return date_times



def insert_null_time(user_id, date):
    """ Date must be fomated YYYY-MM-DD"""
    with closing(sqlite3.connect('CrosswordDB.db')) as conn:
        with closing(conn.cursor()) as c:
            c.execute('INSERT INTO DATES_TIMES (date, user_id) VALUES(?, ?)', (date, user_id))


def get_remindees(date):
    """ Get all users opting for reminders who have a null-time at date"""
    with closing(sqlite3.connect('CrosswordDB.db')) as conn:
        with closing(conn.cursor()) as c:
            c.execute('SELECT USER_DATA.user_id '
                      'FROM DATES_TIMES '
                      'JOIN USER_DATA '
                      'ON USER_DATA.user_id = DATES_TIMES.user_id AND USER_DATA.remind = "1" '
                      'WHERE date = ? AND time IS NULL', date)
            remindees = c.fetchall()
    return remindees


def set_remind(user_id, remind):
    pass