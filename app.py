import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, jsonify, send_from_directory
from chatbot import get_reply
from history import tambah_message, ambil_history, hapus_history
from database import build_table_history, build_table_knowledge, knowledge_exists
from rag import build_knowledge

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
build_table_history()
build_table_knowledge()
if not knowledge_exists():
  try:
    build_knowledge()
  except Exception as e:
    print(f"[ERROR] Gagal membangun knowledge: {e}")

@app.route("/")
def home():
  return send_from_directory("home-react/dist", "index.html")

@app.route("/react-assets/<path:filename>")
def react_assets(filename):
    return send_from_directory("home-react/dist", filename)
  
@app.route("/chatbot")
def chatbot():
  return render_template(
    "chatbot.html",
    nama="RIO",
    riwayat_chat=ambil_history()
  )

@app.route("/api/chat", methods=["POST"])
def api_chat():
  message = request.form.get("pesan", "")
  if message == "":
    return jsonify({
      "error": "Pesan kosong"
    })
  history = ambil_history()
  reply = get_reply(message, history)
  tambah_message("Rio", message)
  tambah_message("AI", reply)

  return jsonify({
    "reply": reply
  })

@app.route("/clear", methods=["POST"])
def clear_history():
  hapus_history()
  return redirect("/chatbot")

if __name__ == "__main__":
  app.run(
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "5000"))
  )