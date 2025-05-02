from playwright.sync_api import sync_playwright
import requests
from datetime import datetime

def normalize_date(text):
    try:
        dt = datetime.strptime(text.replace('Thursday ', '').replace(',', '').strip(), '%B %d %Y')
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

            # Try to get the date
            date_el = td.query_selector("span.date")
            if date_el:
                date_text = date_el.inner_text().strip() + " 2025"
                current_date = normalize_date(date_text)

            # Try to get the headliner
            band_els = td.query_selector_all("big.band")
            if band_els:
                artist = band_els[0].inner_text().strip().upper()
            else:
                continue

            if not artist or not current_date:
                print("⚠️ Skipping row due to missing artist or date")
                continue

            # Extract time info (loosely)
            time_text = td.inner_text()
            time_lines = [line.strip() for line in time_text.splitlines() if "door" in line.lower()]
            show_time = time_lines[0] if time_lines else ""

            events.append({
                "artist": artist,
                "date": current_date,
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
