from flask import Flask, render_template_string
import feedparser
from bs4 import BeautifulSoup
import re
from datetime import datetime

app = Flask(__name__)

RSS_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=58&CID=All-calendar.xml"

HTML_TEMPLATE = """
<!doctype html>
<title>Romeoville Events</title>
<h1>Upcoming Romeoville Events</h1>
{% if events %}
  <ul>
  {% for e in events %}
    <li><strong>{{ e.title }}</strong><br>
        {{ e.date_str }} | {{ e.time }}<br>
        {{ e.location }}<br>
        <a href="{{ e.link }}">Details</a>
    </li>
  {% endfor %}
  </ul>
{% else %}
  <p>No upcoming events found.</p>
{% endif %}
"""

def extract_event_date_and_time(desc_html):
    """Returns (date, date_str, time_range) or (None, None, None)."""
    soup = BeautifulSoup(desc_html, "html.parser")
    text = " ".join(soup.get_text(separator=" ").split())

    # Date: match "July 23, 2025"
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
            # Get clean location text
            loc_soup = BeautifulSoup(desc, "html.parser")
            loc_text = ""
            if "Location:" in loc_soup.get_text():
                # Grab everything after the "Location:" label
                parts = loc_soup.get_text().split("Location:", 1)[1].strip()
                loc_text = parts.split("Event Time:",1)[0].strip()
            events.append({
                "title": entry.get("title", "No title"),
                "date_str": date_str,
                "time": time_range,
                "location": loc_text,
                "link": entry.get("link", "#")
            })

    # Sort events chronologically
    events.sort(key=lambda e: datetime.strptime(e["date_str"], "%B %d, %Y").date())

    return render_template_string(HTML_TEMPLATE, events=events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 5000)))
