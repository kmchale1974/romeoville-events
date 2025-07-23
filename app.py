from flask import Flask, render_template_string
import feedparser
from datetime import datetime
import pytz
import re

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
            font-size: 1.5em;
            font-weight: bold;
        }
        .event:nth-child(even) {
            background-color: #e6f0ff;
            padding: 1em;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class=\"container\">
        {% if events %}
        <div class=\"scroll\">
            {% for event in events %}
            <div class=\"event\">{{ event }}</div>
            {% endfor %}
        </div>
        {% else %}
        <p>No upcoming events found</p>
        {% endif %}
    </div>
</body>
</html>
"""

def extract_event_date(description):
    match = re.search(r'Event date: ([A-Za-z]+ \d{1,2}, \d{4}) from ([\d:APMapm\s]+) to ([\d:APMapm\s]+)', description)
    if match:
        date_str, start_time, end_time = match.groups()
        try:
            event_datetime = datetime.strptime(f"{date_str} {start_time.strip()}", "%B %d, %Y %I:%M %p")
            return event_datetime
        except Exception as e:
            print(f"Date parse error: {e}")
    return None

@app.route("/")
def index():
    feed = feedparser.parse(FEED_URL)
    now = datetime.now(pytz.timezone("America/Chicago"))
    upcoming_events = []

    for entry in feed.entries:
        if hasattr(entry, "description"):
            event_datetime = extract_event_date(entry.description)
            if event_datetime and event_datetime >= now:
                event_title = entry.title
                location = entry.get("location", "Location not specified")
                formatted = f"{event_title} – {event_datetime.strftime('%b %d, %Y at %I:%M %p')} – {location}"
                upcoming_events.append(formatted)

    return render_template_string(TEMPLATE, events=upcoming_events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
