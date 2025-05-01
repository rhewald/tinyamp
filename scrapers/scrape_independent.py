for block in event_blocks:
    # Updated selectors for title and detail link
    title_el = block.query_selector("div.tw-name a")
    time_el = block.query_selector("p.doortime-showtime")
    date_el = block.query_selector("p.fs-18.bold.mt-1r.date")

    artist = title_el.inner_text().strip() if title_el else None
    link = title_el.get_attribute("href") if title_el else None
    time = time_el.inner_text().strip() if time_el else None
    date = date_el.inner_text().strip() if date_el else None

    if link and not link.startswith("http"):
        link = "https://www.theindependentsf.com" + link

    events.append({
        "artist": artist,
        "date": date,
        "time": time,
        "venue": "The Independent",
        "link": link
    })
