from playwright.sync_api import sync_playwright
import requests
from datetime import datetime

def normalize_date(date_str):
    try:
        parts = date_str.strip().split()
        # Expected format: ['Thursday', 'May', '1', '2025']
        if len(parts) == 4:
            month = datetime.strptime(parts[1], "%B").month
            day = int(parts[2])
            year = int(parts[3])
            return datetime(year=year, month=month, day=day).strftime("%Y-%m-%d")
    except Exception as e:
        print(f"⚠️ Date normalization failed for '{date_str}': {e}")
    return None

def scrape_bottom_of_the_hill():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("⏳ Loading Bottom of the Hill page...")
        page.goto("https://www.bottomofthehill.com/calendar.html", timeout=60000)

        events = []
        event_blocks = page.query_selector_all("table#listings > tbody > tr")

        print(f"✅ Found {len(event_blocks)} rows (some may be empty or irrelevant)")

        current_date = None
        for row in event_blocks:
            date_el = row.query_selector("td.date span")
            artist_els = row.query_selector_all("td.big.band big.band")
            time_el = row.query_selector("td.time")

            if date_el:
                date_text = date_el.inner_text().strip()
                if date_text:
                    current_date = date_text  # Set current date for subsequent rows

            artists = [a.inner_text().strip() for a in artist_els if a.inner_text().strip()]
            artist_str = ", ".join(artists) if artists else None

            time_text = time_el.inner_text().strip() if time_el else None

            if artist_str and current_date:
                events.append({
                    "artist": artist_str.upper(),
                    "date": normalize_date(current_date),
                    "time": time_text or "TBA",
                    "venue": "Bottom of the Hill",
                    "link": "https://www.bottomofthehill.com/calendar.html"
                })
            else:
                print("⚠️ Skipping row due to missing artist or date")

        browser.close()
        print(events)

        # Optional POST to local backend
        try:
            response = requests.post("http://localhost:3001/api/events", json=events)
            print(f"POST status: {response.status_code}")
            print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to backend: {e}")

if __name__ == "__main__":
    scrape_bottom_of_the_hill()
