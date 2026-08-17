import sqlite3
from contextlib import closing

DB_FILE = "database.db"
TIMEOUT = 10

def build_table_history():
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn, conn:
    conn.execute(
      """CREATE TABLE IF NOT EXISTS history(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT,
      sender TEXT,
      text TEXT
      )"""
    )
    columns = [row[1] for row in conn.execute("PRAGMA table_info(history)").fetchall()]
    if "user_id" not in columns:
      conn.execute("ALTER TABLE history ADD COLUMN user_id TEXT")

def insert_history(user_id, sender, text):
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn, conn:
    conn.execute(
      """INSERT INTO history(user_id, sender, text)
      VALUES(?,?,?)""", (user_id, sender, text)
    )

def get_history(user_id):
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn:
    return conn.execute(
      """SELECT id, user_id, sender, text
      FROM history
      WHERE user_id = ?
      ORDER BY id""", (user_id,)
    ).fetchall()

def clear_history(user_id):
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn, conn:
    conn.execute("DELETE FROM history WHERE user_id = ?", (user_id,))

def build_table_knowledge():
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn, conn:
    conn.execute(
      """CREATE TABLE IF NOT EXISTS knowledge(id INTEGER PRIMARY KEY AUTOINCREMENT, 
      source TEXT NOT NULL, 
      chunk TEXT NOT NULL
      )"""
    )

def insert_knowledge(source, chunk):
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn, conn:
    cursor = conn.execute(
      """INSERT INTO knowledge(source, chunk) 
      VALUES(?,?)""", (source, chunk)
    )
    return cursor.lastrowid

def take_all_chunk():
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn:
    return conn.execute("""
      SELECT id, source, chunk
      FROM knowledge
      ORDER BY id;
      """).fetchall()

def get_chunk_by_id(id):
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn:
    row = conn.execute("""
      SELECT chunk
      FROM knowledge
      WHERE id = ?""", (id,)).fetchone()
  if row is None:
    return None
  return row[0]

def clear_knowledge():
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn, conn:
    conn.execute("DELETE FROM knowledge")

def knowledge_exists():
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn:
    jumlah = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
  return jumlah > 0