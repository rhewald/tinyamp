import json
import requests
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.theindependentsf.com/", timeout=90000, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)  # Let dynamic content load

    event_items = page.query_selector_all("div.tw-event-item")
    print(f"Found {len(event_items)} events")

    events = []
    for item in event_items:
        artist_el = item.query_selector("img[alt]")
        date_el = item.query_selector(".tw-event-info .tw-event-date-time .date")
        time_el = item.query_selector(".tw-event-info .tw-event-date-time .time")
        link_el = item.query_selector(".tw-event-info .tw-event-date-time a[href]")

        events.append({
            "artist": artist_el.get_attribute("alt") if artist_el else None,
            "date": date_el.inner_text().strip() if date_el else None,
            "time": time_el.inner_text().strip() if time_el else None,
            "venue": "The Independent",
            "link": link_el.get_attribute("href") if link_el else None
        })

    browser.close()

print(json.dumps(events, indent=2))

# Optional POST
try:
    response = requests.post("http://localhost:5000/api/ingest", json=events)
    print("POST status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Failed to POST:", str(e))
