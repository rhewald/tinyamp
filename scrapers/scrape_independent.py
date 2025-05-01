from playwright.sync_api import sync_playwright
import requests
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    print("⏳ Loading page...")
    page.goto("https://www.theindependentsf.com/", timeout=60000)

    # Close popup if it appears
    try:
        popup_close = page.query_selector("div#om-mnuwxyw8zcuetb2b-holder .om-close")
        if popup_close:
            popup_close.click()
            print("✅ Closed popup.")
        else:
            print("ℹ️ No popup found or already closed.")
    except:
        print("⚠️ Error while trying to close popup (may not be critical)")

    print("⏳ Waiting for content to load...")
    page.wait_for_selector("div.tw-event-item", timeout=30000)

    event_blocks = page.query_selector_all("div.tw-event-item")
    print(f"Found {len(event_blocks)} events")

    events = []

    for block in event_blocks:
        artist_el = block.query_selector("p.headliners")
        date_el = block.query_selector("p.fs-18.bold.mt-1r.date")
        time_el = block.query_selector("p.doortime-showtime")
        link_el = block.query_selector("a[href*='/event/']")

        events.append({
            "artist": artist_el.inner_text().strip() if artist_el else None,
            "date": date_el.inner_text().strip() if date_el else None,
            "time": time_el.inner_text().strip() if time_el else None,
            "venue": "The Independent",
            "link": link_el.get_attribute("href") if link_el else None
        })

    print(events)

    # Optionally post to backend
    response = requests.post("http://localhost:3001/api/events", json=events)
    print(f"POST status: {response.status_code}")
    print(f"Response: {response.text}")

    browser.close()
