from flask import Flask, render_template_string
import feedparser
import datetime
import pytz
import os

app = Flask(__name__)

FEED_URL = "https://www.romeoville.org/Calendar.aspx?feed=calendar"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Romeoville Upcoming Events</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #002856;
            color: white;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        h1 {
            text-align: center;
            background-color: #006747;
            margin: 0;
            padding: 20px 0;
            font-size: 2em;
        }
        .scroll-container {
            height: calc(100vh - 80px);
            overflow: hidden;
            position: relative;
        }
        .scroll-content {
            position: absolute;
            width: 100%;
            animation: scroll-up 40s linear infinite;
        }
        .event {
            padding: 20px;
            border-bottom: 1px solid #ccc;
            width: 100%;
            box-sizing: border-box;
            text-align: center;
        }
        .event h2 {
            color: #f4c542;
            margin: 0 0 10px 0;
            font-size: 1.5em;
        }
        .event p {
            margin: 5px 0;
            font-size: 1.1em;
        }
        @keyframes scroll-up {
            0% {
                top: 100%;
            }
            100% {
                top: -100%;
            }
        }
    </style>
</head>
<body>
    <h1>Romeoville Upcoming Events</h1>
    <div class="scroll-container">
        <div class="scroll-content">
            {% for event in events %}
            <div class="event">
                <h2>{{ event.title }}</h2>
                <p><strong>Date:</strong> {{ event.date }}</p>
                <p><strong>Time:</strong> {{ event.time }}</p>
                <p><strong>Location:</strong> {{ event.location }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

def parse_event_date(text):
    try:
        # Example: July 21, 2025
        return datetime.datetime.strptime(text.strip(), "%B %d, %Y").date()
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
        
        # Extract pieces
        date_text = time_text = location_text = ""
        if "Event date:" in summary:
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

    # Sort by date
    events.sort(key=lambda x: parse_event_date(x["date"]))
   
    print(f"Found {len(events)} events")
for e in events:
    print(e)

    return render_template_string(HTML_TEMPLATE, events=events)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
