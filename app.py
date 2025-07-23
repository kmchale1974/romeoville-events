from flask import Flask, render_template_string
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

app = Flask(__name__)

FEED_URL = "https://www.romeoville.org/Calendar.aspx?RSS=1&CID=14"

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Romeoville Events</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            background: #f4f4f4;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 2em;
            text-align: center;
        }
        .scroll-wrapper {
            overflow: hidden;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .scroll {
            display: inline-block;
            animation: scrollUp 20s linear infinite;
        }
        @keyframes scrollUp {
            0% { transform: translateY(100%); }
            100% { transform: translateY(-100%); }
        }
        .event {
            margin: 2em 0;
            font-size: 1.8em;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="scroll-wrapper">
        {% if events %}
        <div class="scroll">
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
    events = []

    for entry in feed.entries:
        soup = BeautifulSoup(entry.description, "html.parser")
        strong_tags = soup.find_all("strong")

        event_date = None
        for tag in strong_tags:
            if "Event date" in tag.text:
                text = tag.next_sibling
                if text:
                    date_str = text.strip().split(" - ")[0]
                    try:
                        dt = datetime.strptime(date_str, "%B %d, %Y")
                        dt = pytz.timezone("America/Chicago").localize(dt)
                        if dt >= now:
                            events.append(entry.title.strip())
                    except Exception as e:
                        print(f"Error parsing '{entry.title}': {e}")
                break

    return render_template_string(TEMPLATE, events=events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
