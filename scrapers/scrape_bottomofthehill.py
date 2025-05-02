from playwright.sync_api import sync_playwright
import requests
from datetime import datetime

def normalize_date(date_str):
    try:
        parts = date_str.strip().split()
        # Expected: Thursday May 1 2025
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

        rows = page.query_selector_all("table#listings > tbody > tr")
        print(f"✅ Found {len(rows)} rows")

        events = []
        current_date = None

        for row in rows:
            # Date appears in span inside td with class="date"
            date_el = row.query_selector("td.date span")
            if date_el:
                current_date = date_el.inner_text().strip()  # Updates for this and following rows

            # Artist(s) are all <big class="band"> within td.big.band
            artist_els = row.query_selector_all("td.big.band big.band")
            artists = [el.inner_text().strip() for el in artist_els if el.inner_text().strip()]
            artist_str = ", ".join(artists) if artists else None

            # Doors/time (optional, fallback to TBA)
            time_el = row.query_selector("td.time")
            time_str = time_el.inner_text().strip() if time_el and time_el.inner_text().strip() else "TBA"

            if artist_str and current_date:
                events.append({
                    "artist": artist_str.upper(),
                    "date": normalize_date(current_date),
                    "time": time_str,
                    "venue": "Bottom of the Hill",
                    "link": "https://www.bottomofthehill.com/calendar.html"
                })
            else:
                print("⚠️ Skipping row due to missing artist or date")

        browser.close()
        print(events)

        try:
            response = requests.post("http://localhost:3001/api/events", json=events)
            print(f"POST status: {response.status_code}")
            print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to backend: {e}")

if __name__ == "__main__":
    scrape_bottom_of_the_hill()
