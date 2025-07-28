from playwright.sync_api import sync_playwright
import requests
from datetime import datetime
import re

def extract_date_from_text(text: str):
    """Extract a date like 'May 1 2025' from a text block."""
    match = re.search(r'([A-Z][a-z]+ \d{1,2},? 20\d{2})', text)
    if match:
        try:
            return datetime.strptime(match.group(1).replace(',', ''), "%B %d %Y").strftime("%Y-%m-%d")
        except:
            return None
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
            text = block.inner_text().strip()
            date = extract_date_from_text(text)

            # Extract artist(s)
            band_els = block.query_selector_all("big.band")
            artists = [el.inner_text().strip().upper() for el in band_els]
            artist_string = ", ".join(artists) if artists else ""

            # Extract time info
            time_lines = [line for line in text.splitlines() if "door" in line.lower() or "music" in line.lower()]
            show_time = time_lines[0].replace('\xa0', ' ').strip() if time_lines else ""

            # Only keep events with both date and artist
            if date and artist_string:
                print(f"📅 [Block {i}] Extracted date: {date}")
                print(f"✅ [Block {i}] Parsed event: {artist_string} on {date}")
                events.append({
                    "artist": artist_string,
                    "date": date,
                    "time": show_time,
                    "venue": "Bottom of the Hill",
                    "link": "https://www.bottomofthehill.com/calendar.html"
                })
            else:
                print(f"⚠️ [Block {i}] Skipping: Incomplete data — date: {date}, artist: {artist_string}, time: {show_time}")

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
