from playwright.sync_api import sync_playwright
import requests

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
        # Try updated selector for title and link
        title_el = block.query_selector("div.tw-name a")
        date_el = block.query_selector("p.fs-18.bold.mt-1r.date")
        time_el = block.query_selector("p.doortime-showtime")

        artist = title_el.inner_text().strip() if title_el else None
        link = title_el.get_attribute("href") if title_el else None
        date = date_el.inner_text().strip() if date_el else None
        time = time_el.inner_text().strip() if time_el else None

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
