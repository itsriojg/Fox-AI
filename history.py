from flask import session

def tambah_message(sender, text):
  if "history" not in session:
    session["history"] = []
  pesan = {
    "sender": sender,
    "text": text
  }
  session["history"].append(pesan)
  session.modified = True
  
def ambil_history():
  if "history" not in session:
    session["history"] = []
  return session["history"]
 