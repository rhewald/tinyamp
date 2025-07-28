#!/usr/bin/env python3
"""
Enhanced Independent SF scraper with improved event detection and error handling.
"""

import json
import re
from enhanced_scraper_utils import (
    EnhancedScraper, 
    normalize_date_enhanced, 
    normalize_time_enhanced,
    insert_unique_events_enhanced,
    validate_event_data,
    logger
)

def scrape_independent_events_enhanced():
    """Enhanced Independent scraper with better popup handling and event detection"""
    venue_name = "The Independent"
    events = []
    
    with EnhancedScraper() as scraper:
        # Navigate to the events page
        if not scraper.safe_navigate("https://www.theindependentsf.com/", wait_for=".tw-event-item"):
            logger.error("Failed to load Independent events page")
            return []
        
        # Handle popup with multiple strategies
        handle_popup(scraper)
        
        # Try multiple selector strategies for events
        selectors_to_try = [
            ".tw-event-item",     # Current selector
            ".event-item",        # Alternative
            ".event",             # Generic
            "[class*='event']",   # Any class containing 'event'
            ".tw-item"            # Possible variation
        ]
        
        event_elements = []
        for selector in selectors_to_try:
            event_elements = scraper.safe_query_selector_all(selector)
            if event_elements:
                logger.info(f"Found {len(event_elements)} events using selector: {selector}")
                break
        
        if not event_elements:
            logger.error("No event elements found with any selector")
            # Save page content for debugging
            save_debug_page(scraper, "independent_debug.html")
            return []
        
        for i, event_element in enumerate(event_elements):
            try:
                event_data = extract_independent_event_data(scraper, event_element, i)
                if event_data:
                    events.append(event_data)
            except Exception as e:
                logger.warning(f"Failed to extract data from event {i}: {e}")
                continue
    
    # Validate and clean events
    validated_events = validate_event_data(events, venue_name)
    
    # Print results
    print(f"\n=== {venue_name} Events ===")
    print(f"Raw events found: {len(events)}")
    print(f"Valid events: {len(validated_events)}")
    print(json.dumps(validated_events[:5], indent=2))  # Show first 5 for brevity
    print(f"... and {len(validated_events) - 5} more events" if len(validated_events) > 5 else "")
    
    # Insert into database
    result = insert_unique_events_enhanced(validated_events, venue_name)
    print(f"\nDatabase result: {result}")
    
    return validated_events


def handle_popup(scraper: EnhancedScraper):
    """Handle potential popups with multiple strategies"""
    popup_selectors = [
        "div#om-mnuwxyw8zcuetb2b-holder .om-close",
        ".popup-close",
        ".modal-close",
        "[class*='close']",
        ".om-close"
    ]
    
    for selector in popup_selectors:
        try:
            popup = scraper.page.query_selector(selector)
            if popup:
                popup.click()
                logger.info(f"Closed popup using selector: {selector}")
                scraper.page.wait_for_timeout(1000)  # Wait for popup to close
                return
        except:
            continue
    
    logger.info("No popup found or popup already closed")


def extract_independent_event_data(scraper: EnhancedScraper, event_element, index: int) -> dict:
    """Extract event data from a single Independent event element"""
    
    # Extract artist/title with multiple selector fallbacks
    artist_selectors = [
        "div.tw-name > a",
        ".tw-name a",
        ".event-name a",
        ".artist-name",
        "h1 a", "h2 a", "h3 a",
        "a[href*='event']",
        "a[href*='tm-event']"
    ]
    
    artist = None
    link = None
    for selector in artist_selectors:
        try:
            artist_element = event_element.query_selector(selector)
            if artist_element:
                artist = scraper.extract_text_safe(artist_element)
                link = scraper.extract_attribute_safe(artist_element, "href")
                if artist:
                    break
        except:
            continue
    
    if not artist:
        # Fallback: try to extract from any link in the element
        try:
            links = event_element.query_selector_all("a")
            for link_el in links:
                text = scraper.extract_text_safe(link_el)
                href = scraper.extract_attribute_safe(link_el, "href")
                if text and len(text) > 3 and "event" in href:
                    artist = text
                    link = href
                    break
        except:
            pass
    
    if not artist:
        logger.warning(f"No artist found for event {index}")
        return None
    
    # Extract date with multiple selector fallbacks
    date_selectors = [
        "span.tw-event-date",
        ".tw-date",
        ".event-date",
        "[class*='date']"
    ]
    
    raw_date = None
    for selector in date_selectors:
        try:
            date_element = event_element.query_selector(selector)
            if date_element:
                raw_date = scraper.extract_text_safe(date_element)
                if raw_date:
                    break
        except:
            continue
    
    # Enhanced date extraction from text if selectors fail
    if not raw_date:
        try:
            full_text = event_element.inner_text()
            # Look for date patterns in the text
            date_patterns = [
                r'\d{1,2}\.\d{1,2}',  # 8.29
                r'\d{1,2}/\d{1,2}',   # 8/29
                r'[A-Z][a-z]{2}\s+\d{1,2}',  # Aug 29
            ]
            for pattern in date_patterns:
                match = re.search(pattern, full_text)
                if match:
                    raw_date = match.group()
                    break
        except:
            pass
    
    # Normalize date
    normalized_date = normalize_date_enhanced(raw_date, "The Independent")
    if not normalized_date:
        logger.warning(f"Could not parse date '{raw_date}' for event: {artist}")
        return None
    
    # Extract time information
    time_selectors = [
        "span.tw-event-time-complete",
        ".tw-time",
        ".event-time",
        "[class*='time']"
    ]
    
    raw_time = None
    for selector in time_selectors:
        try:
            time_element = event_element.query_selector(selector)
            if time_element:
                raw_time = scraper.extract_text_safe(time_element)
                if raw_time:
                    break
        except:
            continue
    
    # Ensure link is absolute
    if link and not link.startswith("http"):
        if link.startswith("/"):
            link = "https://www.theindependentsf.com" + link
        else:
            link = "https://www.theindependentsf.com/" + link
    
    return {
        "artist": artist,
        "date": normalized_date,
        "time": normalize_time_enhanced(raw_time),
        "venue": "The Independent",
        "link": link,
        "raw_date": raw_date,
        "raw_time": raw_time
    }


def save_debug_page(scraper: EnhancedScraper, filename: str):
    """Save page content for debugging"""
    try:
        content = scraper.page.content()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Saved debug page content to {filename}")
    except Exception as e:
        logger.warning(f"Failed to save debug page: {e}")


if __name__ == "__main__":
    scrape_independent_events_enhanced()