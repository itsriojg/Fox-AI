import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("AI_API_KEY"),
    base_url=os.getenv("AI_BASE_URL")
)

MODEL = "GPT-120B-Fallback"
TIMEOUT = 30

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
    timeout=TIMEOUT
  )
    end = time.time()
    print(f"Model : {MODEL}")
    print(f"Waktu request: {end - start:.2f} detik")
    return response.choices[0].message.content

  except Exception as e:
    print(e)
    return "Maaf, server sedang mengalami kendala. Silakan coba lagi."