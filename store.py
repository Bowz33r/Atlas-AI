import sqlite3, os
from pathlib import Path
from datetime import datetime, timezone

DB = Path(os.getenv("DATA_DIR", "./data")) / "atlas.sqlite3"
DB.parent.mkdir(parents=True, exist_ok=True)

def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, role TEXT NOT NULL, content TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY, note TEXT NOT NULL, created TEXT NOT NULL);
        ''')

def has_user():
    with connect() as c: return c.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None

def create_user(username, password_hash):
    with connect() as c: c.execute("INSERT INTO users VALUES (?,?)", (username, password_hash))

def get_user(username):
    with connect() as c: return c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

def add_message(role, content):
    with connect() as c:
        c.execute("INSERT INTO messages(role,content,created) VALUES (?,?,?)",
                  (role, content[:30000], datetime.now(timezone.utc).isoformat()))

def history(limit=30):
    with connect() as c:
        rows = c.execute("SELECT role,content,created FROM messages ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in reversed(rows)]

def add_memory(note):
    with connect() as c:
        c.execute("INSERT INTO memories(note,created) VALUES (?,?)",
                  (note[:4000], datetime.now(timezone.utc).isoformat()))

def memories(limit=30):
    with connect() as c:
        return [r["note"] for r in c.execute("SELECT note FROM memories ORDER BY id DESC LIMIT ?", (limit,))]
