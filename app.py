from flask import Flask, render_template, request

app = Flask(__name__)
responses = {
      "halo" : "Halo juga:)",
      "kamu siapa" : "Saya project pillow-fox",
      "bisa bantu saya?" : "Tentu saja, apa yang bisa saya bantu?",
      "selamat pagi" : "Selamat pagi",
      "" : ""
    }
@app.route("/", methods=["GET", "POST"])
def home():
    message = request.form.get("pesan", "")
    message = message.strip().lower()
    reply = responses.get(message, "Maaf saya tidak mengerti")
    return render_template("index.html", nama="Rio", pesan=message, balasan=reply)

app.run()
