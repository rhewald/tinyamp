#!/usr/bin/env python3
"""
Enhanced Great American Music Hall scraper with improved event detection and error handling.
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

def scrape_gamh_events_enhanced():
    """Enhanced GAMH scraper with better event detection"""
    venue_name = "Great American Music Hall"
    events = []
    
    with EnhancedScraper() as scraper:
        # Navigate to the events page
        if not scraper.safe_navigate("https://gamh.com/", wait_for=".seetickets-list-event-container"):
            logger.error("Failed to load GAMH events page")
            return []
        
        # Try multiple selector strategies for events
        selectors_to_try = [
            ".seetickets-list-event-container",  # Current selector
            ".event-container",                  # Alternative
            ".event-item",                       # Generic
            "[class*='event']",                  # Any class containing 'event'
            ".list-event-container"              # Possible variation
        ]
        
        event_elements = []
        for selector in selectors_to_try:
            event_elements = scraper.safe_query_selector_all(selector)
            if event_elements:
                logger.info(f"Found {len(event_elements)} events using selector: {selector}")
                break
        
        if not event_elements:
            logger.error("No event elements found with any selector")
            save_debug_page(scraper, "gamh_debug.html")
            return []
        
        for i, event_element in enumerate(event_elements):
            try:
                event_data = extract_gamh_event_data(scraper, event_element, i)
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


def extract_gamh_event_data(scraper: EnhancedScraper, event_element, index: int) -> dict:
    """Extract event data from a single GAMH event element"""
    
    # Extract artist/title with multiple selector fallbacks
    artist_selectors = [
        "p.event-title a",
        ".event-title a",
        ".title a",
        "h1 a", "h2 a", "h3 a",
        "a[href*='event']",
        ".artist-name"
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
        logger.warning(f"No artist found for event {index}")
        return None
    
    # Extract date with multiple selector fallbacks
    date_selectors = [
        "p.event-date",
        ".event-date",
        ".date",
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
    
    # Enhanced date parsing for GAMH format
    normalized_date = parse_gamh_date(raw_date)
    if not normalized_date:
        logger.warning(f"Could not parse date '{raw_date}' for event: {artist}")
        return None
    
    # Extract time information
    time_selectors = [
        "p.doortime-showtime",
        ".doortime-showtime", 
        ".event-time",
        ".time",
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
            link = "https://gamh.com" + link
        else:
            link = "https://gamh.com/" + link
    
    return {
        "artist": artist.upper(),  # GAMH convention
        "date": normalized_date,
        "time": normalize_time_enhanced(raw_time),
        "venue": "Great American Music Hall",
        "link": link,
        "raw_date": raw_date,
        "raw_time": raw_time
    }


def parse_gamh_date(date_str: str) -> str:
    """Parse GAMH-specific date format like 'Thu May 1'"""
    if not date_str:
        return None
    
    try:
        # Split the date string
        parts = date_str.strip().split()
        if len(parts) >= 3:  # e.g., "Thu May 1"
            # Extract month and day
            month_str = parts[1]
            day_str = parts[2]
            
            # Convert month name to number
            from datetime import datetime
            month_num = datetime.strptime(month_str, "%b").month
            day_num = int(day_str)
            year = datetime.now().year
            
            # Create date object
            event_date = datetime(year, month_num, day_num)
            
            # If date is in the past, assume next year
            if event_date < datetime.now():
                event_date = event_date.replace(year=year + 1)
            
            return event_date.strftime("%Y-%m-%d")
    except Exception as e:
        logger.warning(f"Error parsing GAMH date '{date_str}': {e}")
    
    # Fallback to enhanced date normalization
    return normalize_date_enhanced(date_str, "GAMH")


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
    scrape_gamh_events_enhanced()