from flask import Flask, render_template_string
import feedparser
from bs4 import BeautifulSoup
import re
from datetime import datetime

app = Flask(__name__)

RSS_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=58&CID=All-calendar.xml"

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Romeoville Events</title>
  <style>
    body {
      margin: 0;
      font-family: sans-serif;
      background: #f9f9f9;
      color: #222;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    h1 {
      text-align: center;
      margin-top: 1rem;
    }
    .scroll-container {
      height: 80vh;
      width: 100%;
      max-width: 800px;
      overflow: hidden;
      position: relative;
    }
    .scroll-content {
      display: flex;
      flex-direction: column;
      animation: scrollUp linear infinite;
    }
    .event {
      padding: 1rem;
      text-align: center;
      border-bottom: 1px solid #ddd;
    }
    @keyframes scrollUp {
      0% { transform: translateY(100%); }
      100% { transform: translateY(-100%); }
    }
  </style>
</head>
<body>
  <h1>Upcoming Romeoville Events</h1>
  {% if events %}
  <div class="scroll-container">
    <div class="scroll-content" style="animation-duration: {{ duration }}s;">
      {% for _ in range(2) %}  {# Loop twice to create smooth loop #}
        {% for e in events %}
          <div class="event">
            <strong>{{ e.title }}</strong><br>
            {{ e.date_str }}<br>
            {{ e.time }}<br>
            {{ e.location }}
          </div>
        {% endfor %}
      {% endfor %}
    </div>
  </div>
  {% else %}
    <p>No upcoming events found.</p>
  {% endif %}
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
