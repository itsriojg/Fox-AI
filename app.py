import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect 
from chatbot import get_reply
from history import tambah_message, ambil_history, hapus_history
from database import build_table_history, build_table_knowledge, knowledge_exists
from rag import build_knowledge

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
build_table_history()
build_table_knowledge()
if not knowledge_exists():
  build_knowledge()

@app.route("/")
def home():
  return render_template("home.html")


@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
  if request.method == "POST":
    message = request.form.get("pesan", "")
    if message != "":
      history = ambil_history()
      reply = get_reply(message, history)
      tambah_message("Rio", message)
      tambah_message("AI", reply)
      return redirect("/chatbot")
    else:
      return redirect("/chatbot")
  return render_template("chatbot.html", nama="RIO", riwayat_chat=ambil_history())


@app.route("/clear", methods=["POST"])
def clear_history():
  hapus_history()
  return redirect("/chatbot")

app.run()