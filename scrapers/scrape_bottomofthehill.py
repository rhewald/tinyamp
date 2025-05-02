from playwright.sync_api import sync_playwright
import requests
from datetime import datetime

def normalize_date(text):
    """Convert 'Thursday May 1 2025' → '2025-05-01'"""
    try:
        dt = datetime.strptime(text.strip(), '%A %B %d %Y')
        return dt.strftime('%Y-%m-%d')
    except:
        return None

def scrape_bottom_of_the_hill():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("⏳ Loading Bottom of the Hill page...")
        page.goto("https://www.bottomofthehill.com/calendar.html", timeout=60000)

        rows = page.query_selector_all("table#listings tr")
        print(f"✅ Found {len(rows)} rows (some may be empty or irrelevant)")

        events = []
        current_date = None

        for row in rows:
            cell = row.query_selector("td[style*='background-color']")
            if not cell:
                continue

            text = cell.inner_text().strip()

            # Grab the date like "Thursday May 1 2025"
            date_el = cell.query_selector("span.date")
            if date_el:
                current_date = normalize_date(date_el.inner_text() + " 2025")

            # First band listed is headliner
            headliner_el = cell.query_selector("big.band")
            if not headliner_el or not current_date:
                print("⚠️ Skipping row due to missing artist or date")
                continue

            artist = headliner_el.inner_text().strip().upper()

            # Extract line with "door" or "music"
            time_lines = [line.strip() for line in text.splitlines() if "door" in line.lower() or "music" in line.lower()]
            time = time_lines[0] if time_lines else ""

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
