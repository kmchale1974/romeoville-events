from flask import Flask, render_template_string
import feedparser
from datetime import datetime
import pytz

app = Flask(__name__)

FEED_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=58&CID=All-calendar.xml"

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Romeoville Upcoming Events</title>
    <meta charset="utf-8">
    <style>
        body {
            background-color: #00274D;
            font-family: Arial, sans-serif;
            color: white;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        h1 {
            text-align: center;
            font-size: 2.5em;
            margin: 20px 0;
        }
        .marquee {
            height: 100vh;
            overflow: hidden;
            position: relative;
        }
        .marquee-content {
            display: flex;
            flex-direction: column;
            animation: scroll-up 20s linear infinite;
            width: 100%;
            align-items: center;
        }
        .event {
            width: 80%;
            margin: 20px auto;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            text-align: center;
        }
        .event h2 {
            font-size: 1.8em;
            margin: 0 0 10px;
        }
        .event p {
            font-size: 1.2em;
            margin: 0;
        }
        @keyframes scroll-up {
            0% {
                transform: translateY(100%);
            }
            100% {
                transform: translateY(-100%);
            }
        }
    </style>
</head>
<body>
    <h1>Romeoville Upcoming Events</h1>
    <div class="marquee">
        <div class="marquee-content">
            {% if events %}
                {% for event in events %}
                    <div class="event">
                        <h2>{{ event.title }}</h2>
                        <p>{{ event.date }}</p>
                    </div>
                {% endfor %}
            {% else %}
                <div class="event">
                    <h2>No upcoming events found</h2>
                </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

def parse_date(entry):
    # Try extracting date from entry.updated or entry.published
    date_str = entry.get('updated', '') or entry.get('published', '')
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
        except Exception:
            return None

@app.route('/')
def index():
    feed = feedparser.parse(FEED_URL)
    now = datetime.now(pytz.timezone('US/Central'))

    upcoming_events = []
    for entry in feed.entries:
        date = parse_date(entry)
        if date and date >= now:
            upcoming_events.append({
                "title": entry.title,
                "date": date.strftime("%A, %B %d, %Y at %I:%M %p")
            })

    upcoming_events.sort(key=lambda x: datetime.strptime(x["date"], "%A, %B %d, %Y at %I:%M %p"))
    return render_template_string(TEMPLATE, events=upcoming_events)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
