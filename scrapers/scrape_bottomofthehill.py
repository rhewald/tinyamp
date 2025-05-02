
from playwright.sync_api import sync_playwright
import requests
import re
from datetime import datetime

def normalize_date_from_img(src):
    try:
        match = re.search(r"/f/(\d{8})f\.jpg", src)
        if match:
            return datetime.strptime(match.group(1), "%Y%m%d").strftime("%Y-%m-%d")
    except Exception:
        pass
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
            img = block.query_selector("a > img")
            if not img:
                print(f"⚠️ [Block {i}] No image found for date")
                continue

            src = img.get_attribute("src")
            date = normalize_date_from_img(src)
            if not date:
                print(f"⚠️ [Block {i}] Could not parse date from image src")
                continue
            else:
                print(f"📅 [Block {i}] Extracted date from img: {date}")

            text = block.inner_text()
            time_lines = [line.strip() for line in text.splitlines() if "door" in line.lower() or "music" in line.lower()]
            show_time = time_lines[0] if time_lines else ""

            band_els = block.query_selector_all("big.band")
            artists = [el.inner_text().strip().upper() for el in band_els]
            if not artists:
                print(f"⚠️ [Block {i}] No artists found")
                continue

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
