from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    message = request.form.get("message", "")
    return render_template("index.html", nama="Rio", message=message)

app.run()
