import sqlite3
from datetime import datetime

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            photo     TEXT,
            message   TEXT,
            post_time TEXT NOT NULL,
            status    INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telegram_kanal_id (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            kanal_id     TEXT,
            admin_id     TEXT

        )
    """)


    conn.commit()
    conn.close()

def add_post(message: str, post_time: str, photo: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (photo, message, post_time) VALUES (?, ?, ?)",
        (photo, message, post_time)
    )
    conn.commit()
    conn.close()

def get_pending_posts():
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    posts = cursor.execute(
        "SELECT id, photo, message FROM posts WHERE post_time <= ? AND status = 0",
        (now,)
    ).fetchall()
    conn.close()
    return posts

def update_status(post_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE posts SET status = 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def delete_post(post_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE id = ? AND status = 1", (post_id,))
    conn.commit()
    conn.close()




#  Chanels




def add_channel(channel_id: str, channel_link: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO telegram_kanal_id (kanal_id, admin_id)
        VALUES (?, ?)
        ON CONFLICT(kanal_id) DO UPDATE SET admin_id=excluded.admin_id
    """, (channel_id, channel_link))
    conn.commit()
    conn.close()


def remove_channel(kanal_id: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM telegram_kanal_id WHERE kanal_id=?", (kanal_id,))
    conn.commit()
    conn.close()


def get_channels():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT kanal_id, admin_id FROM telegram_kanal_id")
    rows = cursor.fetchall()
    conn.close()
    return rows










if __name__ == "__main__":
    init_db()