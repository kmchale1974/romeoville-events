from flask import Flask, render_template_string
import feedparser
from datetime import datetime
import pytz
import re
import os

app = Flask(__name__)

RSS_FEED_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=58&CID=All-calendar.xml"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Romeoville Upcoming Events</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f6f6f6;
            margin: 0;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #003366;
        }
        .event {
            background-color: white;
            border-left: 5px solid #003366;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .event-title {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 5px;
            color: #003366;
        }
        .event-date, .event-time, .event-location {
            font-size: 14px;
            margin: 2px 0;
        }
    </style>
</head>
<body>
    <h1>Romeoville Upcoming Events</h1>
    {% if events %}
        {% for event in events %}
        <div class="event">
            <div class="event-title"><a href="{{ event.link }}" target="_blank">{{ event.title }}</a></div>
            <div class="event-date">{{ event.date }}</div>
            <div class="event-time">{{ event.time }}</div>
            <div class="event-location">{{ event.location }}</div>
        </div>
        {% endfor %}
    {% else %}
        <p style="text-align:center;">No upcoming events found.</p>
    {% endif %}
</body>
</html>
"""

def parse_event_date(summary):
    """Extract and return event date and time from summary string"""
    date_match = re.search(r"Event date[s]*: (.*?)\n", summary)
    time_match = re.search(r"Event Time: (.*?)\n", summary)
    date_str = date_match.group(1).strip() if date_match else ''
    time_str = time_match.group(1).strip() if time_match else ''
    return date_str, time_str

def is_future_event(date_str):
    """Return True if the event is today or in the future"""
    today = datetime.now().date()
    try:
        if " - " in date_str:
            start_date_str = date_str.split(" - ")[0].strip()
        else:
            start_date_str = date_str.strip()
        event_date = datetime.strptime(start_date_str, "%B %d, %Y").date()
        return event_date >= today
    except ValueError:
        return False

def extract_location(summary):
    """Extract location from summary if available"""
    location_match = re.search(r"Location:\s*(.*?)$", summary.strip(), re.MULTILINE | re.DOTALL)
    return location_match.group(1).strip().replace("\n", ", ") if location_match else ''

@app.route('/')
def show_events():
    feed = feedparser.parse(RSS_FEED_URL)
    events = []

    for entry in feed.entries:
        date_str, time_str = parse_event_date(entry.summary)
        if date_str and is_future_event(date_str):
            events.append({
                'title': entry.title,
                'link': entry.link,
                'date': date_str,
                'time': time_str,
                'location': extract_location(entry.summary)
            })

    return render_template_string(HTML_TEMPLATE, events=events)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
