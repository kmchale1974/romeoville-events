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

def parse_event_date(summary):
    date_match = re.search(r"Event date[s]*: (.*?)\n", summary)
    time_match = re.search(r"Event Time: (.*?)\n", summary)
    location_match = re.search(r"Location:\s*(.*?)\s*Romeoville", summary, re.DOTALL)
    
    date_str = date_match.group(1).strip() if date_match else ''
    time_str = time_match.group(1).strip() if time_match else ''
    location_str = location_match.group(1).strip().replace("\n", ", ") + ", Romeoville, IL" if location_match else "Romeoville, IL"
    
    return date_str, time_str, location_str

def is_future_event(date_str):
    today = datetime.now().date()
    try:
        if " - " in date_str:
            end_str = date_str.split(" - ")[1].strip()
            event_date = datetime.strptime(end_str, "%B %d, %Y").date()
        else:
            event_date = datetime.strptime(date_str.strip(), "%B %d, %Y").date()
        return event_date >= today
    except Exception as e:
        print(f"[SKIP] Failed to parse date '{date_str}': {e}")
        return False

@app.route("/")
def show_events():
    feed = feedparser.parse(FEED_URL)
    events = []

    for entry in feed.entries:
    date_str, time_str, location_str = parse_event_date(entry.summary)
    print(f"[PARSE] Title: {entry.title} | Date: {date_str}")
    if is_future_event(date_str):
        events.append({
            "title": entry.title,
            "link": entry.link,
            "date": date_str,
            "time": time_str,
            "location": location_str
        })
    else:
        print(f"[SKIP] {entry.title} excluded: '{date_str}' is in the past")

    events = sorted(events, key=lambda e: datetime.strptime(e["date"].split(" - ")[0], "%B %d, %Y"))
    return render_template_string(TEMPLATE, events=events)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
