import os
import requests
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()
JINA_API_KEY = os.getenv("JINA_API_KEY")

# Cache embedding query di memori (LRU 512). Pertanyaan PKKMB banyak yang
# sama/diulan-ulang -> cache hit = skip HTTP Jina total (0,5-2 dtk hemat).
# Key = teks query persis; miss = hit API sekali lalu disimpan. Build-time
# (rag.py/vector_db.py) ikut kecache tapi cuma 22 chunk, negligible.
# Trade-off sadar: teks beda 1 char = miss. Ga pake normalisasi fuzzy biar
# ga salah arti (misal "ketua" vs "ketua?").
@lru_cache(maxsize=512)
def _fetch_embedding(text):
  headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "Content-Type": "application/json"
    }
  body = {
        "model": "jina-embeddings-v5-text-small",
        "input": [text]
    }
  try:
    response = requests.post(
          "https://api.jina.ai/v1/embeddings",
          headers=headers,
          json=body,
          timeout=30
      )
    response.raise_for_status()
    return tuple(response.json()["data"][0]["embedding"])
  except requests.exceptions.Timeout:
    raise RuntimeError("Embedding API timeout: server terlalu lama merespons")
  except requests.exceptions.RequestException as e:
    raise RuntimeError(f"Embedding API error: {e}")
  except (KeyError, ValueError) as e:
    raise RuntimeError("Format respons embedding tidak valid") from e

def get_embedding(text):
  # lru_cache ga bisa cache list (unhashable) -> balikin list copy biar
  # pemanggil bebas mutasi tanpa ngerusak cache.
  return list(_fetch_embedding(text))

def cache_info():
  return _fetch_embedding.cache_info()