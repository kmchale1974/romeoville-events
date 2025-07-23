from flask import Flask, render_template_string
import feedparser
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

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
    <div class="container">
        {% if events %}
        <div class="scroll">
            {% for event in events %}
            <div class="event {% if loop.index0 % 2 == 0 %}even{% endif %}">
                <strong>{{ event.title }}</strong><br/>
                {{ event.date }}<br/>
                {{ event.time }}<br/>
                {{ event.location }}
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
            soup = BeautifulSoup(entry.get("description", ""), "html.parser")
            text = soup.get_text(separator="\n")

            # Extract date, time, location
            date = time = location = None
            for line in text.splitlines():
                if "Event date:" in line:
                    date = line.replace("Event date:", "").strip()
                elif "Event Time:" in line:
                    time = line.replace("Event Time:", "").strip()
                elif "Location:" in line:
                    location = line.replace("Location:", "").strip()
                elif location and line.strip():  # get additional lines after Location:
                    location += ", " + line.strip()

            # Check if date is valid and upcoming
            if date:
                event_date = datetime.strptime(date, "%B %d, %Y")
                event_date = pytz.timezone("America/Chicago").localize(event_date)
                if event_date >= now:
                    upcoming_events.append({
                        "title": entry.title,
                        "date": event_date.strftime("%B %d, %Y"),
                        "time": time or "",
                        "location": location or ""
                    })
        except Exception as e:
            print(f"Error parsing entry '{entry}': {e}")

    return render_template_string(TEMPLATE, events=upcoming_events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
