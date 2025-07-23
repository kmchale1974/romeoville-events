from flask import Flask, render_template_string
import feedparser
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

app = Flask(__name__)

FEED_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=58&CID=All-calendar.xml"
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Romeoville Events</title>
    <style>
        body {
            background-color: #f4f4f4;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            width: 90%;
            max-width: 800px;
            text-align: center;
            overflow: hidden;
            position: relative;
        }
        .scroll {
            display: inline-block;
            animation: scrollUp 90s linear infinite;
        }
        @keyframes scrollUp {
            0%   { transform: translateY(100%); }
            100% { transform: translateY(-100%); }
        }
        .event {
            margin: 2em 0;
            font-size: 1.2em;
            padding: 1em;
        }
        .even {
            background-color: #e6f0ff;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        {% if events %}
        <div class="scroll">
            {% for event in events %}
            <div class="event {% if loop.index0 % 2 == 0 %}even{% endif %}">
                {{ event }}
            </div>
            {% endfor %}
        </div>
        {% else %}
        <p>No upcoming events found</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    feed = feedparser.parse(FEED_URL)
    now = datetime.now(pytz.timezone("America/Chicago"))
    upcoming_events = []

    for entry in feed.entries:
        try:
            description = entry.get("description", "")
            soup = BeautifulSoup(description, "html.parser")
            text = soup.get_text()

            event_date = None
            if "Event date:" in text:
                parts = text.split("Event date:")[1].strip()
                date_only = parts.split("Event Time")[0].strip()
                date_only = date_only.split("\n")[0].split("  ")[0].strip()
                event_date = datetime.strptime(date_only, "%B %d, %Y")
                event_date = pytz.timezone("America/Chicago").localize(event_date)

            if event_date and event_date >= now:
                event_info = f"{entry.title} — {event_date.strftime('%B %d, %Y')}"
                upcoming_events.append(event_info)
        except Exception as e:
            print(f"Error parsing entry '{entry}': {e}")

    return render_template_string(TEMPLATE, events=upcoming_events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
