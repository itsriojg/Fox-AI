import faiss
import numpy as np
from database import take_all_chunk
from embedding import get_embedding

DIMENSION = 1024

def tambah_embedding(index, embedding):
  embedding = np.array([embedding], dtype="float32")
  index.add(embedding)
  
def cari_embedding(index, query_embedding, top_k=3):
  query_embedding = np.array([query_embedding], dtype="float32")
  scores, indexes = index.search(query_embedding, top_k)
  return scores, indexes
  
def rebuild_faiss():
  index = faiss.IndexFlatIP(DIMENSION)
  chunks = take_all_chunk()
  for id, source, chunk in chunks:
    embedding = get_embedding(chunk)
    tambah_embedding(index, embedding)
  faiss.write_index(index, "knowledge.index")
  
def load_index():
  index = faiss.read_index("knowledge.index")
  return index