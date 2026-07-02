from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    message = request.args.get("message", "")
    return render_template("index.html", nama="Rio", message=message)

app.run()
