from playwright.sync_api import sync_playwright
import requests
from datetime import datetime

def normalize_date(date_str):
    try:
        # Expected: "Thursday May 1 2025"
        parts = date_str.strip().split()
        if len(parts) == 4:
            dt = datetime.strptime(" ".join(parts[1:]), "%B %d %Y")
            return dt.strftime("%Y-%m-%d")
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
        print(f"✅ Found {len(rows)} rows (some may be empty or irrelevant)")

        events = []
        current_date = None

        for row in rows:
            td = row.query_selector("td")
            if not td:
                continue

            # Look for date if it's present
            date_el = td.query_selector("span.date")
            if date_el:
                date_text = date_el.inner_text().strip()
                current_date = normalize_date(date_text)

            # Look for date in span.date
            date_el = td.query_selector("span.date")
            if date_el:
                date_text = date_el.inner_text().strip()
                current_date = normalize_date(date_text)

            # Gather all bands (headliner, supports, opener)
            band_els = td.query_selector_all("big.band")
            bands = [el.inner_text().strip() for el in band_els if el.inner_text().strip()]
            artist = ", ".join(bands)

            # Optional time
            time_el = td.query_selector("span.time")
            time = time_el.inner_text().strip() if time_el else "TBA"

            if current_date and artist:
                events.append({
                    "artist": artist.upper(),
                    "date": current_date,
                    "time": time,
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
            print(f"❌ POST failed: {e}")

if __name__ == "__main__":
    scrape_bottom_of_the_hill()
