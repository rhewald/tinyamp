import json
import requests
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.theindependentsf.com/", timeout=60000)
    page.wait_for_load_state("networkidle")  # Wait for dynamic content

    # Select the root event container
    event_blocks = page.query_selector_all("div.tw-event-item")

    print(f"Found {len(event_blocks)} events")

    events = []
    for block in event_blocks:
        # Extract elements
        title_el = block.query_selector("p.headliners")
        date_el = block.query_selector("p.date, p.fs-18.bold.mt-1r.date")
        time_el = block.query_selector("p.doortime-showtime")
        link_el = block.query_selector("a[href*='/event/']")

        events.append({
            "artist": title_el.inner_text().strip() if title_el else None,
            "date": date_el.inner_text().strip() if date_el else None,
            "time": time_el.inner_text().strip() if time_el else None,
            "venue": "The Independent",
            "link": link_el.get_attribute("href") if link_el else None
        })

    browser.close()

# Output result
print(json.dumps(events, indent=2))

# Optional: post to local ingest endpoint
try:
    response = requests.post("http://localhost:5000/api/ingest", json=events)
    print("POST status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Failed to POST:", str(e))
