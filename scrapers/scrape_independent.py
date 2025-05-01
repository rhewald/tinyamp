import json
import requests
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.theindependentsf.com/", timeout=60000)
    page.wait_for_load_state("networkidle")

    # Scroll to load events if lazy-loaded
    page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)

    event_items = page.query_selector_all("li.Component-EventCard")  # Common class name for event blocks
    print(f"Found {len(event_items)} events")

    events = []
    for item in event_items:
        title_el = item.query_selector(".EventCardHeadliner")
        date_el = item.query_selector(".EventCardDate-date")
        link_el = item.query_selector("a[href]")

        events.append({
            "artist": title_el.inner_text().strip() if title_el else None,
            "date": date_el.inner_text().strip() if date_el else None,
            "time": None,  # Not shown on main page
            "venue": "The Independent",
            "link": link_el.get_attribute("href") if link_el else None
        })

    browser.close()

print(json.dumps(events, indent=2))

# Optional POST to your ingest API
try:
    response = requests.post("http://localhost:5000/api/ingest", json=events)
    print("POST status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Failed to POST:", str(e))
