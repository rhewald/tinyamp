import json
import requests
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.theindependentsf.com/", timeout=90000)

    # Step 1: Close popup if it appears
    try:
        page.wait_for_selector("text='NO THANKS'", timeout=5000)
        page.click("text='NO THANKS'")
        print("✅ Closed popup.")
    except:
        print("ℹ️ No popup found or already closed.")

    # Step 2: Wait for container that holds events
    page.wait_for_selector("div#tw-upcoming-upcoming-event-list", timeout=15000)
    event_cards = page.query_selector_all("div#tw-upcoming-upcoming-event-list div.tw-event-item")

    print(f"Found {len(event_cards)} events")
    events = []
    for card in event_cards:
        artist_el = card.query_selector("p.headliners")
        date_el = card.query_selector("p.date, p.fs-18.bold.mt-1r.date")  # fallback
        time_el = card.query_selector("p.doortime-showtime")
        link_el = card.query_selector("a[href*='event']")

        events.append({
            "artist": artist_el.inner_text().strip() if artist_el else None,
            "date": date_el.inner_text().strip() if date_el else None,
            "time": time_el.inner_text().strip() if time_el else None,
            "venue": "The Independent",
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
