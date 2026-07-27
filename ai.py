import requests
import os
import time
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
    start = time.time()
    for i in range(3):
      response = requests.post(
        url = url,
        headers = headers,
        json = body,
        timeout = 30
    )
      print("STATUS:", response.status_code)
      if response.status_code == 200:
        break

      if response.status_code == 429:
        print("Rate limit. Menunggu 10 detik...")
        time.sleep(10)
        continue

      break
      
    end = time.time()
    print(f"Waktu request Gemini: {end - start:.2f} detik")
  except ConnectionError:
    return "Tidak dapat terhubung ke server, silahkan periksa kembali koneksi internet Anda"
  except Timeout:
    return "Maaf, server terlalu lama merespon. Silahkan coba lagi"
  except Exception:
    return "Maaf, terjadi kesalahan. Silahkan coba lagi"
    
  if response.status_code != 200:
    return "Maaf, server sedang mengalami kendala. Silakan coba beberapa saat lagi."

  data = response.json()
  candidates = data.get("candidates")

  if candidates:
    return candidates[0]["content"]["parts"][0]["text"]

  return "Maaf, AI tidak memberikan jawaban."
