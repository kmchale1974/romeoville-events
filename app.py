from flask import Flask, Response
import fetch_events

app = Flask(__name__)

@app.route("/")
def index():
    html = fetch_events.build_html()
    return Response(html, mimetype="text/html")