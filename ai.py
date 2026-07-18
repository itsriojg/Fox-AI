import requests
import os
from dotenv import load_dotenv
from requests.exceptions import ConnectionError, Timeout

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"

def get_ai_reply(prompt):
  url = URL
  headers = {
    "Content-Type": "application/json"
  }
  body = {
    "contents": [
        {
            "parts": [
                {
                    "text": prompt
                }
            ]
        }
    ]
  }
  try:
  response = requests.post(
    url = URL,
    headers = headers,
    json = body,
    timeout = 10
    )
  except ConnectionError:
    return "Tidak dapat terhubung ke server, silahkan periksa kembali koneksi internet Anda"
  except Timeout:
    return "Maaf, server terlalu lama merespon. Silahkan coba lagi"
  except Exception:
    return "Maaf, terjadi kesalahan. Silahkan coba lagi"
  if response.status_code == 200:
    data = response.json()
    candidates = data.get("candidates")
    if candidates:
      return candidates[0]["content"]["parts"][0]["text"]
  return "Maaf, server sedang mengalami kendala."