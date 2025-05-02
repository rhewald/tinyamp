from playwright.sync_api import sync_playwright
import requests
from datetime import datetime

def normalize_date(text):
    try:
        return datetime.strptime(text.strip(), "%A %B %d %Y").strftime("%Y-%m-%d")
    except Exception:
        return None

def scrape_bottom_of_the_hill():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("⏳ Loading Bottom of the Hill page...")
        page.goto("https://www.bottomofthehill.com/calendar.html", timeout=60000)

        event_blocks = page.query_selector_all("td[style*='background-color: rgb(204, 204, 51)']")
        print(f"✅ Found {len(event_blocks)} event blocks")

        events = []

        for i, block in enumerate(event_blocks):
            date_el = block.query_selector("span.date")
            band_els = block.query_selector_all("big.band")

            if not date_el:
                print(f"⚠️ [Block {i}] No date found")
                continue
            if not band_els:
                print(f"⚠️ [Block {i}] No artists found")
                continue

            # Parse date
            date_text = date_el.inner_text().strip() + " 2025"
            date = normalize_date(date_text)
            if not date:
                print(f"⚠️ [Block {i}] Could not parse date: '{date_text}'")
                continue

            # Parse bands
            artists = [el.inner_text().strip().upper() for el in band_els]
            artist_string = ", ".join(artists)

            # Extract time info
            text = block.inner_text()
            time_lines = [line.strip() for line in text.splitlines() if "door" in line.lower()]
            show_time = time_lines[0] if time_lines else ""

            events.append({
                "artist": artist_string,
                "date": date,
                "time": show_time,
                "venue": "Bottom of the Hill",
                "link": "https://www.bottomofthehill.com/calendar.html"
            })

        print(events)

        try:
            response = requests.post("http://localhost:3001/api/events", json=events)
            print(f"POST status: {response.status_code}")
            print(f"Response: {response.text}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to localhost:3001 — skipping POST.")

        browser.close()

if __name__ == "__main__":
    scrape_bottom_of_the_hill()
