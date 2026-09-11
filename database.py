import sqlite3
from contextlib import closing

DB_FILE = "database.db"
TIMEOUT = 10

def _ensure_wal(conn):
  # Biar sqlite3 manual bisa intip pas stan jalan tanpa ke-block write.
  try:
    conn.execute("PRAGMA journal_mode=WAL")
  except Exception:
    pass

def build_table_history():
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn, conn:
    _ensure_wal(conn)
    conn.execute(
      """CREATE TABLE IF NOT EXISTS history(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT,
      sender TEXT,
      text TEXT,
      created_at TEXT
      )"""
    )
    columns = [row[1] for row in conn.execute("PRAGMA table_info(history)").fetchall()]
    if "user_id" not in columns:
      conn.execute("ALTER TABLE history ADD COLUMN user_id TEXT")
    if "created_at" not in columns:
      # Baris lama (dev) biarin NULL biar ga ngotorin statistik PKKMB.
      # (ALTER ga boleh bawa default fungsi, insert baru isi eksplisit.)
      conn.execute("ALTER TABLE history ADD COLUMN created_at TEXT")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_history_user_created ON history(user_id, created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_history_created ON history(created_at)")

def build_table_audit():
  # Append-only: TIDAK ikut /clear. 1 baris per 1 pertanyaan user.
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn, conn:
    _ensure_wal(conn)
    conn.execute(
      """CREATE TABLE IF NOT EXISTS chat_audit(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      created_at TEXT DEFAULT (datetime('now','localtime')),
      user_id TEXT,
      ip TEXT,
      endpoint TEXT,
      user_text TEXT,
      hit_knowledge INTEGER,
      latency_ms INTEGER,
      error TEXT,
      miss_reason TEXT
      )"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_created ON chat_audit(created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON chat_audit(user_id, created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_hit ON chat_audit(hit_knowledge, created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_miss ON chat_audit(miss_reason, created_at)")
    # Migrasi DB lama (sebelum kolom miss_reason ada).
    cols = [row[1] for row in conn.execute("PRAGMA table_info(chat_audit)").fetchall()]
    if "miss_reason" not in cols:
      conn.execute("ALTER TABLE chat_audit ADD COLUMN miss_reason TEXT")

def insert_audit(user_id, ip, endpoint, user_text, hit_knowledge, latency_ms, error=None, miss_reason=None):
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn, conn:
    conn.execute(
      """INSERT INTO chat_audit(user_id, ip, endpoint, user_text, hit_knowledge, latency_ms, error, miss_reason, created_at)
      VALUES(?,?,?,?,?,?,?,?,datetime('now','localtime'))""",
      (user_id, ip, endpoint, user_text, hit_knowledge, latency_ms, error, miss_reason)
    )

def insert_history(user_id, sender, text):
  with closing(sqlite3.connect(DB_FILE, timeout=TIMEOUT)) as conn, conn:
    conn.execute(
      """INSERT INTO history(user_id, sender, text, created_at)
      VALUES(?,?,?,datetime('now','localtime'))""", (user_id, sender, text)
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