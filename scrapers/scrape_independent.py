import json
import requests
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.theindependentsf.com/", timeout=90000, wait_until="networkidle")
    page.wait_for_timeout(3000)  # Let JS render the list

    event_blocks = page.query_selector_all(".tw-event-item")
    print(f"Found {len(event_blocks)} events")

    events = []
    for item in event_blocks:
        title_el = item.query_selector("p.title a")
        date_el = item.query_selector("p.date")
        time_el = item.query_selector("p.doortime-showtime")
        link_el = title_el or item.query_selector("a[href]")

        events.append({
            "artist": title_el.inner_text().strip() if title_el else None,
            "date": date_el.inner_text().strip() if date_el else None,
            "time": time_el.inner_text().strip() if time_el else None,
            "venue": "The Independent",
            "link": link_el.get_attribute("href") if link_el else None
        })

    browser.close()

print(json.dumps(events, indent=2))

# Optional POST to API
try:
    response = requests.post("http://localhost:5000/api/ingest", json=events)
    print("POST status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Failed to POST:", str(e))
