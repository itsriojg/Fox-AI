from ai import get_ai_reply
from prompt import SYSTEM_PROMPT
from embedding import get_embedding
from vector_db import load_index, cari_embedding, rebuild_faiss
from database import get_chunk_by_id
import os

if os.path.exists("knowledge.index"):
    index = load_index()
else:
    rebuild_faiss()
    index = load_index()

def get_reply(message, history):
  query_embedding = get_embedding(message)
  context = []
  scores, indexes = cari_embedding(index, query_embedding, top_k=3)
  for id in indexes[0]:
    if id == -1:
      continue
    chunk = get_chunk_by_id(id)
    context.append(chunk)
  knowledge = "\n\n".join(context)
  
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
  
  reply = get_ai_reply(prompt)
  return reply