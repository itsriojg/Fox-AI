import faiss
import numpy as np
from database import take_all_chunk
from embedding import get_embedding

DIMENSION = 1024

def cari_embedding(index, query_embedding, top_k=3):
  query_embedding = np.array([query_embedding], dtype="float32")
  scores, indexes = index.search(query_embedding, top_k)
  return scores, indexes
  
def rebuild_faiss():
  index = faiss.IndexIDMap(faiss.IndexFlatIP(DIMENSION))
  chunks = take_all_chunk()
  ids = []
  vectors = []
  for id, source, chunk in chunks:
    ids.append(int(id))
    vectors.append(get_embedding(chunk))
  index.add_with_ids(np.array(vectors, dtype="float32"), np.array(ids, dtype="int64"))
  faiss.write_index(index, "knowledge.index")
  
def load_index():
  index = faiss.read_index("knowledge.index")
  return index