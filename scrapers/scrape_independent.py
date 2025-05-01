import json
import requests
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.theindependentsf.com/", timeout=90000)
    page.wait_for_load_state("domcontentloaded")

    # Wait for iframe to load
    iframe_element = page.wait_for_selector("iframe[src*='ticketweb']")
    iframe = iframe_element.content_frame()

    # Wait for some event content to render inside iframe
    iframe.wait_for_selector(".tw-event-item", timeout=10000)
    event_items = iframe.query_selector_all(".tw-event-item")
    print(f"Found {len(event_items)} events")

    events = []
    for item in event_items:
        title_el = item.query_selector("p.title a") or item.query_selector("p.headliners")
        date_el = item.query_selector("p.date") or item.query_selector("p[class*='date']")
        time_el = item.query_selector("p.doortime-showtime")
        link_el = item.query_selector("a[href]")

        events.append({
            "artist": title_el.inner_text().strip() if title_el else None,
            "date": date_el.inner_text().strip() if date_el else None,
            "time": time_el.inner_text().strip() if time_el else None,
            "venue": "The Independent",
            "link": link_el.get_attribute("href") if link_el else None
        })

    browser.close()

print(json.dumps(events, indent=2))

# Optional: POST to ingest API
try:
    response = requests.post("http://localhost:5000/api/ingest", json=events)
    print("POST status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Failed to POST:", str(e))
