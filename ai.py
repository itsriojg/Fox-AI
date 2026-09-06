import os
import re
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TEMPERATURE = 0.7

def sanitize_markdown(text):
  if not text:
    return text
  text = text.replace("—", "-").replace("–", "-")
  text = re.sub(r"(?m)^[ \t]*```.*$", "", text)
  text = re.sub(r"(?m)^[ \t]*---+[ \t]*$", "", text)
  text = re.sub(r"(?m)^[ \t]*\|?[ \t:\-|]+\|[ \t]*$", "", text)
  text = text.replace("\\[", "").replace("\\]", "")
  while text.count("**") % 2 == 1:
    text = "".join(text.rsplit("**", 1))
  text = re.sub(r"(?m)[ \t]+$", "", text)
  text = re.sub(r"\n{3,}", "\n\n", text)
  return text.strip()

client = OpenAI(
    api_key=os.getenv("AI_API_KEY") or os.getenv("GROQ_API_KEY"),
    base_url=os.getenv("AI_BASE_URL") or os.getenv("GROQ_BASE_URL")
)

MODEL = os.getenv("AI_MODEL") or ("GPT-120B-Fallback" if os.getenv("AI_BASE_URL") else "openai/gpt-oss-120b")
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
    temperature=TEMPERATURE,
    timeout=TIMEOUT
  )
    end = time.time()
    print(f"Model : {MODEL}")
    print(f"Waktu request: {end - start:.2f} detik")
    return sanitize_markdown(response.choices[0].message.content)

  except Exception as e:
    print(e)
    return "Maaf, server sedang mengalami kendala. Silakan coba lagi."

def get_ai_reply_stream(system_prompt, prompt):
  start = time.time()
  print(f"Model : {MODEL} [stream]")
  stream = client.chat.completions.create(
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
    temperature=TEMPERATURE,
    timeout=TIMEOUT,
    stream=True
  )
  for chunk in stream:
    try:
      delta = chunk.choices[0].delta.content
    except Exception:
      delta = None
    if delta:
      yield delta
  end = time.time()
  print(f"Waktu stream: {end - start:.2f} detik")