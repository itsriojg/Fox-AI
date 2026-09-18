from ai import get_ai_reply
from prompt import system_prompt
from embedding import get_embedding
from vector_db import load_index, cari_embedding, rebuild_faiss
from database import get_chunks_by_ids
import os

SIMILARITY_THRESHOLD = 0.55
# Diukur 2026-09-11 (23 query, Jina 1024-d): valid-HIMATIF top1 0.618-0.717,
# OOT murni (presiden/resep/sudo) <= 0.514. Threshold 0.55 = semua valid lolos,
# OOT murni ke-filter. Gibberish pendek + chit-chat ("p", "kadal", ...) skornya
# 0.55-0.63 (nemu kata himatif) -> DITANGKAP via guard len<3 + tag LLM, bukan sini.
# Efisiensi 2026-09-14: naik ke 0.60 + top_k 15->6 (22 chunk doang, top 6 cukup).
# Efek: input LLM turun ~40%, jawaban lebih nempel data. Kalau [GATAU] naik,
# turunin lagi ke 0.55.
# FIX 2026-09-16: balik ke 0.55 + top_k 6->10. Chunk jawaban ketua (id 2,
# Anindita, skor 0.637 rank 7) ketendang top-6 -> LLM jujur [GATAU] padahal
# data ada. 0.55 tetap aman dari OOT murni (<=0.514).
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

# Alias singkatan user -> istilah knowledge, dipakai SEBELUM embedding.
# Diukur 2026-09-18: "wakahim siapa?" mentah = chunk jawaban (id 2) rank 17
# skor 0.542 (kepotong top_k + di bawah threshold) -> [GATAU] padahal data ada.
# Dinormalisasi "wakil ketua himatif siapa?" = id 2 rank 7 skor 0.62 -> masuk
# konteks -> jawab bener. Deterministik, nol token. Hanya untuk query
# retrieval; teks asli user tetap dikirim ke LLM/history apa adanya.
_ALIAS_TUKAR = [
  # Urutan penting: singkatan di-expand DULUAN, kata dasar (ketua/wakil/
  # sekretaris/bendahara) cuma nambah "himatif" kalau BELUM ada himatif
  # di belakangnya (negative lookahead) biar ga double ("ketua himatif
  # himatif"). Imbuhan -nya/-ku/-mu ikut dikenal.
  ("wakahim", "wakil ketua himatif"),
  ("wakim", "wakil ketua himatif"),
  ("kahim", "ketua himatif"),
  ("sekum", "sekretaris umum himatif"),
  ("bendum", "bendahara umum himatif"),
  ("kadep", "kepala departemen"),
  ("waka", "wakil ketua"),
  ("danus", "dana usaha"),
  ("keorgan", "keorganisasian"),
  ("psdm", "pemberdayaan sumber daya mahasiswa"),
  ("kominfo", "komunikasi dan informasi"),
  ("litbang", "penelitian pengembangan"),
]
# kata dasar + imbuhan opsional, tanpa "himatif" di belakangnya
_DASAR_RE = None

def _normalisasi(query):
  import re as _re
  global _DASAR_RE
  # Urutan: kata dasar DULU (ketua->ketua himatif), BARU singkatan
  # (wakahim->wakil ketua himatif). Kebalik = hasil expand dimakan lagi
  # ("wakil ketua himatif" -> "... himatif ketua himatif").
  if _DASAR_RE is None:
    _DASAR_RE = _re.compile(r"\b(ketua|wakil(?: ketua)?|sekretaris(?: umum)?|bendahara(?: umum)?)(nya|ku|mu)?\b(?!\s+himatif)", _re.IGNORECASE)
  def _dasar(m):
    k = m.group(1).lower()
    if k.startswith("wakil"):
      return "wakil ketua himatif"
    if k.startswith("sekretaris"):
      return "sekretaris umum himatif"
    if k.startswith("bendahara"):
      return "bendahara umum himatif"
    return "ketua himatif"
  s = _DASAR_RE.sub(_dasar, query)
  for singkat, panjang in _ALIAS_TUKAR:
    s = _re.sub(r"\b" + singkat + r"(nya|ku|mu)?\b(?!\s+himatif)", panjang, s, flags=_re.IGNORECASE)
  return s

import sqlite3

if os.path.exists("knowledge.index"):
    index = load_index()
else:
    # Fresh clone: tabel knowledge belum ada (dibuat app.py:60-62 SETELAH
    # import ini) -> jangan crash di import-time. Index dibangun nanti via
    # rag.build_knowledge() (app.py:63-67), atau lazy di bawah saat tabel ada.
    try:
        rebuild_faiss()
        index = load_index()
    except (sqlite3.OperationalError, ValueError, RuntimeError) as e:
        print(f"[WARN] Index belum bisa dibangun saat import: {e}")
        index = None

def build_rag_prompt(message, history):
  global index
  try:
    # Normalisasi alias DULU biar embedding nemu chunk jawaban
    # (wakahim->wakil ketua himatif, dst). Teks asli tetap ke LLM/history.
    query_embedding = get_embedding(_normalisasi(message))
  except RuntimeError:
    return None, None, "embedding_error", 0
  context = []
  # Index belum kebangun (fresh clone, prebuild jalan SETELAH import ini):
  # coba lazy-load kalau file sudah ada, kalau belum -> hit=0, LLM jawab jujur.
  if index is None and os.path.exists("knowledge.index"):
    try:
      index = load_index()
    except Exception as e:
      print(f"[WARN] Gagal lazy-load index: {e}")
  # Query terlalu pendek ("p", "1") = bukan pertanyaan materi. Tetap dijawab
  # LLM (chit-chat) tapi langsung hit=0 biar masuk miss tanpa ngandelin skor.
  if index is not None and len(message.strip()) >= MIN_QUERY_LEN:
    scores, indexes = cari_embedding(index, query_embedding, top_k=15)
    if len(scores) > 0 and len(indexes) > 0:
      # Kumpulin ID lolos threshold dulu, ambil chunk 1 query batch
      # (bukan N+1 query). Urutan skor dijaga biar konteks tetap relevan.
      # top_k 15: chunk jawaban ketua/waka (id 2, skor ~0.64 rank 7-13)
      # kepotong top-10 -> [GATAU] padahal data ada (diukur 2026-09-18).
      # 22 chunk doang, cost token +~500 char, OOT murni tetap kefilter 0.55.
      lolos = []
      for score, id in zip(scores[0], indexes[0]):
        if id == -1:
          continue
        if score >= SIMILARITY_THRESHOLD:
          lolos.append(int(id))
      chunks = get_chunks_by_ids(lolos)
      for id in lolos:
        if id in chunks:
          context.append(_strip_label(chunks[id]))

  hit_knowledge = 1 if context else 0
  knowledge = "\n\n".join(context) if context else "Tidak ada data relevan yang ditemukan."
  
  history_text = ""

  for chat in history[-6:]:
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
