import sqlite3
from contextlib import closing

DB_FILE = "database.db"
TIMEOUT = 10

def build_table_history():
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn, conn:
    conn.execute(
      """CREATE TABLE IF NOT EXISTS history(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      sender TEXT,
      text TEXT
      )"""
    )

def insert_history(sender, text):
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn, conn:
    conn.execute(
      """INSERT INTO history(sender, text)
      VALUES(?,?)""", (sender, text)
    )

def get_history():
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn:
    return conn.execute("SELECT * FROM history").fetchall()

def clear_history():
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn, conn:
    conn.execute("DELETE FROM history")

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