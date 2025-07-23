from flask import Flask, render_template_string
import feedparser
import datetime
import pytz

app = Flask(__name__)

FEED_URL = "https://www.romeoville.org/Calendar.aspx?feed=calendar"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Romeoville Upcoming Events</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #00205B;
            font-family: Arial, sans-serif;
            color: white;
            overflow: hidden;
        }
        h1 {
            text-align: center;
            background-color: #C8102E;
            padding: 20px;
            margin: 0;
        }
        .events-wrapper {
            position: relative;
            height: 100vh;
            overflow: hidden;
        }
        .scrolling-events {
            position: absolute;
            width: 100%;
            animation: scroll-up 60s linear infinite;
        }
        .event {
            padding: 20px;
            border-bottom: 1px solid #ccc;
            text-align: center;
        }
        .event-title {
            font-size: 1.5em;
            color: #FFD100;
        }
        .event-date, .event-time, .event-location {
            font-size: 1.2em;
        }

        @keyframes scroll-up {
            0% { top: 100%; }
            100% { top: -100%; }
        }
    </style>
</head>
<body>
    <h1>Romeoville Upcoming Events</h1>
    <div class="events-wrapper">
        <div class="scrolling-events">
            {% if events %}
                {% for event in events %}
                <div class="event">
                    <div class="event-title">{{ event.title }}</div>
                    <div class="event-date">{{ event.date }}</div>
                    <div class="event-time">{{ event.time }}</div>
                    <div class="event-location">{{ event.location }}</div>
                </div>
                {% endfor %}
            {% else %}
                <div class="event">No upcoming events found.</div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

def parse_event_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%B %d, %Y").date()
    except Exception:
        return None

@app.route('/')
def index():
    feed = feedparser.parse(FEED_URL)
    today = datetime.datetime.now(pytz.timezone("America/Chicago")).date()

    events = []
    for entry in feed.entries:
        summary = entry.get("summary", "")
        title = entry.get("title", "No Title")
        link = entry.get("link", "")

        date_text = time_text = location_text = ""
        if "Event date:" in summary or "Event dates:" in summary:
            parts = summary.split("<br>")
            for part in parts:
                if "Event date:" in part:
                    date_text = part.replace("Event date:", "").strip()
                elif "Event dates:" in part:
                    date_text = part.replace("Event dates:", "").strip().split("-")[0].strip()
                elif "Event Time:" in part:
                    time_text = part.replace("Event Time:", "").strip()
                elif "Location:" in part:
                    location_text = part.replace("Location:", "").strip()

        event_date = parse_event_date(date_text)
        if event_date and event_date >= today:
            events.append({
                "title": title,
                "date": date_text,
                "time": time_text,
                "location": location_text,
                "link": link
            })

    events.sort(key=lambda x: parse_event_date(x["date"]))
    return render_template_string(HTML_TEMPLATE, events=events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
