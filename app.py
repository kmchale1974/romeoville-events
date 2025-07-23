from flask import Flask, render_template_string
import feedparser
from datetime import datetime
import pytz

app = Flask(__name__)

RSS_FEED_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=58&CID=All-calendar.xml"

@app.route('/')
def index():
    feed = feedparser.parse(RSS_FEED_URL)
    events = []

    now = datetime.now(pytz.timezone("America/Chicago"))

    for entry in feed.entries:
        if 'published' in entry:
            try:
                event_date = datetime(*entry.published_parsed[:6], tzinfo=pytz.utc).astimezone(pytz.timezone("America/Chicago"))
                if event_date.date() >= now.date():
                    events.append({
                        'title': entry.title,
                        'date': event_date.strftime("%A, %B %d, %Y %I:%M %p"),
                        'link': entry.link
                    })
            except Exception as e:
                print(f"Skipping malformed date: {e}")
                continue

    return render_template_string("""
        <html>
        <head>
            <title>Romeoville Events</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 1rem; background: #f5f5f5; }
                h1 { text-align: center; color: #003865; }
                .event { background: #ffffff; margin: 10px auto; padding: 10px; border-radius: 8px; max-width: 600px; }
                .event h2 { margin: 0; font-size: 1.2em; }
                .event p { margin: 5px 0 0; color: #555; }
            </style>
        </head>
        <body>
            <h1>Romeoville Upcoming Events</h1>
            {% if events %}
                {% for event in events %}
                    <div class="event">
                        <h2>{{ event.title }}</h2>
                        <p>{{ event.date }}</p>
                        <p><a href="{{ event.link }}">Details</a></p>
                    </div>
                {% endfor %}
            {% else %}
                <p style="text-align:center;">No upcoming events found.</p>
            {% endif %}
        </body>
        </html>
    """, events=events)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
