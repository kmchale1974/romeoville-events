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
            animation: scrollUp 60s linear infinite;
        }
        @keyframes scrollUp {
            0%   { transform: translateY(100%); }
            100% { transform: translateY(-100%); }
        }
        .event {
            margin: 2em 0;
            font-size: 1.5em;
            font-weight: bold;
            padding: 1em;
        }
        .event:nth-child(even) {
            background-color: #f0f8ff; /* Soft blue */
            border-radius: 8px;
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

@app.route("/")
def index():
    feed = feedparser.parse(FEED_URL)
    now = datetime.now(pytz.timezone("America/Chicago"))
    upcoming_events = []

    for entry in feed.entries:
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                event_date = datetime(*entry.published_parsed[:6], tzinfo=pytz.utc).astimezone(pytz.timezone("America/Chicago"))
                if event_date >= now:
                    summary = getattr(entry, 'summary', '').strip()
                    location = entry.get('location', '')
                    display_text = f"{event_date.strftime('%A, %B %d, %Y at %I:%M %p')} - {entry.title}"
                    if summary:
                        display_text += f"<br><small>{summary}</small>"
                    upcoming_events.append(display_text)
        except Exception as e:
            print(f"Error parsing entry '{entry}': {e}")

    return render_template_string(TEMPLATE, events=upcoming_events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
