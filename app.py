from flask import Flask, render_template_string
import requests
from ics import Calendar
import datetime
import os

app = Flask(__name__)

ICS_URL = "https://www.romeoville.org/calendar.aspx?view=list&format=ical"

HTML_TEMPLATE = """<!DOCTYPE html>
<html><head><style>body { font-family:Arial, sans-serif; } .event{margin-bottom:20px;} h1{text-align:center;} </style></head><body>
<h1>Romeoville Upcoming Events</h1>
{% if events %}
  {% for e in events %}
    <div class="event">
      <strong>{{ e.name }}</strong><br>
      {{ e.begin }} – {{ e.end }}<br>
      {{ e.location }}
    </div>
  {% endfor %}
{% else %}
  <div>No upcoming events found.</div>
{% endif %}
</body></html>"""

@app.route('/')
def index():
    r = requests.get(ICS_URL, timeout=10)
    cal = Calendar(r.text)
    now = datetime.datetime.now()
    upcoming = []

    for ev in cal.events:
        if ev.begin.datetime >= now:
            upcoming.append({
                "name": ev.name,
                "begin": ev.begin.format('MMMM D, YYYY h:mm A'),
                "end": ev.end.format('h:mm A'),
                "location": ev.location or ""
            })

    upcoming.sort(key=lambda x: datetime.datetime.strptime(x["begin"], "%B %d, %Y %I:%M %p"))
    return render_template_string(HTML_TEMPLATE, events=upcoming)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
