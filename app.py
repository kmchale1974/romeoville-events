from bs4 import BeautifulSoup
import re

@app.route("/")
def index():
    feed = feedparser.parse(FEED_URL)
    now = datetime.now(pytz.timezone("America/Chicago"))
    upcoming_events = []

    for entry in feed.entries:
        try:
            soup = BeautifulSoup(entry.description, "html.parser")
            text = soup.get_text(separator="\n")  # Keep line breaks for parsing

            # Extract date
            date_match = re.search(r'Event date:\s*([A-Za-z]+ \d{1,2}, \d{4})', text)
            if not date_match:
                continue

            event_date_str = date_match.group(1)
            event_date = datetime.strptime(event_date_str, "%B %d, %Y")
            event_date = pytz.timezone("America/Chicago").localize(event_date)

            if event_date >= now:
                # Extract time and location
                time_match = re.search(r'Time:\s*(.*)', text)
                location_match = re.search(r'Location:\s*(.*)', text)

                time_str = time_match.group(1).strip() if time_match else "Time not listed"
                location_str = location_match.group(1).strip() if location_match else "Location not listed"

                display_text = f"{entry.title} – {event_date_str} @ {time_str} ({location_str})"
                upcoming_events.append(display_text)

        except Exception as e:
            print(f"Error parsing entry: {e}")

    return render_template_string(TEMPLATE, events=upcoming_events)
