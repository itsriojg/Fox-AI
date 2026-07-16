import json
with open("responses.json","r") as file:
  responses = json.load(file)

def clean_message(message):
  message = message.strip().lower()
  message = message.replace("!!!","")
  message = message.replace("!","")
  message = message.replace("?","")
  message = message.replace(".","")
  message = message.replace("!!","")
  return message

def get_reply(message, knowledge):
  message = clean_message(message)
  reply = responses.get(message, "Maaf saya tidak mengerti")
  return reply