import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect 
from chatbot import get_reply
from history import tambah_message, ambil_history, hapus_history
from database import build_database
from knowledge import brain_knowledge

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
build_database()
@app.route("/", methods=["GET", "POST"])

def home():
  if request.method == "POST":
    message = request.form.get("pesan", "")
    if message != "":
      reply = get_reply(message)
      tambah_message("Rio", message)
      tambah_message("AI", reply)
      return redirect("/")
  return render_template("index.html", nama="RIO", riwayat_chat=ambil_history())

@app.route("/clear", methods=["POST"])

def clear_history():
  hapus_history()
  return redirect("/")

app.run()

