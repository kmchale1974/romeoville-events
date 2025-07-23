from flask import Flask, render_template_string
import feedparser
from datetime import datetime
import os

app = Flask(__name__)

RSS_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=76&CID=All-0"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Romeoville Upcoming Events</title>
  <style>
    body { font-family: Arial, sans-serif; background: #002856; color: white; margin:0; padding:0; overflow:hidden; }
    h1 { text-align:center; background:#0066a1; padding:20px; margin:0; font-size:2em; }
    .scroll-container { height:90vh; overflow:hidden; position:relative; }
    .events { animation: scroll-up 30s linear infinite; padding:20px; }
    .event { margin-bottom: 30px; border-bottom: 1px solid #ccc; padding-bottom:10px; }
    .title { font-size:1.5em; color:#ffc72c; }
    .datetime { font-size:1.1em; color:#ddd; }
    @keyframes scroll-up { 0% { transform: translateY(100%); } 100% { transform: translateY(-100%); } }
  </style>
</head>
<body>
  <h1>Romeoville Upcoming Events</h1>
  <div class="scroll-container">
    <div class="events">
      {% for e in events %}
        <div class="event">
          <div class="title">{{ e.title }}</div>
          <div class="datetime">{{ e.date }} — {{ e.time }}</div>
        </div>
      {% endfor %}
      {% if not events %}
        <div class="event">No upcoming events found.</div>
      {% endif %}
    </div>
  </div>
</body>
</html>
"""

@app.route("/")
def index():
    feed = feedparser.parse(RSS_URL)
    now = datetime.now()
    events = []

    for entry in feed.entries:
        # feedparser extracts date info automatically
        dt = None
        if hasattr(entry, "published_parsed"):
            dt = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, "updated_parsed"):
            dt = datetime(*entry.updated_parsed[:6])

        if dt and dt >= now:
            date_str = dt.strftime("%B %d, %Y")
            time_str = dt.strftime("%I:%M %p").lstrip("0")
            events.append({"title": entry.title, "date": date_str, "time": time_str})

    # sort chronologically
    events.sort(key=lambda e: datetime.strptime(e["date"] + " " + e["time"], "%B %d, %Y %I:%M %p"))
    return render_template_string(HTML_TEMPLATE, events=events)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
