import os
import re
import secrets
import time
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, jsonify, session, Response, stream_with_context
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from chatbot import get_reply, build_rag_prompt
from ai import get_ai_reply_stream, sanitize_markdown
from history import tambah_message, ambil_history, hapus_history
from database import build_table_history, build_table_knowledge, build_table_audit, insert_audit, knowledge_exists
from rag import build_knowledge
import json

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)

# Cookie flags: HttpOnly selalu aman. Secure + SameSite cuma nyala di HTTPS
# (env HTTPS=1, di VPS) biar session dev HTTP lokal ga mati.
app.config["SESSION_COOKIE_HTTPONLY"] = True
if os.getenv("HTTPS") == "1":
  app.config["SESSION_COOKIE_SECURE"] = True
  app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# CORS buat frontend Vue (dev localhost / demo / official).
# FRONTEND_ORIGIN bisa comma-separated, misal:
#   http://localhost:5173,https://himatif.xxx,https://mintif.xxx
FRONTEND_ORIGIN = [o.strip() for o in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",") if o.strip()]
CORS(app, resources={r"/api/*": {"origins": FRONTEND_ORIGIN}})

def get_rate_limit_key():
  # Client Vue kirim user_id sendiri (tanpa cookie) -> kunci ikut itu biar
  # maba di NAT kampus (1 IP rame-rame) ga saling makan jatah limit.
  data = request.get_json(silent=True) or {}
  uid = data.get("user_id") or request.form.get("user_id", "")
  if isinstance(uid, str) and _UID_WEB_RE.match(uid):
    return f"user:{uid}"
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
build_table_audit()
build_table_knowledge()
if not knowledge_exists():
  try:
    build_knowledge()
  except Exception as e:
    print(f"[ERROR] Gagal membangun knowledge: {e}")

_UID_WEB_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

MAX_PESAN = 500
PESAN_PANJANG = "Ups, pesannya kepanjangan (maks 500 karakter). Bagi jadi 2x kirim ya."

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

def get_client_ip():
  # Di produksi ada Nginx di depan -> IP asli ada di X-Forwarded-For.
  # Tanpa ini semua audit kesimpen 127.0.0.1, useless buat deteksi spam.
  xff = request.headers.get("X-Forwarded-For", "")
  if xff:
    return xff.split(",")[0].strip()
  return request.remote_addr or ""

def catat_audit(user_id, ip, endpoint, user_text, hit, latency_ms, error=None, miss_reason=None):
  # Audit gagal JANGAN bikin chat gagal. Best-effort aja.
  try:
    insert_audit(user_id, ip, endpoint, user_text, hit, latency_ms, error, miss_reason)
  except Exception as e:
    print(f"[AUDIT ERROR] {e}")

# Tag akhir jawaban Mimin (konvensi prompt.py 2b): [OK]/[OOT]/[GATAU]/[CHIT].
# [OK] = materi terjawab (bukan miss). Sisanya = miss gabungan.
# Tag DICOPOT sebelum ke user/storage biar chat tetap bersih profesional.
_TAG_RE = re.compile(r"\[(OK|OOT|GATAU|CHIT)\]\s*$")
_TAG_MISS = {"OOT": "oot", "GATAU": "gatau", "CHIT": "chit"}

def petik_tag(reply):
  if not reply:
    return reply, None
  m = _TAG_RE.search(reply.strip())
  if not m:
    return reply, None
  bersih = _TAG_RE.sub("", reply.strip()).strip()
  return bersih, _TAG_MISS.get(m.group(1))

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
  ip = get_client_ip()
  if len(message) > MAX_PESAN:
    catat_audit(user_id, ip, "chat", message[:MAX_PESAN], 0, 0, "too_long")
    return jsonify({
      "error": PESAN_PANJANG
    }), 413
  start = time.time()
  reply, hit, err = get_reply(message, history)
  latency_ms = int((time.time() - start) * 1000)
  reply, miss_reason = petik_tag(reply)
  tambah_message(user_id, "User", message)
  tambah_message(user_id, "AI", sanitize_markdown(reply))
  catat_audit(user_id, ip, "chat", message, hit, latency_ms, err, miss_reason)

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
  ip = get_client_ip()
  if len(message) > MAX_PESAN:
    catat_audit(user_id, ip, "stream", message[:MAX_PESAN], 0, 0, "too_long")
    def too_long():
      yield f"data: {json.dumps({'error': PESAN_PANJANG}, ensure_ascii=False)}\n\n"
    return Response(stream_with_context(too_long()), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
  start = time.time()
  system_p, prompt, err, hit = build_rag_prompt(message, history)
  if err == "embedding_error":
    catat_audit(user_id, ip, "stream", message, 0, int((time.time() - start) * 1000), err)
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
      full, miss_reason = petik_tag(full)
      tambah_message(user_id, "AI", sanitize_markdown(full))
      catat_audit(user_id, ip, "stream", message, hit, int((time.time() - start) * 1000), None, miss_reason)
      yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
    except Exception as e:
      print(f"[STREAM ERROR] {e}")
      full, miss_reason = petik_tag(full)
      if full:
        tambah_message(user_id, "AI", sanitize_markdown(full))
      catat_audit(user_id, ip, "stream", message, hit, int((time.time() - start) * 1000), "stream_error", miss_reason)
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