from playwright.sync_api import sync_playwright
import requests
from datetime import datetime
import re

def extract_date_from_img_src(src: str):
    match = re.search(r'/f/(20\d{6})[a-z]*\.jpg', src)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y%m%d").strftime("%Y-%m-%d")
        except:
            return None
    return None

def extract_fallback_date(text: str):
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

        rows = page.query_selector_all("tr")
        print(f"✅ Found {len(rows)} table rows")

        events = []

        for i, row in enumerate(rows):
            tds = row.query_selector_all("td")
            if len(tds) < 3:
                continue

            block = tds[2]  # Only the third column (event info)
            style = block.get_attribute("style") or ""
            if "background-color: rgb(204, 204, 51)" not in style:
                continue

            text = block.inner_text().strip()
            img_el = block.query_selector("a[href$='.jpg'] > img")
            date = None

            if img_el:
                img_src = img_el.get_attribute("src")
                date = extract_date_from_img_src(img_src)
                if date:
                    print(f"📅 [Block {i}] Extracted date from img: {date}")
                else:
                    print(f"⚠️ [Block {i}] Image found but date couldn't be parsed")
            else:
                print(f"⚠️ [Block {i}] No image found for date")
                date = extract_fallback_date(text)
                if date:
                    print(f"📅 [Block {i}] Fallback date extracted from text: {date}")
                else:
                    print(f"⚠️ [Block {i}] Could not extract date")

            band_els = block.query_selector_all("big.band")
            artists = [el.inner_text().strip().upper() for el in band_els]
            if not artists:
                print(f"⚠️ [Block {i}] No artists found")
                continue

            artist_string = ", ".join(artists)

            time_lines = [line for line in text.splitlines() if "door" in line.lower() or "music" in line.lower()]
            show_time = time_lines[0].replace('\xa0', ' ').strip() if time_lines else ""

            events.append({
                "artist": artist_string,
                "date": date,
                "time": show_time,
                "venue": "Bottom of the Hill",
                "link": "https://www.bottomofthehill.com/calendar.html"
            })

            print(f"✅ [Block {i}] Parsed event: {artist_string} on {date}")

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
