import sqlite3
from config import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    user_id INTEGER,
                    task TEXT
                )''')
    conn.commit()
    conn.close()

def add_task(user_id, task):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO tasks (user_id, task) VALUES (?, ?)", (user_id, task))
    conn.commit()
    conn.close()

def get_tasks(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT rowid, task FROM tasks WHERE user_id = ?", (user_id,))
    results = c.fetchall()
    conn.close()
    return results

def delete_task(user_id, task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE rowid = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()
