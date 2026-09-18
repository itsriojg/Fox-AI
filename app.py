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
  # Return (uid, bad_uid). Frontend Vue kirim user_id sendiri (localStorage)
  # biar lolos beda origin, via JSON atau form. Fallback ke session cookie
  # buat web Flask lama. bad_uid=True kalau body ngirim user_id tapi formatnya
  # invalid (M3 pentest 2026-09-17) — pemanggil catat ke audit biar kelihatan
  # di pantau, tapi request TETAP jalan (nol breakage: tanpa 400).
  data = request.get_json(silent=True) or {}
  raw = data.get("user_id") or request.form.get("user_id", "")
  if isinstance(raw, str) and raw != "":
    if _UID_WEB_RE.match(raw):
      return raw, False
    if "user_id" not in session:
      session["user_id"] = secrets.token_hex(16)
    return session["user_id"], True
  if "user_id" not in session:
    session["user_id"] = secrets.token_hex(16)
  return session["user_id"], False

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
# Pola kuat: model kadang kasih newline/case beda setelah tag.
_TAG_RE = re.compile(r"\[+(OK|OOT|GATAU|CHIT)\]+[ \t]*(?:\n|\s*$)", re.IGNORECASE)
_TAG_TAIL_RE = re.compile(r"[ \t]+\[(OK|OOT|GATAU|CHIT)?[A-Z]*\]?[ \t]*$", re.IGNORECASE)
# Tag halu (model kadang ngarang [MINTIF]/[INFO]/dsb): ikut dicopot dari
# tampilan biar user ga liat, tapi audit = miss (None) biar ketauan di pantau.
_TAG_HALU_RE = re.compile(r"\[+[A-Z]{2,}\]+[ \t]*(?:\n|\s*$)", re.IGNORECASE)
_TAG_MISS = {"OOT": "oot", "GATAU": "gatau", "CHIT": "chit"}

def petik_tag(reply):
  if not reply:
    return reply, None
  s = reply.strip()
  m = _TAG_RE.search(s)
  if m:
    tag = m.group(1).upper()
    bersih = _TAG_RE.sub("", s).strip()
    bersih = _TAG_TAIL_RE.sub("", bersih).strip()
    return bersih, _TAG_MISS.get(tag)
  # sisa "[" nyangkut (stream kepotong tengah tag) — buang biar bersih
  bersih = _TAG_TAIL_RE.sub("", s).strip()
  # tag halu di ekor? copot dari tampilan, audit tetap miss
  if _TAG_HALU_RE.search(bersih):
    bersih = _TAG_HALU_RE.sub("", bersih).strip()
  return bersih, None

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
    riwayat_chat=ambil_history(get_user_id()[0])
  )

@app.route("/api/chat", methods=["POST"])
@limiter.limit("15 per minute; 200 per hour")
def api_chat():
  message = ambil_pesan()
  if message == "":
    return jsonify({
      "error": "Pesan kosong"
    })
  user_id, bad_uid = get_user_id()
  history = ambil_history(user_id, limit=6, max_chars=180)
  ip = get_client_ip()
  if len(message) > MAX_PESAN:
    catat_audit(user_id, ip, "chat", message[:MAX_PESAN], 0, 0, "too_long" if not bad_uid else "bad_uid")
    return jsonify({
      "error": PESAN_PANJANG
    }), 413
  start = time.time()
  reply, hit, err = get_reply(message, history)
  latency_ms = int((time.time() - start) * 1000)
  reply, miss_reason = petik_tag(reply)
  tambah_message(user_id, "User", message)
  tambah_message(user_id, "AI", sanitize_markdown(reply))
  catat_audit(user_id, ip, "chat", message, hit, latency_ms, err or ("bad_uid" if bad_uid else None), miss_reason)

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
  user_id, bad_uid = get_user_id()
  history = ambil_history(user_id, limit=6, max_chars=180)
  ip = get_client_ip()
  if len(message) > MAX_PESAN:
    catat_audit(user_id, ip, "stream", message[:MAX_PESAN], 0, 0, "too_long" if not bad_uid else "bad_uid")
    def too_long():
      yield f"data: {json.dumps({'error': PESAN_PANJANG}, ensure_ascii=False)}\n\n"
    return Response(stream_with_context(too_long()), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
  start = time.time()
  system_p, prompt, err, hit = build_rag_prompt(message, history)
  if err == "embedding_error":
    catat_audit(user_id, ip, "stream", message, 0, int((time.time() - start) * 1000), err if not bad_uid else "bad_uid")
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
      # Model reasoning bisa balikin KOSONG kalau thinking makan habis budget
      # (finish:length, diukur 2026-09-17 di DeepSeek V4 Flash). Jangan simpan
      # bubble kosong: kasih fallback hangat + audit 'empty_reply' biar pantau.
      if not full.strip():
        full = "Waduh, mimin blank sebentar. Coba kirim ulang pertanyaannya ya."
        catat_audit(user_id, ip, "stream", message, hit, int((time.time() - start) * 1000), "empty_reply" if not bad_uid else "bad_uid", miss_reason)
        yield f"data: {json.dumps({'token': full}, ensure_ascii=False)}\n\n"
        tambah_message(user_id, "AI", sanitize_markdown(full))
        yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
        return
      full, miss_reason = petik_tag(full)
      tambah_message(user_id, "AI", sanitize_markdown(full))
      catat_audit(user_id, ip, "stream", message, hit, int((time.time() - start) * 1000), "bad_uid" if bad_uid else None, miss_reason)
      yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
    except Exception as e:
      print(f"[STREAM ERROR] {e}")
      full, miss_reason = petik_tag(full)
      if full:
        tambah_message(user_id, "AI", sanitize_markdown(full))
      catat_audit(user_id, ip, "stream", message, hit, int((time.time() - start) * 1000), "stream_error" if not bad_uid else "bad_uid", miss_reason)
      yield f"data: {json.dumps({'error': 'Maaf, server sedang mengalami kendala. Silakan coba lagi.'}, ensure_ascii=False)}\n\n"
  return Response(stream_with_context(generate()), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Content-Type": "text/event-stream"})

@app.route("/clear", methods=["POST"])
@limiter.limit("5 per minute")
def clear_history():
  # H2 pentest 2026-09-17: /clear percaya user_id body apa adanya. Versi aman
  # tanpa breakage: user_id body WAJIB lolos regex (M3), kalau invalid/zonk
  # pakai session cookie (web Flask same-origin tetap jalan, Vue kirim UID
  # valid tetap jalan). Limit 5/menit biar abuse hapus-chat orang mahal.
  data = request.get_json(silent=True) or {}
  raw = data.get("user_id") or request.form.get("user_id", "")
  if isinstance(raw, str) and raw != "" and _UID_WEB_RE.match(raw):
    uid = raw
  else:
    if "user_id" not in session:
      session["user_id"] = secrets.token_hex(16)
    uid = session["user_id"]
  hapus_history(uid)
  return redirect("/chatbot")

if __name__ == "__main__":
  app.run(
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "5000"))
  )