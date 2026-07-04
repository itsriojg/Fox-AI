from flask import Flask, render_template, request
from chatbot import get_reply
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])

def home():
  message = request.form.get("pesan", "")
  reply = get_reply(message)
  return render_template("index.html", nama="RIO", balasan=reply)

app.run()

