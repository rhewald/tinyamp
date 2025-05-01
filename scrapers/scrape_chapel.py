import json
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://thechapelsf.com/music/", timeout=60000)
    page.wait_for_load_state("networkidle")  # Wait for network to go idle (safer than relying on a selector)

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Optional: dump HTML for debugging
    # with open("chapel_debug.html", "w") as f:
    #     f.write(html)

    event_elements = soup.select(".event-listing, .event-item")  # Looser selector just in case

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

print(json.dumps(events, indent=2))

# OPTIONAL: POST to your ingest API
try:
    response = requests.post("http://localhost:5000/api/ingest", json=events)
    print("POST status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Failed to POST:", str(e))
