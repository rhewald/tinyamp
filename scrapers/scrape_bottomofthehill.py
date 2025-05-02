from playwright.sync_api import sync_playwright
import requests
from datetime import datetime
import re

def normalize_date(text):
    """Convert 'Thursday May 1 2025' → '2025-05-01'"""
    try:
        dt = datetime.strptime(text.replace(',', '').strip(), '%A %B %d %Y')
        return dt.strftime('%Y-%m-%d')
    except:
        return None

def scrape_bottom_of_the_hill():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("⏳ Loading Bottom of the Hill page...")
        page.goto("https://www.bottomofthehill.com/calendar.html", timeout=60000)
        
        rows = page.query_selector_all("table#listings > tbody > tr")
        print(f"✅ Found {len(rows)} rows (some may be empty or irrelevant)")

        events = []
        current_date = None

        for row in rows:
            td = row.query_selector("td")
            if not td:
                continue

            text = td.inner_text().strip()

            # Extract date if present
            date_match = re.search(r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) (\w+ \d{1,2})", text)
            if date_match:
                full_date = f"{date_match.group(0)} 2025"
                current_date = normalize_date(full_date)

            # Extract artists
            band_els = td.query_selector_all("big.band")
            artist = band_els[0].inner_text().strip().upper() if band_els else None

            # Extract time (look for 'doors' line)
            time_lines = [line.strip() for line in text.splitlines() if "door" in line.lower()]
            time = time_lines[0] if time_lines else ""

            if not artist or not current_date:
                print("⚠️ Skipping row due to missing artist or date")
                continue

            events.append({
                "artist": artist,
                "date": current_date,
                "time": time,
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
