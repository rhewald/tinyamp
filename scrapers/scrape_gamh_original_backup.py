from playwright.sync_api import sync_playwright
import requests
from datetime import datetime
import re

def parse_date(text):
    try:
        parts = text.strip().split()
        if len(parts) == 3:  # e.g., "Thu May 1"
            month = datetime.strptime(parts[1], "%b").month
            day = int(parts[2])
            year = datetime.now().year
            return datetime(year, month, day).strftime("%Y-%m-%d")
    except:
        return None

def scrape_gamh_events():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("⏳ Loading GAMH page...")
        page.goto("https://gamh.com/", timeout=60000)
        page.wait_for_selector("div.seetickets-list-event-container", timeout=30000)

        event_blocks = page.query_selector_all("div.seetickets-list-event-container")
        print(f"✅ Found {len(event_blocks)} events")

        events = []

        for block in event_blocks:
            title_el = block.query_selector("p.event-title a")
            date_el = block.query_selector("p.event-date")
            time_el = block.query_selector("p.doortime-showtime")

            artist = title_el.inner_text().strip() if title_el else None
            link = title_el.get_attribute("href") if title_el else None
            raw_date = date_el.inner_text().strip() if date_el else None
            date = parse_date(raw_date)
            time = time_el.inner_text().strip() if time_el else None

            if artist and date:
                events.append({
                    "artist": artist.upper(),
                    "date": date,
                    "time": time,
                    "venue": "Great American Music Hall",
                    "link": link
                })
            else:
                print("⚠️ Skipping incomplete event block")

        print(events)

        try:
            response = requests.post("http://localhost:3001/api/events", json=events)
            print(f"POST status: {response.status_code}")
            print(f"Response: {response.text}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to backend — skipping POST.")

        browser.close()

if __name__ == "__main__":
    scrape_gamh_events()
