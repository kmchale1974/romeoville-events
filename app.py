from flask import Flask, render_template_string
import feedparser
from datetime import datetime
import pytz
import time

app = Flask(__name__)

RSS_FEED_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=58&CID=All-calendar.xml"

@app.route('/')
def index():
    feed = feedparser.parse(RSS_FEED_URL)
    events = []

    now = datetime.now(pytz.timezone("America/Chicago"))

    for entry in feed.entries:
        try:
            # Try using published_parsed (if available)
            if hasattr(entry, 'published_parsed'):
                event_time = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=pytz.utc)
            else:
                # Fallback to parsing pubDate manually
                pub_date = entry.get('pubDate') or entry.get('published')
                if pub_date:
                    event_time = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=pytz.utc)
                else:
                    continue

            event_time_local = event_time.astimezone(pytz.timezone("America/Chicago"))
            if event_time_local.date() >= now.date():
                events.append({
                    'title': entry.title,
                    'date': event_time_local.strftime("%A, %B %d, %Y"),
                    'link': entry.link
                })
        except Exception as e:
            print(f"Skipping event due to error: {e}")
            continue

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Romeoville Events</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f0f4f8; color: #003865; padding: 2rem; text-align: center; }
            h1 { color: #003865; }
            .event { background: white; margin: 1rem auto; padding: 1rem; max-width: 600px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .event h2 { margin: 0 0 0.5rem; }
            .event p { margin: 0.3rem 0; }
        </style>
    </head>
    <body>
        <h1>Romeoville Upcoming Events</h1>
        {% if events %}
            {% for event in events %}
                <div class="event">
                    <h2>{{ event.title }}</h2>
                    <p>{{ event.date }}</p>
                    <p><a href="{{ event.link }}" target="_blank">More Info</a></p>
                </div>
            {% endfor %}
        {% else %}
            <p>No upcoming events found.</p>
        {% endif %}
    </body>
    </html>
    """, events=events)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
