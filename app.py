from flask import Flask, render_template_string
import feedparser
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup

app = Flask(__name__)

FEED_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=58&CID=All-calendar.xml"
TEMPLATE = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
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
    <div class=\"container\">
        {% if events %}
        <div class=\"scroll\">
            {% for event in events %}
            <div class=\"event {% if loop.index0 % 2 == 0 %}even{% endif %}\">
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
            # Parse date from title or description
            description = entry.get("description", "")
            soup = BeautifulSoup(description, "html.parser")
            text = soup.get_text()

            event_date = None
            if "Event date:" in text:
                parts = text.split("Event date:")[1].split("\n")[0].strip()
                if " - " in parts:
                    parts = parts.split(" - ")[0]
                event_date = datetime.strptime(parts, "%B %d, %Y")
                event_date = pytz.timezone("America/Chicago").localize(event_date)

            if event_date and event_date >= now:
                event_info = f"{entry.title} — {parts}"
                upcoming_events.append(event_info)
        except Exception as e:
            print(f"Error parsing entry '{entry}': {e}")

    return render_template_string(TEMPLATE, events=upcoming_events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
