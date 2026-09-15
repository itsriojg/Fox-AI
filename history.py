from database import insert_history, get_history, clear_history

def tambah_message(user_id, sender, text):
  insert_history(user_id, sender, text)

def ambil_history(user_id, limit=None, max_chars=None):
  results = get_history(user_id, limit=limit)
  hasil = []
  for row in results:
    text = row[3]
    # Truncate per pesan cuma buat konteks LLM (hemat token).
    # Render template (/chatbot) panggil tanpa max_chars = full text.
    if max_chars is not None and isinstance(text, str) and len(text) > max_chars:
      text = text[:max_chars] + "..."
    pesan = {
    "sender": row[2],
    "text": text
    }
    hasil.append(pesan)
  return hasil

def hapus_history(user_id):
  clear_history(user_id)