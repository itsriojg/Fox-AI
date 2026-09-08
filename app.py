import os
import re
import secrets
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, jsonify, session, Response, stream_with_context
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from chatbot import get_reply, build_rag_prompt
from ai import get_ai_reply_stream, sanitize_markdown
from history import tambah_message, ambil_history, hapus_history
from database import build_table_history, build_table_knowledge, knowledge_exists
from rag import build_knowledge
import json

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)

# CORS buat frontend Vue (dev localhost / demo / official).
# FRONTEND_ORIGIN bisa comma-separated, misal:
#   http://localhost:5173,https://himatif.xxx,https://mintif.xxx
FRONTEND_ORIGIN = [o.strip() for o in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",") if o.strip()]
CORS(app, resources={r"/api/*": {"origins": FRONTEND_ORIGIN}})

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

_UID_WEB_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

def ambil_pesan():
  """Pesan dari JSON (frontend Vue) atau form (web Flask lama)."""
  data = request.get_json(silent=True) or {}
  pesan = data.get("pesan") or request.form.get("pesan", "")
  return pesan.strip() if isinstance(pesan, str) else ""

def get_user_id():
  # Frontend Vue kirim user_id sendiri (localStorage) biar lolos beda origin,
  # via JSON atau form. Fallback ke session cookie buat web Flask lama.
  data = request.get_json(silent=True) or {}
  uid = data.get("user_id") or request.form.get("user_id", "")
  if isinstance(uid, str) and _UID_WEB_RE.match(uid):
    return uid
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
    home_url=os.getenv("HOME_URL", "/"),
    riwayat_chat=ambil_history(get_user_id())
  )

@app.route("/api/chat", methods=["POST"])
@limiter.limit("15 per minute; 200 per hour")
def api_chat():
  message = ambil_pesan()
  if message == "":
    return jsonify({
      "error": "Pesan kosong"
    })
  user_id = get_user_id()
  history = ambil_history(user_id)
  reply = get_reply(message, history)
  tambah_message(user_id, "User", message)
  tambah_message(user_id, "AI", sanitize_markdown(reply))

  return jsonify({
    "reply": reply
  })

@app.route("/api/chat/stream", methods=["POST"])
@limiter.limit("15 per minute; 200 per hour")
def api_chat_stream():
  message = ambil_pesan()
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
      tambah_message(user_id, "AI", sanitize_markdown(full))
      yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
    except Exception as e:
      print(f"[STREAM ERROR] {e}")
      if full:
        tambah_message(user_id, "AI", sanitize_markdown(full))
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