import sqlite3

DB="chat.db"

def init_db():

    conn=sqlite3.connect(DB)
    cur=conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    content TEXT
    )
    """)

    conn.commit()
    conn.close()


def save(role,content):

    conn=sqlite3.connect(DB)
    cur=conn.cursor()

    cur.execute(
    "INSERT INTO messages(role,content) VALUES(?,?)",
    (role,content)
    )

    conn.commit()
    conn.close()


def history(limit=12):

    conn=sqlite3.connect(DB)
    cur=conn.cursor()

    cur.execute(
    "SELECT role,content FROM messages ORDER BY id DESC LIMIT ?",
    (limit,)
    )

    rows=cur.fetchall()

    conn.close()

    rows.reverse()

    return [{"role":r[0],"content":r[1]} for r in rows]