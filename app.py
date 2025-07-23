from flask import Flask, render_template_string
import feedparser
from datetime import datetime
import pytz
import re

app = Flask(__name__)

RSS_FEED_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=58&CID=All-calendar.xml"

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Romeoville Upcoming Events</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 90%;
            max-width: 800px;
            margin: 2em auto;
            background: white;
            padding: 1em 2em;
            border-radius: 8px;
            box-shadow: 0 0 10px #ccc;
        }
        h1 {
            text-align: center;
            color: #00467f;
        }
        .event {
            border-bottom: 1px solid #ccc;
            padding: 1em 0;
        }
        .event:last-child {
            border-bottom: none;
        }
        .event h2 {
            margin: 0 0 0.3em;
            font-size: 1.2em;
            color: #00467f;
        }
        .event .date {
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Romeoville Upcoming Events</h1>
        {% if events %}
            {% for event in events %}
                <div class="event">
                    <h2><a href="{{ event.link }}" target="_blank">{{ event.title }}</a></h2>
                    <p class="date">{{ event.date }}</p>
                </div>
            {% endfor %}
        {% else %}
            <p>No upcoming events found.</p>
        {% endif %}
    </div>
</body>
</html>
"""

def parse_event_date(summary):
    try:
        match = re.search(r"Date:\s*(.+?)<br", summary)
        if not match:
            return None
        date_text = match.group(1).strip()
        parts = date_text.split(" - ")

        start_str = parts[0].strip()
        start_date = datetime.strptime(start_str, "%B %d, %Y")

        return start_date
    except Exception as e:
        print(f"[Date Parse Error] {e} in summary: {summary}")
        return None

def is_future_date(date_obj):
    chicago_tz = pytz.timezone("America/Chicago")
    now = datetime.now(chicago_tz)
    return date_obj.replace(tzinfo=chicago_tz) >= now

@app.route("/")
def show_events():
    feed = feedparser.parse(RSS_FEED_URL)
    events = []

    for entry in feed.entries:
        summary = entry.summary or ""
        start_date = parse_event_date(summary)
        if not start_date:
            continue
        if is_future_date(start_date):
            events.append({
                "title": entry.title,
                "link": entry.link,
                "date": start_date.strftime("%B %d, %Y")
            })

    return render_template_string(TEMPLATE, events=events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
