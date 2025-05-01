from playwright.sync_api import sync_playwright
import requests
from datetime import datetime

def normalize_date(short_date):
    """Convert dates like '5.1' to '2025-05-01'."""
    try:
        month, day = map(int, short_date.strip().split('.'))
        year = datetime.now().year
        today = datetime.today()
        event_date = datetime(year=year, month=month, day=day)
        # If somehow the event date has already passed, still assume current year (no wraparound)
        return event_date.strftime("%Y-%m-%d")
    except:
        return None

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    print("⏳ Loading page...")
    page.goto("https://www.theindependentsf.com/", timeout=60000)

    # Try closing the popup if it appears
    try:
        popup = page.query_selector("div#om-mnuwxyw8zcuetb2b-holder .om-close")
        if popup:
            popup.click()
            print("✅ Closed popup.")
        else:
            print("ℹ️ No popup found or already closed.")
    except:
        print("⚠️ Popup close failed (non-blocking).")

    print("⏳ Waiting for content to load...")
    page.wait_for_selector("div.tw-event-item", timeout=30000)
    event_blocks = page.query_selector_all("div.tw-event-item")
    print(f"✅ Found {len(event_blocks)} events")

    events = []

    for block in event_blocks:
        artist_el = block.query_selector("p.headliners")
        date_el = block.query_selector("span.tw-event-date")
        time_el = block.query_selector("span.tw-event-time-complete")
        link_el = block.query_selector("a")

        artist = artist_el.inner_text().strip() if artist_el else None
        short_date = date_el.inner_text().strip() if date_el else None
        time = time_el.inner_text().strip() if time_el else None
        link = link_el.get_attribute("href") if link_el else None

        date = normalize_date(short_date)

        if link and not link.startswith("http"):
            link = "https://www.theindependentsf.com" + link

        events.append({
            "artist": artist,
            "date": date,
            "time": time,
            "venue": "The Independent",
            "link": link
        })

    print(events)

    # Optional POST to local backend
    try:
        response = requests.post("http://localhost:3001/api/events", json=events)
        print(f"POST status: {response.status_code}")
        print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to localhost:3001 — skipping POST.")

    browser.close()
