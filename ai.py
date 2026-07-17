import requests
import os
from dotenv import load_dotenv

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
  response = requests.post(
    url = URL,
    headers = headers,
    json = body
    )
  data = response.json()
  return data["candidates"][0]["content"]["parts"][0]["text"]