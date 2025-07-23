from flask import Flask, render_template_string
import feedparser
from datetime import datetime
import pytz

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
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: #111;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        h1 {
            margin-top: 1rem;
            font-size: 2rem;
            text-align: center;
        }
        .scroll-container {
            height: 500px;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
        }
        .event-list {
            display: inline-block;
            animation: scrollUp 30s linear infinite;
        }
        .event {
            padding: 1rem;
            text-align: center;
            font-size: 1.2rem;
        }
        @keyframes scrollUp {
            0% { transform: translateY(100%); }
            100% { transform: translateY(-100%); }
        }

        @media (max-width: 600px) {
            .event {
                font-size: 1rem;
            }
        }
    </style>
</head>
<body>
    <h1>Upcoming Romeoville Events</h1>
    {% if events %}
    <div class="scroll-container">
        <div class="event-list">
            {% for event in events %}
            <div class="event">
                <strong>{{ event.date }}</strong><br>
                {{ event.title }}
            </div>
            {% endfor %}
        </div>
    </div>
    {% else %}
    <p>No upcoming events found.</p>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def home():
    feed = feedparser.parse(FEED_URL)
    events = []
    central = pytz.timezone("America/Chicago")
    today = datetime.now(central).date()

    for entry in feed.entries:
        description = entry.get("description", "")
        lines = description.splitlines()
        for line in lines:
            if "Event date" in line or "Event dates" in line:
                date_str = line.split(":", 1)[-1].strip().replace("<br>", "")
                date_parts = date_str.split(" - ")[0].strip()
                try:
                    event_date = datetime.strptime(date_parts, "%B %d, %Y").date()
                    if event_date >= today:
                        events.append({
                            "title": entry.title,
                            "date": event_date.strftime("%B %d, %Y")
                        })
                except ValueError:
                    continue

    events.sort(key=lambda e: datetime.strptime(e["date"], "%B %d, %Y"))
    return render_template_string(TEMPLATE, events=events)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
