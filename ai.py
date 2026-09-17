import os
import re
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TEMPERATURE = 0.7
# Cap output: jawaban Mintif pendek (paragraf + 2 saran). Tanpa cap, model
# bisa nulis 1000+ token = mahal + stream lama. 500 cukup buat materi + follow-up.
MAX_TOKENS = 500
# gpt-oss-120b = reasoning model: mikir dulu (chunk kosong) SEBELUM jawab.
# Prompt RAG ~7rb char bikin thinking 400+ chunk -> budget 500 habis duluan ->
# finish:length, jawaban 0 char / kepotong tengah kata. reasoning_effort=low
# pangkas thinking (~80 chunk), budget kepakai buat jawaban. Diukur 2026-09-16:
# baseline ketua 499 chunk/0 char/length vs low 79 chunk/stop. Buat tugas Mintif
# (RAG lookup faktual) low cukup; kalau jawaban kompleks menurun, naikkan medium.
REASONING_EFFORT = "low"

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
  """Return (reply, err). err=None sukses, 'llm_error' kalau upstream gagal.
  Dipakai POST /api/chat biar audit bisa bedain jawaban asli vs fallback."""
  try:
    start = time.time()

    # reasoning_effort mungkin ditolak provider non-Groq (9router/Flaz) ->
    # fallback tanpa param biar ga 500 error.
    try:
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
      max_tokens=MAX_TOKENS,
      reasoning_effort=REASONING_EFFORT,
      timeout=TIMEOUT
    )
    except Exception as e:
      if "reasoning_effort" in str(e).lower() or "extra" in str(e).lower() or "unknown" in str(e).lower():
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
        max_tokens=MAX_TOKENS,
        timeout=TIMEOUT
      )
      else:
        raise
    end = time.time()
    print(f"Model : {MODEL}")
    print(f"Waktu request: {end - start:.2f} detik")
    return sanitize_markdown(response.choices[0].message.content), None

  except Exception as e:
    print(e)
    return "Maaf, server sedang mengalami kendala. Silakan coba lagi.", "llm_error"

def _stream_kwargs():
  # reasoning_effort mungkin ditolak provider non-Groq -> pemanggil fallback
  # tanpa param kalau create() raise soal argumen tak dikenal.
  return {
    "model": MODEL,
    "temperature": TEMPERATURE,
    "max_tokens": MAX_TOKENS,
    "timeout": TIMEOUT,
    "reasoning_effort": REASONING_EFFORT,
    "stream": True,
  }

def _open_stream(system_prompt, prompt, with_reasoning=True):
  kw = _stream_kwargs()
  if not with_reasoning:
    kw.pop("reasoning_effort", None)
  return client.chat.completions.create(
    model=kw["model"],
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
    temperature=kw["temperature"],
    max_tokens=kw["max_tokens"],
    timeout=kw["timeout"],
    **({"reasoning_effort": kw["reasoning_effort"]} if with_reasoning else {}),
    stream=True
  )

def _iter_deltas(stream):
  for chunk in stream:
    try:
      delta = chunk.choices[0].delta.content
    except Exception:
      delta = None
    if delta:
      yield delta

def get_ai_reply_stream(system_prompt, prompt):
  start = time.time()
  print(f"Model : {MODEL} [stream]")
  # reasoning_effort mungkin ditolak provider non-Groq (9router/Flaz) ->
  # fallback tanpa param biar ga 500 error. Iterasi dibungkus: penolakan
  # param bisa raise di create() ATAU di chunk pertama.
  try:
    stream = _open_stream(system_prompt, prompt, with_reasoning=True)
    yield from _iter_deltas(stream)
  except Exception as e:
    msg = str(e).lower()
    if "reasoning_effort" in msg or "extra" in msg or "unknown" in msg:
      stream = _open_stream(system_prompt, prompt, with_reasoning=False)
      yield from _iter_deltas(stream)
    else:
      raise
  end = time.time()
  print(f"Waktu stream: {end - start:.2f} detik")