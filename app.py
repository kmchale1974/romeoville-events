from flask import Flask, render_template_string
import feedparser
from datetime import datetime
import pytz
import os
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

FEED_URL = "https://www.romeoville.org/Calendar.aspx?RSS=true"
CENTRAL = pytz.timezone("America/Chicago")

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Romeoville Events</title>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: black;
            color: white;
            text-align: center;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        .container {
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .events {
            animation: scroll 60s linear infinite;
            display: inline-block;
        }
        .event {
            font-size: 2em;
            margin: 1em 0;
        }
        @keyframes scroll {
            0% { transform: translateY(100%); }
            100% { transform: translateY(-100%); }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if events %}
        <div class="events">
            {% for event in events %}
                <div class="event">{{ event['title'] }}</div>
            {% endfor %}
        </div>
        {% else %}
            <div class="event">No upcoming events found</div>
        {% endif %}
    </div>
</body>
</html>
"""

def extract_event_date(description):
    soup = BeautifulSoup(description, "html.parser")
    text = soup.get_text()

    match = re.search(r"Event date[s]*:?\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})", text)
    if match:
        try:
            return datetime.strptime(match.group(1), "%B %d, %Y")
        except ValueError:
            pass
    return None

@app.route("/")
def index():
    feed = feedparser.parse(FEED_URL)
    today = datetime.now(CENTRAL).date()
    events = []

    for entry in feed.entries:
        event_date = extract_event_date(entry.description)
        if event_date and event_date.date() >= today:
            events.append({
                "title": entry.title,
                "link": entry.link
            })

    events.sort(key=lambda e: extract_event_date(feed.entries[[entry.title for entry in feed.entries].index(e["title"])].description))

    return render_template_string(TEMPLATE, events=events)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
