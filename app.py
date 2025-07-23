from flask import Flask, render_template_string
import feedparser
import re
from datetime import datetime

app = Flask(__name__)

FEED_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=58&CID=All-calendar.xml"

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Romeoville Events</title>
    <meta http-equiv="refresh" content="600">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            color: #222;
            padding: 20px;
            font-size: 1.2em;
        }
        .event {
            background: white;
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 0px 8px rgba(0,0,0,0.1);
        }
        .title {
            font-weight: bold;
            font-size: 1.4em;
            margin-bottom: 5px;
        }
        .time, .location {
            margin-top: 5px;
            font-size: 0.95em;
            color: #555;
        }
    </style>
</head>
<body>
    {% if events %}
        {% for event in events %}
            <div class="event">
                <div class="title">{{ event.title }}</div>
                <div class="time">{{ event.date }} | {{ event.time }}</div>
                <div class="location">{{ event.location }}</div>
            </div>
        {% endfor %}
    {% else %}
        <p>No upcoming events found.</p>
    {% endif %}
</body>
</html>
"""

import re

def parse_event_date(summary):
    # Extract the event date line from the summary
    match = re.search(r'Event date[s]*: (.+?)(?:<br|\\n|$)', summary)
    if not match:
        return None, None, None

    date_part = match.group(1).strip()

    # Example: "July 21, 2025 - July 25, 2025"
    if " - " in date_part:
        start_date_str, end_date_str = [d.strip() for d in date_part.split(" - ")]
    else:
        start_date_str = date_part.strip()
        end_date_str = start_date_str

    return start_date_str, end_date_str

def is_future_event(date_str):
    today = datetime.now().date()
    try:
        event_date = datetime.strptime(date_str, "%B %d, %Y").date()
        return event_date >= today
    except Exception as e:
        print(f"[ERROR] Failed to parse date '{date_str}': {e}")
        return False


@app.route("/")
def show_events():
    feed = feedparser.parse(FEED_URL)
    events = []

    for entry in feed.entries:
    start_date_str, end_date_str = parse_event_date(entry.summary or "")
    if not start_date_str:
        print(f"[SKIP] Could not find event date in: {entry.title}")
        continue

    if is_future_event(start_date_str):
        events.append({
            "title": entry.title,
            "link": entry.link,
            "date": start_date_str,
            "time": "",  # Optional: extract from summary
            "location": ""  # Optional: extract from summary
        })
    else:
        print(f"[SKIP] Event '{entry.title}' has start date '{start_date_str}' in the past")


    events = sorted(events, key=lambda e: datetime.strptime(e["date"].split(" - ")[0], "%B %d, %Y"))
    return render_template_string(TEMPLATE, events=events)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
