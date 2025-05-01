import json
import requests
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Turn off headless for now
    page = browser.new_page()
    page.goto("https://www.theindependentsf.com/", timeout=90000)

    # Wait longer and for a higher-level container that we know exists
    page.wait_for_selector("div#tw-upcoming-upcoming-event-list", timeout=60000)

    container_html = page.query_selector("div#tw-upcoming-upcoming-event-list").inner_html()
    print("=== DEBUG: Raw Inner HTML of event container ===")
    print(container_html[:3000])  # print first part only for sanity
    print("=== END ===")

    browser.close()
