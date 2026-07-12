from database import insert_history, get_history, clear_history

def tambah_message(sender, text):
  insert_history(sender, text)
  
def ambil_history():
  results = get_history()
  hasil = []
  for row in results:
    pesan = {
    "sender": row[1],
    "text": row[2]
    }
    hasil.append(pesan)
  return hasil
  
def hapus_history():
  clear_history()