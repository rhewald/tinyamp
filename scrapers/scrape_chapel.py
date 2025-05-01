from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://thechapelsf.com/music/", timeout=60000)
    page.wait_for_selector("#event-list")

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    events = soup.select("#event-list .event-item")  # Adjust this selector as needed

    for event in events:
        date = event.select_one(".event-date, .date")
        title = event.select_one(".event-title, h2")
        time = event.select_one(".event-time, .time")
        link = event.select_one("a")["href"] if event.select_one("a") else None

        print({
            "date": date.get_text(strip=True) if date else None,
            "artist": title.get_text(strip=True) if title else None,
            "time": time.get_text(strip=True) if time else None,
            "link": link
        })

    browser.close()
