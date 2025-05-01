import json
import requests
import time
from playwright.sync_api import sync_playwright

def auto_scroll(page):
    page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 300;
                const timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    totalHeight += distance;

                    if (totalHeight >= document.body.scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 200);
            });
        }
    """)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://thechapelsf.com/music/", timeout=60000)
    page.wait_for_load_state("networkidle")
    auto_scroll(page)
    time.sleep(2)  # wait briefly for JS-inserted content

    # Save rendered HTML
    with open("chapel_rendered_debug.html", "w") as f:
        f.write(page.content())

    # Parse shows after scroll
    event_items = page.query_selector_all("div.show")
    print(f"Found {len(event_items)} events")

    events = []
    for item in event_items:
        date = item.query_selector(".event-date") or item.query_selector(".date")
        title = item.query_selector(".event-title") or item.query_selector("h2")
        time_el = item.query_selector(".event-time") or item.query_selector(".time")
        link = item.query_selector("a")

        events.append({
            "date": date.inner_text().strip() if date else None,
            "artist": title.inner_text().strip() if title else None,
            "time": time_el.inner_text().strip() if time_el else None,
            "venue": "The Chapel",
            "link": link.get_attribute("href") if link else None
        })

    browser.close()

# Output
print(json.dumps(events, indent=2))

# Post to your API
try:
    response = requests.post("http://localhost:5000/api/ingest", json=events)
    print("POST status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Failed to POST:", str(e))
