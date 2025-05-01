import json
import requests
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.theindependentsf.com/", timeout=60000)

    # ✅ Wait for key selector (artist names) to load
    page.wait_for_selector("p.headliners")

    event_elements = page.query_selector_all("div.tw-event-item")
    print(f"Found {len(event_elements)} events")

    events = []
    for item in event_elements:
        artist_el = item.query_selector("p.headliners")
        date_el = item.query_selector("p.date") or item.query_selector("p.fs-18.bold.mt-1r.date")
        time_el = item.query_selector("p.doortime-showtime")
        link_el = item.query_selector("p.title a") or item.query_selector("a[href]")

        events.append({
            "artist": artist_el.inner_text().strip() if artist_el else None,
            "date": date_el.inner_text().strip() if date_el else None,
            "time": time_el.inner_text().strip() if time_el else None,
            "venue": "The Independent",
            "link": link_el.get_attribute("href") if link_el else None
        })

    browser.close()

# Output for verification
print(json.dumps(events, indent=2))

# Send to ingest API
try:
    response = requests.post("http://localhost:5000/api/ingest", json=events)
    print("POST status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Failed to POST:", str(e))
