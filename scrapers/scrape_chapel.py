from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # run with UI
    page = browser.new_page()
    page.goto("https://thechapelsf.com/music/", timeout=60000)
    page.wait_for_load_state("networkidle")

    # Simulate manual scrolling
    for _ in range(10):
        page.mouse.wheel(0, 1000)
        time.sleep(0.5)

    # Save what was actually rendered
    with open("chapel_rendered_debug.html", "w") as f:
        f.write(page.content())

    print("✅ Saved chapel_rendered_debug.html")
    browser.close()
