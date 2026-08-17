import os
import faiss
import numpy as np
from database import take_all_chunk
from embedding import get_embedding

DIMENSION = 1024
INDEX_FILE = "knowledge.index"
TEMP_INDEX_FILE = "knowledge.index.tmp"

def _normalize(matrix):
  matrix = np.array(matrix, dtype="float32")
  norms = np.linalg.norm(matrix, axis=1, keepdims=True)
  norms[norms == 0] = 1.0
  return matrix / norms

def cari_embedding(index, query_embedding, top_k=3):
  query = np.array([query_embedding], dtype="float32")
  norm = np.linalg.norm(query)
  if norm > 0:
    query = query / norm
  scores, indexes = index.search(query, top_k)
  return scores, indexes

def simpan_index(ids, vectors):
  if len(ids) == 0 or len(vectors) == 0:
    raise ValueError("Tidak ada data untuk menyimpan index")

  normalized = _normalize(vectors)
  index = faiss.IndexIDMap(faiss.IndexFlatIP(DIMENSION))
  index.add_with_ids(normalized, np.array(ids, dtype="int64"))
  faiss.write_index(index, TEMP_INDEX_FILE)
  os.replace(TEMP_INDEX_FILE, INDEX_FILE)

def rebuild_faiss():
  chunks = take_all_chunk()
  ids = []
  vectors = []
  for id, source, chunk in chunks:
    ids.append(int(id))
    vectors.append(get_embedding(chunk))
  simpan_index(ids, vectors)

def load_index():
  index = faiss.read_index(INDEX_FILE)
  return index