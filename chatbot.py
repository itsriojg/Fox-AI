responses = {
      "halo" : "Halo juga:)",
      "kamu siapa" : "Saya project pillow-fox",
      "bisa bantu saya?" : "Tentu saja, apa yang bisa saya bantu?",
      "selamat pagi" : "Selamat pagi",
      "" : ""
    }

def get_reply(message):
  message = message.strip().lower()
  reply = responses.get(message, "Maaf saya tidak mengerti")
  return reply