from flask import Flask, render_template_string
import feedparser
from datetime import datetime
import pytz
import re

app = Flask(__name__)

FEED_URL = "https://www.romeoville.org/Calendar.aspx?feed=calendar"

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Romeoville Events</title>
    <style>
        body {
            background-color: #000;
            color: #fff;
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 40px;
        }
        .event-list {
            display: inline-block;
            text-align: left;
            animation: scroll-up 60s linear infinite;
        }
        .event {
            margin-bottom: 40px;
            font-size: 1.5em;
        }
        @keyframes scroll-up {
            0% { transform: translateY(100%); }
            100% { transform: translateY(-100%); }
        }
    </style>
</head>
<body>
    <h1>Upcoming Events in Romeoville</h1>
    {% if events %}
        <div class="event-list">
            {% for event in events %}
                <div class="event">{{ event['title'] }} — {{ event['date'].strftime('%A, %B %d, %Y') }}</div>
            {% endfor %}
        </div>
    {% else %}
        <p>No upcoming events found.</p>
    {% endif %}
</body>
</html>
"""

def extract_event_date(description):
    match = re.search(r'Event date[s]*:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})', description)
    if not match:
        match = re.search(r'Event date[s]*:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})\s*-\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})', description)
        if match:
            return datetime.strptime(match.group(1), "%B %d, %Y")
        return None
    return datetime.strptime(match.group(1), "%B %d, %Y")

@app.route('/')
def home():
    feed = feedparser.parse(FEED_URL)
    now = datetime.now()
    events = []

    for entry in feed.entries:
        event_date = extract_event_date(entry.get('summary', ''))
        if event_date and event_date >= now:
            events.append({
                'title': entry.title,
                'date': event_date
            })

    events.sort(key=lambda x: x['date'])
    return render_template_string(TEMPLATE, events=events)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
