import os
import requests
from dotenv import load_dotenv

load_dotenv()
JINA_API_KEY = os.getenv("JINA_API_KEY")

def get_embedding(text):
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
    return response.json()["data"][0]["embedding"]
  except requests.exceptions.Timeout:
    raise RuntimeError("Embedding API timeout: server terlalu lama merespons")
  except requests.exceptions.RequestException as e:
    raise RuntimeError(f"Embedding API error: {e}")
  except (KeyError, ValueError) as e:
    raise RuntimeError("Format respons embedding tidak valid") from e