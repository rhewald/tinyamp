from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=250)
    page = browser.new_page()
    page.goto("https://thechapelsf.com/music/", timeout=60000)
    page.wait_for_timeout(5000)

    html = page.content()

    with open("chapel_debug.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Saved page snapshot to chapel_debug.html")
    browser.close()
