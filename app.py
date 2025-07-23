from flask import Flask, render_template_string
import feedparser
from bs4 import BeautifulSoup
import re
from datetime import datetime

app = Flask(__name__)

RSS_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=58&CID=All-calendar.xml"

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Romeoville Upcoming Events</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            margin: 0;
            padding: 0;
            text-align: center;
            overflow: hidden;
        }
        h1 {
            background-color: #6a1b1a;
            color: white;
            padding: 20px;
            margin: 0;
        }
        .scrolling-container {
            height: 100vh;
            overflow: hidden;
            position: relative;
        }
        .event-list {
            display: inline-block;
            text-align: center;
            animation: scroll-up linear infinite;
            animation-duration: 40s;
        }
        .event {
            padding: 20px 0;
            font-size: 1.4em;
            color: #333;
        }
        @keyframes scroll-up {
            0% { transform: translateY(100%); }
            100% { transform: translateY(-100%); }
        }
        @media (max-width: 768px) {
            .event {
                font-size: 1.1em;
                padding: 15px 0;
            }
        }
    </style>
</head>
<body>
    <h1>Romeoville Upcoming Events</h1>
    <div class="scrolling-container">
        <div class="event-list">
            {% for event in events %}
                <div class="event">{{ event.date }} — {{ event.title }}</div>
            {% endfor %}
            <!-- Repeat events to ensure smooth loop -->
            {% for event in events %}
                <div class="event">{{ event.date }} — {{ event.title }}</div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""


def extract_event_date_and_time(desc_html):
    soup = BeautifulSoup(desc_html, "html.parser")
    text = " ".join(soup.get_text(separator=" ").split())

    date_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}", text)
    time_match = re.search(r"(\d{1,2}:\d{2} (?:AM|PM) - \d{1,2}:\d{2} (?:AM|PM))", text)

    if not date_match:
        return None, None, None

    date_str = date_match.group(0)
    try:
        event_date = datetime.strptime(date_str, "%B %d, %Y").date()
    except ValueError:
        return None, None, None

    time_range = time_match.group(1) if time_match else ""
    return event_date, date_str, time_range

@app.route("/")
def index():
    fp = feedparser.parse(RSS_URL)
    events = []
    today = datetime.now().date()

    for entry in fp.entries:
        desc = entry.get("summary", entry.get("description", ""))
        event_date, date_str, time_range = extract_event_date_and_time(desc)
        if event_date and event_date >= today:
            soup = BeautifulSoup(desc, "html.parser")
            text = soup.get_text()
            loc = ""
            if "Location:" in text:
                loc = text.split("Location:")[1].split("Event Time:")[0].strip().replace("\n", " ")
            events.append({
                "title": entry.get("title", "No title"),
                "date_str": date_str,
                "time": time_range,
                "location": loc,
            })

    events.sort(key=lambda e: datetime.strptime(e["date_str"], "%B %d, %Y").date())

    # Approximate scroll speed: 4 seconds per item
    duration = max(len(events), 1) * 4

    return render_template_string(HTML_TEMPLATE, events=events, duration=duration)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 5000)))
