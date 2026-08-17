from database import insert_history, get_history, clear_history

def tambah_message(user_id, sender, text):
  insert_history(user_id, sender, text)

def ambil_history(user_id):
  results = get_history(user_id)
  hasil = []
  for row in results:
    pesan = {
    "sender": row[2],
    "text": row[3]
    }
    hasil.append(pesan)
  return hasil

def hapus_history(user_id):
  clear_history(user_id)