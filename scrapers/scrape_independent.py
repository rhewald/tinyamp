from playwright.sync_api import sync_playwright
from scraper_utils import normalize_date, normalize_time, insert_unique_events

def scrape_independent_events():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("⏳ Loading page...")
        page.goto("https://www.theindependentsf.com/", timeout=60000)

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
            artist_el = block.query_selector("div.tw-name > a")  # 🛠 Corrected
            date_el = block.query_selector("span.tw-event-date")
            time_el = block.query_selector("span.tw-event-time-complete")
            link_el = artist_el

            artist = artist_el.inner_text().strip() if artist_el else None
            short_date = date_el.inner_text().strip() if date_el else None
            raw_time = time_el.inner_text().strip() if time_el else None
            link = link_el.get_attribute("href") if link_el else None

            if link and not link.startswith("http"):
                link = "https://www.theindependentsf.com" + link

            date = normalize_date(short_date)
            time = normalize_time(raw_time)

            if artist and date:
                events.append({
                    "artist": artist,
                    "date": date,
                    "time": time,
                    "venue": "The Independent",
                    "link": link
                })
            else:
                print("⚠️ Skipping event due to missing artist or date.")

        print(events)

        result = insert_unique_events(events) or {"inserted": 0, "skipped": 0}
        print(f"\nDone. Inserted: {result['inserted']}, Skipped (duplicates): {result['skipped']}")

        browser.close()

if __name__ == "__main__":
    scrape_independent_events()
