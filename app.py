from flask import Flask, render_template_string
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

app = Flask(__name__)

FEED_URL = "https://www.romeoville.org/Calendar.aspx?RSS=1&CID=14"

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Debug View - Romeoville Events</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 2em; background: #fff; color: #333; }
        h1 { color: #222; }
        .event { margin-bottom: 1em; }
    </style>
</head>
<body>
    <h1>Parsed Events</h1>
    {% if events %}
        {% for event in events %}
            <div class="event">
                <strong>{{ event.title }}</strong><br>
                Date: {{ event.date }}<br>
            </div>
        {% endfor %}
    {% else %}
        <p>No upcoming events found.</p>
    {% endif %}
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
                        print(f"Parsed '{entry.title}' -> {event_date}")
                        if event_date >= now:
                            parsed_events.append({
                                "title": entry.title,
                                "date": event_date.strftime("%B %d, %Y")
                            })
                    except Exception as e:
                        print(f"Failed to parse '{entry.title}': {e}")
                break

    return render_template_string(TEMPLATE, events=parsed_events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
