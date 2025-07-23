from flask import Flask, render_template_string
import requests
import feedparser
from datetime import datetime
import pytz

app = Flask(__name__)

FEED_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=58&CID=All-calendar.xml"
TIMEZONE = pytz.timezone("America/Chicago")

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Romeoville Upcoming Events</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f2f2f2;
            color: #333;
            padding: 30px;
            text-align: center;
        }
        h1 {
            color: #002855;
            margin-bottom: 30px;
        }
        .event {
            background: white;
            margin: 15px auto;
            padding: 20px;
            border-radius: 12px;
            max-width: 600px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        }
        .event h2 {
            margin: 0;
            color: #0066cc;
        }
        .event p {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <h1>Romeoville Upcoming Events</h1>
    {% if events %}
        {% for event in events %}
            <div class="event">
                <h2>{{ event.title }}</h2>
                <p><strong>{{ event.date }}</strong></p>
                <p>{{ event.description }}</p>
            </div>
        {% endfor %}
    {% else %}
        <p>No upcoming events found.</p>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    feed = feedparser.parse(FEED_URL)
    events = []

    for entry in feed.entries:
        try:
            # Attempt to parse the published date
            event_time = datetime(*entry.published_parsed[:6])
            event_time = pytz.utc.localize(event_time).astimezone(TIMEZONE)
        except Exception:
            continue

        if event_time >= datetime.now(TIMEZONE):
            events.append({
                "title": entry.title,
                "description": entry.description.strip(),
                "date": event_time.strftime("%A, %B %d, %Y at %I:%M %p")
            })

    # Sort events by date
    events.sort(key=lambda e: datetime.strptime(e['date'], "%A, %B %d, %Y at %I:%M %p"))

    return render_template_string(TEMPLATE, events=events)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

