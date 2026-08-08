import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
api_key = os.getenv("GROQ_API_KEY"),
base_url = os.getenv("GROQ_BASE_URL")
)

MODEL = "llama-3.3-70b-versatile"

def get_ai_reply(system_prompt, prompt):
  try:
    start = time.time()

    response = client.chat.completions.create(
    model=MODEL,
    messages=[
      {
       "role": "system",
       "content": system_prompt
      },
      {
       "role": "user",
       "content": prompt
      }
    ],
    timeout=10
  )
    end = time.time()
    print(f"Model : {MODEL}")
    print(f"Waktu request: {end - start:.2f} detik")
    return response.choices[0].message.content

  except Exception as e:
    print(e)
    return "Maaf, server sedang mengalami kendala. Silakan coba lagi."