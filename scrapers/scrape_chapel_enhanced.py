#!/usr/bin/env python3
"""
Enhanced Chapel SF scraper with improved event detection and error handling.
"""

import json
import sys
from enhanced_scraper_utils import (
    EnhancedScraper, 
    normalize_date_enhanced, 
    normalize_time_enhanced,
    insert_unique_events_enhanced,
    validate_event_data,
    logger
)

def scrape_chapel_events_enhanced():
    """Enhanced Chapel scraper with multiple selectors and better error handling"""
    venue_name = "The Chapel"
    events = []
    
    with EnhancedScraper() as scraper:
        # Navigate to the events page
        if not scraper.safe_navigate("https://thechapelsf.com/music/", wait_for=".event-info-block"):
            logger.error("Failed to load Chapel events page")
            return []
        
        # Try multiple selector strategies
        selectors_to_try = [
            ".event-info-block",  # Current selector
            ".event-item",        # Alternative
            ".event",             # Generic
            "[class*='event']",   # Any class containing 'event'
        ]
        
        event_elements = []
        for selector in selectors_to_try:
            event_elements = scraper.safe_query_selector_all(selector)
            if event_elements:
                logger.info(f"Found {len(event_elements)} events using selector: {selector}")
                break
        
        if not event_elements:
            logger.error("No event elements found with any selector")
            return []
        
        for i, event_element in enumerate(event_elements):
            try:
                event_data = extract_chapel_event_data(scraper, event_element, i)
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
    print(json.dumps(validated_events, indent=2))
    
    # Insert into database
    result = insert_unique_events_enhanced(validated_events, venue_name)
    print(f"\nDatabase result: {result}")
    
    return validated_events


def extract_chapel_event_data(scraper: EnhancedScraper, event_element, index: int) -> dict:
    """Extract event data from a single Chapel event element"""
    
    # Extract artist/title with multiple selector fallbacks
    artist_selectors = [
        "p.title a",
        ".title a", 
        "a[href*='event']",
        ".event-title",
        "h1", "h2", "h3",
        "strong a"
    ]
    
    artist = None
    link = None
    for selector in artist_selectors:
        title_element = event_element.query_selector(selector)
        if title_element:
            artist = scraper.extract_text_safe(title_element)
            link = scraper.extract_attribute_safe(title_element, "href")
            if artist:
                break
    
    if not artist:
        logger.warning(f"No artist found for event {index}")
        return None
    
    # Extract date with multiple selector fallbacks
    date_selectors = [
        "p.date",
        ".date",
        ".event-date", 
        "[class*='date']"
    ]
    
    raw_date = None
    for selector in date_selectors:
        date_element = event_element.query_selector(selector)
        if date_element:
            raw_date = scraper.extract_text_safe(date_element)
            if raw_date:
                break
    
    # Normalize date
    normalized_date = normalize_date_enhanced(raw_date, "The Chapel")
    if not normalized_date:
        logger.warning(f"Could not parse date '{raw_date}' for event: {artist}")
        return None
    
    # Extract time information with enhanced detection
    time_info = extract_chapel_time_info(event_element)
    
    # Ensure link is absolute
    if link and not link.startswith("http"):
        if link.startswith("/"):
            link = "https://thechapelsf.com" + link
        else:
            link = "https://thechapelsf.com/" + link
    
    return {
        "artist": artist,
        "date": normalized_date,
        "time": normalize_time_enhanced(time_info),
        "venue": "The Chapel",
        "link": link,
        "raw_date": raw_date,
        "raw_time": time_info
    }


def extract_chapel_time_info(event_element) -> str:
    """Extract time information with multiple strategies"""
    
    # Strategy 1: Look for explicit time elements
    time_selectors = [
        ".time",
        ".event-time",
        "[class*='time']",
        "p:has-text('Doors')",
        "p:has-text('Show')"
    ]
    
    for selector in time_selectors:
        try:
            time_element = event_element.query_selector(selector)
            if time_element:
                time_text = time_element.inner_text().strip()
                if time_text:
                    return time_text
        except:
            continue
    
    # Strategy 2: Look through all paragraph elements for time-related text
    try:
        paragraphs = event_element.query_selector_all("p")
        for p in paragraphs:
            text = p.inner_text().strip()
            if any(keyword in text.lower() for keyword in ["doors", "show", "time", "pm", "am"]):
                return text
    except:
        pass
    
    # Strategy 3: Look for any text containing time patterns
    try:
        full_text = event_element.inner_text()
        import re
        time_pattern = r'\d{1,2}:\d{2}\s*[ap]m|\d{1,2}\s*[ap]m|doors?\s+at|show\s+at'
        matches = re.findall(time_pattern, full_text, re.IGNORECASE)
        if matches:
            return matches[0]
    except:
        pass
    
    return ""


if __name__ == "__main__":
    scrape_chapel_events_enhanced()