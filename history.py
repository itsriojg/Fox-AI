history = []

def tambah_message(sender, text):
  pesan = {
    "sender": sender,
    "text": text
  }
  history.append(pesan)
  
