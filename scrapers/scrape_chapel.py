import json
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://thechapelsf.com/music/", timeout=60000)
    page.wait_for_selector("#event-list")

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    event_elements = soup.select("#event-list .event-item")

    events = []
    for event in event_elements:
        date = event.select_one(".event-date, .date")
        title = event.select_one(".event-title, h2")
        time = event.select_one(".event-time, .time")
        link = event.select_one("a")["href"] if event.select_one("a") else None

        events.append({
            "date": date.get_text(strip=True) if date else None,
            "artist": title.get_text(strip=True) if title else None,
            "time": time.get_text(strip=True) if time else None,
            "venue": "The Chapel",
            "link": link if link and link.startswith("http") else f"https://thechapelsf.com{link}" if link else None
        })

    browser.close()

# Optional: print to console for debugging
print(json.dumps(events, indent=2))

# Send to backend API
response = requests.post("http://localhost:5000/api/ingest", json=events)
print("POST status:", response.status_code)
print("Response:", response.text)

