import json
with open("responses.json","r") as file:
  responses = json.load(file)

def get_reply(message):
  message = message.strip().lower()
  reply = responses.get(message, "Maaf saya tidak mengerti")
  return reply