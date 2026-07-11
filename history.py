from flask import session
from database import insert_history

def tambah_message(sender, text):
  if "history" not in session:
    session["history"] = []
  pesan = {
    "sender": sender,
    "text": text
  }
  session["history"].append(pesan)
  insert_history(sender, text)
  session.modified = True
  
def ambil_history():
  if "history" not in session:
    session["history"] = []
  return session["history"]

def hapus_history():
  if "history" not in session:
    session["history"] = []
  session["history"] = []
  session.modified = True