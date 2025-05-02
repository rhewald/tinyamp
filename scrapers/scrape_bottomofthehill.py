from playwright.sync_api import sync_playwright
import requests
from datetime import datetime
import re

def normalize_date(text):
    try:
        return datetime.strptime(text.strip(), '%A %B %d %Y').strftime('%Y-%m-%d')
    except Exception:
        return None

def scrape_bottom_of_the_hill():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("⏳ Loading Bottom of the Hill page...")
        page.goto("https://www.bottomofthehill.com/calendar.html", timeout=60000)

        rows = page.query_selector_all("table#listings > tbody > tr")
        print(f"✅ Found {len(rows)} rows (some may be empty or irrelevant)\n")

        events = []
        current_date = None

        for i, row in enumerate(rows):
            td = row.query_selector("td")
            if not td:
                print(f"[Row {i}] ⛔ No <td> element found, skipping.\n")
                continue

            td_html = td.inner_html()
            td_text = td.inner_text()

            print(f"\n🔍 [Row {i}] --- RAW HTML START ---")
            print(td_html)
            print(f"--- RAW HTML END ---\n")

            print(f"[Row {i}] --- TEXT START ---")
            print(td_text)
            print(f"--- TEXT END ---\n")

            # Still try to get date
            date_el = td.query_selector("span.date")
            if date_el:
                date_text = date_el.inner_text().strip() + " 2025"
                current_date = normalize_date(date_text)
                print(f"[Row {i}] ✅ Date parsed: {current_date}")
            else:
                print(f"[Row {i}] ⚠️ No date element found")

            # Extract all band names from <big class="band">
            band_matches = re.findall(r'<big[^>]*class=["\']band["\'][^>]*>(.*?)</big>', td_html, re.IGNORECASE)
            band_names = [b.strip().upper() for b in band_matches]
            print(f"[Row {i}] 🎸 Bands found: {band_names}")

            # No filtering yet — we're collecting every row's results

        browser.close()

if __name__ == "__main__":
    scrape_bottom_of_the_hill()
