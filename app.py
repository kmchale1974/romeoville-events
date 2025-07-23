from flask import Flask, render_template_string
import feedparser

app = Flask(__name__)

RSS_FEED_URL = "https://www.romeoville.org/RSSFeed.aspx?ModID=58&CID=All-calendar.xml"

@app.route('/')
def index():
    feed = feedparser.parse(RSS_FEED_URL)

    debug_entries = []

    for entry in feed.entries:
        debug_entries.append({
            'title': getattr(entry, 'title', 'N/A'),
            'link': getattr(entry, 'link', 'N/A'),
            'published': getattr(entry, 'published', 'N/A'),
            'published_parsed': str(getattr(entry, 'published_parsed', 'N/A')),
            'summary': getattr(entry, 'summary', 'N/A'),
            'keys': list(entry.keys())
        })

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DEBUG: Romeoville RSS Feed</title>
        <style>
            body { font-family: monospace; background: #f5f5f5; padding: 2rem; }
            h1 { color: #003865; }
            .entry { background: white; padding: 1rem; margin-bottom: 1.5rem; border-left: 5px solid #003865; }
        </style>
    </head>
    <body>
        <h1>Romeoville RSS Feed - DEBUG VIEW</h1>
        {% for entry in debug_entries %}
            <div class="entry">
                <strong>Title:</strong> {{ entry.title }}<br>
                <strong>Link:</strong> <a href="{{ entry.link }}">{{ entry.link }}</a><br>
                <strong>Published:</strong> {{ entry.published }}<br>
                <strong>Published Parsed:</strong> {{ entry.published_parsed }}<br>
                <strong>Summary:</strong> {{ entry.summary|safe }}<br>
                <strong>All Keys:</strong> {{ entry.keys }}
            </div>
        {% endfor %}
    </body>
    </html>
    """, debug_entries=debug_entries)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
