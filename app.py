from flask import Flask, render_template_string
import feedparser
import re
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

FEED_URL = "https://www.romeoville.org/Calendar.aspx?RSS=1&CID=14"
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
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            width: 90%;
            max-width: 800px;
            height: 100%;
            overflow: hidden;
            text-align: center;
            position: relative;
        }
        .scrolling-wrapper {
            display: flex;
            flex-direction: column;
            animation: scrollUp 60s linear infinite;
        }
        @keyframes scrollUp {
            0% { transform: translateY(0); }
            100% { transform: translateY(-50%); }
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
        <div class=\"scrolling-wrapper\">
            {% for event in events %}
            <div class=\"event\">{{ event }}</div>
            {% endfor %}
            {% for event in events %}
            <div class=\"event\">{{ event }}</div>
            {% endfor %}
        </div>
        {% else %}
        <p>No upcoming events found.</p>
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
        match = re.search(r"Event date[s]?:\\s*(.+?)<", entry.description)
        if match:
            date_str = match.group(1).split("<")[0].strip()
            try:
                # Parse date (single date or date range)
                if "-" in date_str:
                    start_str, _ = date_str.split("-")
                    event_date = datetime.strptime(start_str.strip(), "%B %d, %Y")
                else:
                    event_date = datetime.strptime(date_str, "%B %d, %Y")

                event_date = pytz.timezone("America/Chicago").localize(event_date)
                if event_date >= now:
                    upcoming_events.append(entry.title)
            except Exception as e:
                print(f"Error parsing date from entry '{entry.title}': {e}")

    return render_template_string(TEMPLATE, events=upcoming_events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
