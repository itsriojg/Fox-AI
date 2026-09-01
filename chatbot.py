from ai import get_ai_reply
from prompt import system_prompt
from embedding import get_embedding
from vector_db import load_index, cari_embedding, rebuild_faiss
from database import get_chunk_by_id
import os

SIMILARITY_THRESHOLD = 0.35

if os.path.exists("knowledge.index"):
    index = load_index()
else:
    rebuild_faiss()
    index = load_index()

def build_rag_prompt(message, history):
  try:
    query_embedding = get_embedding(message)
  except RuntimeError:
    return None, None, "embedding_error"
  context = []
  scores, indexes = cari_embedding(index, query_embedding, top_k=5)
  if len(scores) > 0 and len(indexes) > 0:
    for score, id in zip(scores[0], indexes[0]):
      if id == -1:
        continue
      if score >= SIMILARITY_THRESHOLD:
        chunk = get_chunk_by_id(int(id))
        if chunk is not None:
          context.append(chunk)

  knowledge = "\n\n".join(context) if context else "Tidak ada data relevan yang ditemukan."
  
  history_text = ""

  for chat in history[-10:]:
    history_text += f"{chat['sender']}: {chat['text']}\n"
  
  prompt = f"""
Berikut adalah ilmu dan sumber data:
{knowledge}

Berikut adalah riwayat obrolan:
{history_text}

Ini adalah pertanyaan user:
{message}
"""
  return system_prompt, prompt, None

def get_reply(message, history):
  system_p, prompt, err = build_rag_prompt(message, history)
  if err == "embedding_error":
    return "Maaf, layanan pencarian sedang bermasalah. Silakan coba lagi nanti."
  reply = get_ai_reply(system_p, prompt)
  return reply
