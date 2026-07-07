from flask import Flask, render_template, request
from chatbot import get_reply
from history import history, tambah_message
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])

def home():
  reply = ""
  if request.method == "POST":
    message = request.form.get("pesan", "")
    if message != "":
      reply = get_reply(message)
      tambah_message("Rio", message)
      tambah_message("AI", reply)
  return render_template("index.html", nama="RIO", riwayat_chat=history)

app.run()

