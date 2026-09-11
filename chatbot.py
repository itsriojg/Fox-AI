from ai import get_ai_reply
from prompt import system_prompt
from embedding import get_embedding
from vector_db import load_index, cari_embedding, rebuild_faiss
from database import get_chunk_by_id
import os

SIMILARITY_THRESHOLD = 0.55
# Diukur 2026-09-11 (23 query, Jina 1024-d): valid-HIMATIF top1 0.618-0.717,
# OOT murni (presiden/resep/sudo) <= 0.514. Threshold 0.55 = semua valid lolos,
# OOT murni ke-filter. Gibberish pendek + chit-chat ("p", "kadal", ...) skornya
# 0.55-0.63 (nemu kata himatif) -> DITANGKAP via guard len<3 + tag LLM, bukan sini.
MIN_QUERY_LEN = 3

# Prefix struktur chunk ([Bab X - ...] / (bagian N)) = metadata internal retrieval.
# DICOPOT sebelum masuk prompt biar Mimin ga bisa ngutip bab/halaman ke user.
_CHUNK_LABEL_RE = None

def _strip_label(chunk):
  global _CHUNK_LABEL_RE
  import re as _re
  if _CHUNK_LABEL_RE is None:
    _CHUNK_LABEL_RE = _re.compile(r"^\[Bab [^\]]+\]( \(bagian \d+\))?\s*\n?")
  return _CHUNK_LABEL_RE.sub("", chunk).strip()

if os.path.exists("knowledge.index"):
    index = load_index()
else:
    rebuild_faiss()
    index = load_index()

def build_rag_prompt(message, history):
  try:
    query_embedding = get_embedding(message)
  except RuntimeError:
    return None, None, "embedding_error", 0
  context = []
  # Query terlalu pendek ("p", "1") = bukan pertanyaan materi. Tetap dijawab
  # LLM (chit-chat) tapi langsung hit=0 biar masuk miss tanpa ngandelin skor.
  if len(message.strip()) >= MIN_QUERY_LEN:
    scores, indexes = cari_embedding(index, query_embedding, top_k=5)
    if len(scores) > 0 and len(indexes) > 0:
      for score, id in zip(scores[0], indexes[0]):
        if id == -1:
          continue
        if score >= SIMILARITY_THRESHOLD:
          chunk = get_chunk_by_id(int(id))
          if chunk is not None:
            context.append(_strip_label(chunk))

  hit_knowledge = 1 if context else 0
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
  return system_prompt, prompt, None, hit_knowledge

def get_reply(message, history):
  system_p, prompt, err, hit = build_rag_prompt(message, history)
  if err == "embedding_error":
    return "Maaf, layanan pencarian sedang bermasalah. Silakan coba lagi nanti.", 0, err
  reply, llm_err = get_ai_reply(system_p, prompt)
  return reply, hit, llm_err
