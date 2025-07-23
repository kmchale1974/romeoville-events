import requests, feedparser, html, re
from datetime import datetime, timedelta

CACHE = {"html": "", "last_fetch": datetime.min}

FEED_URL = "https://www.romeoville.org/rss.aspx?Category=0"
CACHE_DURATION = timedelta(minutes=30)

def build_html():
    global CACHE
    if datetime.now() - CACHE["last_fetch"] < CACHE_DURATION:
        return CACHE["html"]
    try:
        resp = requests.get(FEED_URL, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        feed = feedparser.parse(resp.content)
        events = []
        today = datetime.now().date()
        for entry in feed.entries:
            desc = html.unescape(entry.description or "")
            m_date = re.search(r'Event date[s]*:</strong>\s*([^<]+)', desc)
            m_time = re.search(r'Event Time:</strong>\s*([^<]+)', desc)
            m_loc = re.search(r'Location:</strong>\s*<br>([^<]+)', desc)
            if not m_date: continue
            date_str = m_date.group(1)
            d = datetime.fromisoformat(date_str.split("–")[0].strip()).date()
            if d < today: continue
            events.append({
                "title": entry.title,
                "date": date_str,
                "time": m_time.group(1).strip() if m_time else "",
                "loc": m_loc.group(1).strip() if m_loc else ""
            })
        html_parts = ["<h1 style='text-align:center;'>Romeoville Upcoming Events</h1><div>"]
        for ev in events:
            html_parts.append(f"<div style='margin-bottom:1em;'><strong>{ev['title']}</strong><br>"
                              f"{ev['date']} | {ev['time']}<br>"
                              f"{ev['loc']}, Romeoville, IL</div><hr>")
        if not events:
            html_parts.append("<p>No upcoming events at this time.</p>")
        html_parts.append("</div>")
        final_html = "<html><body>" + "".join(html_parts) + "</body></html>"
        CACHE["html"] = final_html
        CACHE["last_fetch"] = datetime.now()
        return final_html
    except Exception:
        return CACHE["html"] or ("<html><body><p>Unable to load events.</p></body></html>")