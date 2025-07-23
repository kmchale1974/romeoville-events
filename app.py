from flask import Flask, render_template_string
import feedparser
from datetime import datetime, timedelta
import pytz

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

from bs4 import BeautifulSoup
import re

@app.route("/")
def index():
    feed = feedparser.parse(FEED_URL)
    now = datetime.now(pytz.timezone("America/Chicago"))
    upcoming_events = []

    for entry in feed.entries:
        try:
            soup = BeautifulSoup(entry.description, "html.parser")
            text = soup.get_text(separator="\n")  # Keep line breaks for parsing

            # Extract date
            date_match = re.search(r'Event date:\s*([A-Za-z]+ \d{1,2}, \d{4})', text)
            if not date_match:
                continue

            event_date_str = date_match.group(1)
            event_date = datetime.strptime(event_date_str, "%B %d, %Y")
            event_date = pytz.timezone("America/Chicago").localize(event_date)

            if event_date >= now:
                # Extract time and location
                time_match = re.search(r'Time:\s*(.*)', text)
                location_match = re.search(r'Location:\s*(.*)', text)

                time_str = time_match.group(1).strip() if time_match else "Time not listed"
                location_str = location_match.group(1).strip() if location_match else "Location not listed"

                display_text = f"{entry.title} – {event_date_str} @ {time_str} ({location_str})"
                upcoming_events.append(display_text)

        except Exception as e:
            print(f"Error parsing entry: {e}")

    return render_template_string(TEMPLATE, events=upcoming_events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
