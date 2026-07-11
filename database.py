import sqlite3

def build_database():
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