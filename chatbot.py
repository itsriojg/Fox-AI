from ai import get_ai_reply
from prompt import SYSTEM_PROMPT

def get_reply(message, knowledge, history):
  history_text = ""

  for chat in history[-10:]:
    history_text += f"{chat['sender']}: {chat['text']}\n"
  
  prompt = f"""{SYSTEM_PROMPT}

Knowledge:
{knowledge}

Riwayat obrolan:
{history_text}

Pertanyaan:
{message}
"""
  print(message)
  print(len(knowledge))

  reply = get_ai_reply(prompt)
  return reply