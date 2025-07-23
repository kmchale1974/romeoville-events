from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Romeoville Events</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #002856;
            color: #fff;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        h1 {
            text-align: center;
            background: #0066a1;
            padding: 20px;
            margin: 0;
            font-size: 2em;
        }
        .scroll-container {
            height: 90vh;
            overflow: hidden;
            position: relative;
        }
        .events {
            animation: scroll-up 30s linear infinite;
            padding: 20px;
            box-sizing: border-box;
        }
        .event {
            margin-bottom: 30px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 10px;
        }
        .title {
            font-size: 1.5em;
            color: #ffc72c;
        }
        .datetime {
            font-size: 1.1em;
            color: #ddd;
        }

        @keyframes scroll-up {
            0% { transform: translateY(100%); }
            100% { transform: translateY(-100%); }
        }
    </style>
</head>
<body>
    <h1>Romeoville Upcoming Events</h1>
    <div class="scroll-container">
        <div class="events">
            {% for event in events %}
                <div class="event">
                    <div class="title">{{ event.title }}</div>
                    <div class="datetime">{{ event.date }} — {{ event.time }}</div>
                </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    url = "https://www.romeoville.org/calendar.aspx?view=list"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    events = []
    today = datetime.now().date()

    items = soup.select(".listItem")
    for item in items:
        title_el = item.select_one(".itemTitle a")
        date_el = item.select_one(".itemDate")
        time_el = item.select_one(".itemTime")

        if title_el and date_el:
            title = title_el.get_text(strip=True)
            date_str = date_el.get_text(strip=True)
            try:
                date_obj = datetime.strptime(date_str, "%B %d, %Y").date()
            except ValueError:
                continue  # skip invalid dates

            if date_obj >= today:
                events.append({
                    "title": title,
                    "date": date_str,
                    "time": time_el.get_text(strip=True) if time_el else "Time not listed"
                })

    return render_template_string(TEMPLATE, events=events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
