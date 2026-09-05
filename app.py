import os
import secrets
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, jsonify, session, Response, stream_with_context
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from chatbot import get_reply, build_rag_prompt
from ai import get_ai_reply_stream
from history import tambah_message, ambil_history, hapus_history
from database import build_table_history, build_table_knowledge, knowledge_exists
from rag import build_knowledge
import json

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)

def get_rate_limit_key():
  if "user_id" in session:
    return f"user:{session['user_id']}"
  return f"ip:{get_remote_address()}"

limiter = Limiter(
  get_rate_limit_key,
  app=app,
  default_limits=[],
  storage_uri="memory://",
)

@app.errorhandler(429)
def rate_limit_exceeded(e):
  return jsonify({
    "error": "Kamu terlalu cepat! Tunggu sebentar sebelum chat lagi."
  }), 429

build_table_history()
build_table_knowledge()
if not knowledge_exists():
  try:
    build_knowledge()
  except Exception as e:
    print(f"[ERROR] Gagal membangun knowledge: {e}")

def get_user_id():
  if "user_id" not in session:
    session["user_id"] = secrets.token_hex(16)
  return session["user_id"]

@app.route("/health")
def health():
  return jsonify({
    "status": "ok"
  })

@app.route("/")
def home():
  return render_template("home.html")

@app.route("/chatbot")
def chatbot():
  return render_template(
    "chatbot.html",
    nama="User",
    riwayat_chat=ambil_history(get_user_id())
  )

@app.route("/api/chat", methods=["POST"])
@limiter.limit("15 per minute; 200 per hour")
def api_chat():
  message = request.form.get("pesan", "")
  if message == "":
    return jsonify({
      "error": "Pesan kosong"
    })
  user_id = get_user_id()
  history = ambil_history(user_id)
  reply = get_reply(message, history)
  tambah_message(user_id, "User", message)
  tambah_message(user_id, "AI", reply)

  return jsonify({
    "reply": reply
  })

@app.route("/api/chat/stream", methods=["POST"])
@limiter.limit("15 per minute; 200 per hour")
def api_chat_stream():
  message = request.form.get("pesan", "")
  if message == "":
    def empty_error():
      yield f"data: {json.dumps({'error': 'Pesan kosong'}, ensure_ascii=False)}\n\n"
    return Response(stream_with_context(empty_error()), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
  user_id = get_user_id()
  history = ambil_history(user_id)
  system_p, prompt, err = build_rag_prompt(message, history)
  if err == "embedding_error":
    def emb_error():
      yield f"data: {json.dumps({'error': 'Maaf, layanan pencarian sedang bermasalah. Silakan coba lagi nanti.'}, ensure_ascii=False)}\n\n"
    return Response(stream_with_context(emb_error()), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
  tambah_message(user_id, "User", message)
  def generate():
    full = ""
    try:
      for token in get_ai_reply_stream(system_p, prompt):
        full += token
        yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
      tambah_message(user_id, "AI", full)
      yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
    except Exception as e:
      print(f"[STREAM ERROR] {e}")
      if full:
        tambah_message(user_id, "AI", full)
      yield f"data: {json.dumps({'error': 'Maaf, server sedang mengalami kendala. Silakan coba lagi.'}, ensure_ascii=False)}\n\n"
  return Response(stream_with_context(generate()), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Content-Type": "text/event-stream"})

@app.route("/clear", methods=["POST"])
def clear_history():
  hapus_history(get_user_id())
  return redirect("/chatbot")

if __name__ == "__main__":
  app.run(
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "5000"))
  )