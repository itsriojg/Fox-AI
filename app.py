import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect 
from chatbot import get_reply
from history import tambah_message, ambil_history, hapus_history
from database import build_database
from rag import brain_knowledge, pilih_pdf

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
build_database()
@app.route("/", methods=["GET", "POST"])

def home():
  if request.method == "POST":
    message = request.form.get("pesan", "")
    if message != "":
      files = pilih_pdf(message)
      if files == []:
        knowledge = ""
      else:
        knowledge = brain_knowledge(message)
      history = ambil_history()
      reply = get_reply(message, knowledge, history)
      tambah_message("Rio", message)
      tambah_message("AI", reply)
      print(len(knowledge))
      print(len(history))
      return redirect("/")
    else:
      return redirect("/")
  return render_template("index.html", nama="RIO", riwayat_chat=ambil_history())

@app.route("/clear", methods=["POST"])

def clear_history():
  hapus_history()
  return redirect("/")

app.run()

