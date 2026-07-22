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
  response = requests.post(
        "https://api.jina.ai/v1/embeddings",
        headers=headers,
        json=body
    )
  result = response.json()
  return result["data"][0]["embedding"]