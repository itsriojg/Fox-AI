import sqlite3

def build_table_history():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute(
    """CREATE TABLE IF NOT EXISTS history(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      sender TEXT,
      text TEXT
      )"""
    )
  conn.commit()
  conn.close()
  
def insert_history(sender, text):
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute(
    """INSERT INTO history(sender, text)
    VALUES(?,?)""", (sender, text)
    )
  conn.commit()
  conn.close()
  
def get_history():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("SELECT*FROM history")
  results = cursor.fetchall()
  conn.close()
  return results
  
def clear_history():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("DELETE FROM history")
  conn.commit()
  conn.close()
  
def build_table_knowledge():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute(
    """CREATE TABLE IF NOT EXISTS knowledge(id INTEGER PRIMARY KEY AUTOINCREMENT, 
    source TEXT NOT NULL, 
    chunk TEXT NOT NULL
    )"""
    )
  conn.commit()
  conn.close()
  
def insert_knowledge(source, chunk):
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute(
    """INSERT INTO knowledge(source, chunk) 
    VALUES(?,?)""", (source, chunk)
    )
  conn.commit()
  conn.close()
  
def take_all_chunk():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("""
    SELECT id, source, chunk
    FROM knowledge
    ORDER BY id;
    """)
  chunks = cursor.fetchall()
  conn.close()
  return chunks
  
def get_chunk_by_id(id):
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("""
    SELECT chunk
    FROM knowledge
    WHERE id = ?""", (id,))
  chunk = cursor.fetchone()[0]
  conn.close()
  return chunk