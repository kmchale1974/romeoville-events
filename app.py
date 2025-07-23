from flask import Flask, render_template_string
import feedparser
import pytz
from datetime import datetime
from bs4 import BeautifulSoup
import re

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
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        .container {
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .scrolling-events {
            height: 80%;
            overflow: hidden;
            text-align: center;
            position: relative;
        }
        .scrolling-events ul {
            list-style: none;
            padding: 0;
            margin: 0;
            animation: scrollUp 60s linear infinite;
        }
        .scrolling-events li {
            font-size: 2em;
            padding: 1em 0;
        }
        @keyframes scrollUp {
            0%   { transform: translateY(100%); }
            100% { transform: translateY(-100%); }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if events %}
        <div class="scrolling-events">
            <ul>
                {% for event in events %}
                    <li>{{ event }}</li>
                {% endfor %}
                {% for event in events %}
                    <li>{{ event }}</li>
                {% endfor %}
            </ul>
        </div>
        {% else %}
        <p>No upcoming events found.</p>
        {% endif %}
    </div>
</body>
</html>
"""

def extract_event_date(description):
    """Extract event date using regex."""
    soup = BeautifulSoup(description, "html.parser")
    text = soup.get_text()
    match = re.search(r"Event date[s]?:\s*(.+)", text)
    if match:
        return match.group(1).strip()
    return None

@app.route("/")
def index():
    feed = feedparser.parse(FEED_URL)
    now = datetime.now(pytz.timezone("America/Chicago"))
    upcoming_events = []

    for entry in feed.entries:
        raw_date = extract_event_date(entry.description)
        if raw_date:
            try:
                if "-" in raw_date:
                    start_str = raw_date.split("-")[0].strip()
                else:
                    start_str = raw_date.strip()

                event_date = datetime.strptime(start_str, "%B %d, %Y")
                event_date = pytz.timezone("America/Chicago").localize(event_date)

                if event_date.date() >= now.date():
                    upcoming_events.append(entry.title)
            except Exception as e:
                print(f"Error parsing '{entry.title}': {e}")

    return render_template_string(TEMPLATE, events=upcoming_events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
