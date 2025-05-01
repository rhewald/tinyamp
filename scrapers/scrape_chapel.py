import json
import requests
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://thechapelsf.com/music/", timeout=60000)
    page.wait_for_load_state("networkidle")

    # Correct selector for each event
    event_items = page.query_selector_all(".event-info-block")
    print(f"Found {len(event_items)} events")

    events = []
    for item in event_items:
        title_el = item.query_selector("p.title a")
        date_el = item.query_selector("p.date")
        time_el = item.query_selector("p.doortime.showtime") or item.query_selector("p.doortime") or item.query_selector("p.time")
        link_el = title_el or item.query_selector("a")

        events.append({
            "artist": title_el.inner_text().strip() if title_el else None,
            "date": date_el.inner_text().strip() if date_el else None,
            "time": time_el.inner_text().strip() if time_el else None,
            "venue": "The Chapel",
            "link": link_el.get_attribute("href") if link_el else None
        })

    browser.close()

# Show result
print(json.dumps(events, indent=2))

# Optional POST
try:
    response = requests.post("http://localhost:5000/api/ingest", json=events)
    print("POST status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Failed to POST:", str(e))
