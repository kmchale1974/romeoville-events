from flask import Flask, render_template_string
import feedparser
from bs4 import BeautifulSoup
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
            overflow: hidden;
            text-align: center;
        }
        .scrolling {
            display: inline-block;
            animation: scrollUp 30s linear infinite;
        }
        @keyframes scrollUp {
            0% { transform: translateY(100%); }
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
    <div class="container">
        {% if events %}
        <div class="scrolling">
            {% for event in events %}
            <div class="event">{{ event }}</div>
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
    parsed_events = []

    for entry in feed.entries:
        soup = BeautifulSoup(entry.description, "html.parser")
        strong_tags = soup.find_all("strong")
        for tag in strong_tags:
            if "Event date" in tag.text:
                text = tag.next_sibling
                if text:
                    date_str = text.strip().split(" - ")[0]
                    try:
                        event_date = datetime.strptime(date_str, "%B %d, %Y")
                        event_date = pytz.timezone("America/Chicago").localize(event_date)
                        if event_date >= now:
                            parsed_events.append(f"{event_date.strftime('%B %d, %Y')}: {entry.title}")
                    except Exception as e:
                        print(f"❌ Failed to parse '{entry.title}': {e}")
                break

    return render_template_string(TEMPLATE, events=parsed_events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
