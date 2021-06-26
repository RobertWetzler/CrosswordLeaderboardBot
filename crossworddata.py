import sqlite3
from contextlib import closing

def create_db_from_scratch(global_chat_data):
    conn = sqlite3.connect('CrosswordDB.db')
    cur = conn.cursor()
    for chat_id in global_chat_data:
        chat_data = global_chat_data[chat_id]
        """Create Groups"""
        group_name = 'The Doobie Brothers' if chat_id == -1001392971649 else f'Telegram Group {chat_id}'
        cur.execute("INSERT INTO [group](id, name) VALUES(?,?)", (chat_id, group_name))
        wins = dict()
        for name in chat_data['id_mappings']:
            """Create users"""
            user_id = chat_data['id_mappings'][name]
            # God this is so poorly designed
            remind = chat_data['ids'][user_id] if user_id in chat_data['ids'] else True
            cur.execute("INSERT INTO user(user_id, name, remind) VALUES(?,?,?)", (user_id, name, remind))
            """Add User to Group"""
            cur.execute("INSERT INTO is_member(user_id, group_id) VALUES(?,?)", (user_id, chat_id))
            for i in range(len(chat_data['overall'][name])):
                # convert date to iso YYYY-MM-DD
                date = chat_data['overallDates'][i].split('/')
                date_iso = f'{date[2]}-{date[0].zfill(2)}-{date[1].zfill(2)}'
                time = chat_data['overall'][name][i]
                if time is not None:
                    """Insert Time Entry"""
                    cur.execute("INSERT INTO entry(date, user_id, time) VALUES(?,?,?)",
                                (date_iso, user_id, time))
            wins[name] = 0
        for date_i in range(len(chat_data['overallDates'])):
            rank = []
            for name in chat_data['overall']:
                time = chat_data['overall'][name][date_i]
                if time is not None:
                    if len(rank) == 0:
                        rank.append([name])
                    else:
                        # iterate rank to insert name
                        i = 0
                        inserted = False
                        while i < len(rank) and not inserted:
                            if time < chat_data['overall'][rank[i][0]][date_i]:
                                rank.insert(i, [name])
                                inserted = True
                            elif time == chat_data['overall'][rank[i][0]][date_i]:
                                rank[i].append(name)
                                inserted = True
                            else:
                                i += 1
                        if not inserted:
                            rank.append([name])
            for name in rank[0]:
                wins[name] += 1
        """Insert wins by group"""
        for name in wins:
            user_id = chat_data['id_mappings'][name]
            cur.execute("INSERT INTO wins(user_id, group_id, wins) VALUES(?,?,?)", (user_id, chat_id, wins[name]))
    conn.commit()
    conn.close()



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