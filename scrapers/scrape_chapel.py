import json
from datetime import datetime
from playwright.sync_api import sync_playwright
from scraper_utils import insert_unique_events

def normalize_and_format_date(date_str):
    try:
        parsed = datetime.strptime(date_str, "%a %b %d")
        parsed = parsed.replace(year=2025)  # You can make this dynamic if needed
        return {
            "display": parsed.strftime("%a %b %d"),
            "sort": parsed.strftime("%Y-%m-%d")
        }
    except Exception as e:
        print(f"❌ Failed to parse date: {date_str} — {e}")
        return { "display": date_str, "sort": None }

def scrape_chapel_events():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://thechapelsf.com/music/", timeout=60000)
        page.wait_for_load_state("networkidle")

        event_items = page.query_selector_all(".event-info-block")
        print(f"Found {len(event_items)} events")

        events = []
        for item in event_items:
            title_el = item.query_selector("p.title a")
            date_el = item.query_selector("p.date")

            # Updated time extraction
            time_el = None
            paragraphs = item.query_selector_all("p")
            for p in paragraphs:
                text = p.inner_text().strip()
                if "Doors at" in text or "Show at" in text:
                    time_el = text
                    break

            link_el = title_el or item.query_selector("a")

            raw_date = date_el.inner_text().strip() if date_el else None
            normalized = normalize_and_format_date(raw_date)

            events.append({
                "artist": title_el.inner_text().strip() if title_el else None,
                "date": normalized["display"],
                "sortDate": normalized["sort"],
                "time": time_el,
                "venue": "The Chapel",
                "link": link_el.get_attribute("href") if link_el else None
            })

        browser.close()

    print(json.dumps(events, indent=2))
    insert_unique_events(events)

if __name__ == "__main__":
    scrape_chapel_events()
