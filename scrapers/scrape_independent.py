import json
import requests
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.theindependentsf.com/", timeout=90000)

    # Close the popup if it's there
    try:
        page.click("text='NO THANKS'", timeout=5000)
        print("✅ Popup closed.")
    except:
        print("ℹ️ No popup found or already closed.")

    # Add a short delay to let JS-rendered content load
    print("⏳ Waiting for content to load...")
    time.sleep(5)

    # Select event blocks more defensively
    event_blocks = page.query_selector_all("div.tw-event-item")
    print(f"Found {len(event_blocks)} events")

    events = []
    for block in event_blocks:
        artist_el = block.query_selector("p.headliners")
        date_el = block.query_selector("p.date") or block.query_selector("p.fs-18.bold.mt-1r.date")
        time_el = block.query_selector("p.doortime-showtime")
        link_el = block.query_selector("p.title a")

        events.append({
            "artist": artist_el.inner_text().strip() if artist_el else None,
            "date": date_el.inner_text().strip() if date_el else None,
            "time": time_el.inner_text().strip() if time_el else None,
            "venue": "The Independent",
            "link": link_el.get_attribute("href") if link_el else None
        })

    browser.close()

# Output
print(json.dumps(events, indent=2))

# POST
try:
    response = requests.post("http://localhost:5000/api/ingest", json=events)
    print("POST status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Failed to POST:", str(e))
