from playwright.sync_api import sync_playwright
import requests
from datetime import datetime
import re

def normalize_date(text):
    try:
        # Extract a pattern like 'Thursday May 1 2025'
        match = re.search(r"\b\w+day\s+\w+\s+\d{1,2}\s+2025", text, re.IGNORECASE)
        if match:
            dt = datetime.strptime(match.group(), "%A %B %d %Y")
            return dt.strftime("%Y-%m-%d")
        else:
            print(f"❌ No date match found in: '{text}'")
    except Exception as e:
        print(f"❌ Date parse failed: '{text}' ({e})")
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
            html = block.inner_html()
            text = block.inner_text()

            # Date
            date_el = block.query_selector("span.date")
            if not date_el:
                print(f"⚠️ [Block {i}] No date found")
                continue
            date_text = date_el.inner_text().strip()
            print(f"📅 [Block {i}] Raw date: '{date_text}'")
            date = normalize_date(date_text)

            # Time (from text)
            time_lines = [line.strip() for line in text.splitlines() if "door" in line.lower() or "music" in line.lower()]
            show_time = time_lines[0] if time_lines else ""

            # Bands
            band_els = block.query_selector_all("big.band")
            artists = [el.inner_text().strip().upper() for el in band_els]
            if not artists:
                print(f"⚠️ [Block {i}] No artists found")
                continue

            # Combine artists into single string
            artist_string = ", ".join(artists)

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
