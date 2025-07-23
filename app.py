from flask import Flask, render_template_string
import feedparser
import re
from datetime import datetime
import pytz

app = Flask(__name__)

FEED_URL = "https://www.romeoville.org/Calendar.aspx?RSS=1&CID=14"

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
            text-align: center;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 90%;
            max-width: 800px;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            position: relative;
        }
        .scrolling {
            display: inline-block;
            animation: scrollUp 40s linear infinite;
        }
        @keyframes scrollUp {
            0%   { transform: translateY(100%); }
            100% { transform: translateY(-100%); }
        }
        .event {
            font-size: 2em;
            margin: 1.5em 0;
        }
    </style>
</head>
<body>
    <div class="container">
        {% if events %}
        <div class="scrolling">
            {% for event in events %}
            <div class="event">{{ event }}</div>
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
        description = entry.get("description", "")
        match = re.search(r"Event date[s]?:\s*([A-Za-z]+\s\d{1,2},\s\d{4})", description)
        if match:
            try:
                event_date = datetime.strptime(match.group(1), "%B %d, %Y")
                event_date = pytz.timezone("America/Chicago").localize(event_date)
                if event_date.date() >= now.date():
                    upcoming_events.append(entry.title)
            except Exception as e:
                print(f"Skipping event due to date parsing issue: {e}")

    return render_template_string(TEMPLATE, events=upcoming_events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
