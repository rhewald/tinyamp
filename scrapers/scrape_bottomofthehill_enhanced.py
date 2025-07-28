#!/usr/bin/env python3
"""
Enhanced Bottom of the Hill scraper with improved event detection and error handling.
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

def scrape_bottomofthehill_events_enhanced():
    """Enhanced Bottom of the Hill scraper with better event detection"""
    venue_name = "Bottom of the Hill"
    events = []
    
    with EnhancedScraper() as scraper:
        # Navigate to the events page
        if not scraper.safe_navigate("https://www.bottomofthehill.com/calendar.html"):
            logger.error("Failed to load Bottom of the Hill events page")
            return []
        
        # Try multiple selector strategies for events
        selectors_to_try = [
            "td[style*='background-color: rgb(204, 204, 51)']",  # Current selector
            "td[style*='background-color']",                     # More general
            ".event-cell",                                       # Alternative
            "td:has(big.band)",                                  # Contains band info
            "td[bgcolor]"                                        # Any colored cell
        ]
        
        event_elements = []
        for selector in selectors_to_try:
            try:
                event_elements = scraper.safe_query_selector_all(selector)
                if event_elements:
                    logger.info(f"Found {len(event_elements)} events using selector: {selector}")
                    break
            except:
                continue
        
        if not event_elements:
            logger.error("No event elements found with any selector")
            save_debug_page(scraper, "bottomofthehill_debug.html")
            return []
        
        for i, event_element in enumerate(event_elements):
            try:
                event_data = extract_bottomofthehill_event_data(scraper, event_element, i)
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


def extract_bottomofthehill_event_data(scraper: EnhancedScraper, event_element, index: int) -> dict:
    """Extract event data from a single Bottom of the Hill event element"""
    
    # Get full text of the event cell
    full_text = scraper.extract_text_safe(event_element)
    if not full_text:
        return None
    
    # Extract date using multiple strategies
    date = extract_date_from_text_enhanced(full_text)
    if not date:
        logger.warning(f"Could not extract date from event {index}")
        return None
    
    # Extract artist names with multiple strategies
    artists = extract_artists_from_bottomofthehill(event_element, full_text)
    if not artists:
        logger.warning(f"Could not extract artists from event {index}")
        return None
    
    # Extract time information
    time_info = extract_time_from_text(full_text)
    
    return {
        "artist": ", ".join(artists),
        "date": date,
        "time": normalize_time_enhanced(time_info),
        "venue": "Bottom of the Hill",
        "link": "https://www.bottomofthehill.com/calendar.html",
        "raw_text": full_text,
        "raw_time": time_info
    }


def extract_date_from_text_enhanced(text: str) -> str:
    """Enhanced date extraction with multiple patterns"""
    
    # Multiple date patterns to try
    date_patterns = [
        (r'([A-Z][a-z]+ \d{1,2},? 20\d{2})', "%B %d, %Y"),      # "May 1, 2025"
        (r'([A-Z][a-z]+ \d{1,2} 20\d{2})', "%B %d %Y"),         # "May 1 2025"
        (r'(\d{1,2}/\d{1,2}/20\d{2})', "%m/%d/%Y"),             # "5/1/2025"
        (r'(\d{1,2}-\d{1,2}-20\d{2})', "%m-%d-%Y"),             # "5-1-2025"
    ]
    
    for pattern, date_format in date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            try:
                from datetime import datetime
                parsed_date = datetime.strptime(matches[0].replace(',', ''), date_format)
                return parsed_date.strftime("%Y-%m-%d")
            except:
                continue
    
    # Fallback to original pattern
    match = re.search(r'([A-Z][a-z]+ \d{1,2},? 20\d{2})', text)
    if match:
        try:
            from datetime import datetime
            parsed_date = datetime.strptime(match.group(1).replace(',', ''), "%B %d %Y")
            return parsed_date.strftime("%Y-%m-%d")
        except:
            pass
    
    return None


def extract_artists_from_bottomofthehill(event_element, full_text: str) -> list:
    """Extract artist names using multiple strategies"""
    
    artists = []
    
    # Strategy 1: Look for <big class="band"> elements
    try:
        band_elements = event_element.query_selector_all("big.band")
        for el in band_elements:
            artist_name = el.inner_text().strip().upper()
            if artist_name and len(artist_name) > 1:
                artists.append(artist_name)
    except:
        pass
    
    # Strategy 2: Look for any <big> elements
    if not artists:
        try:
            big_elements = event_element.query_selector_all("big")
            for el in big_elements:
                artist_name = el.inner_text().strip().upper()
                # Filter out obvious non-artist text
                if (artist_name and len(artist_name) > 1 and 
                    not any(word in artist_name.lower() for word in 
                           ['door', 'music', 'show', 'time', 'pm', 'am', 'sold', 'out'])):
                    artists.append(artist_name)
        except:
            pass
    
    # Strategy 3: Extract from text using patterns
    if not artists:
        # Look for lines that might be artist names (typically in ALL CAPS)
        lines = full_text.split('\n')
        for line in lines:
            line = line.strip()
            # Look for lines that are mostly uppercase and seem like band names
            if (len(line) > 2 and len(line) < 100 and 
                line.isupper() and 
                not any(word in line.lower() for word in 
                       ['door', 'music', 'show', 'time', 'sold', 'out', 'ticket'])):
                artists.append(line)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_artists = []
    for artist in artists:
        if artist not in seen:
            seen.add(artist)
            unique_artists.append(artist)
    
    return unique_artists


def extract_time_from_text(text: str) -> str:
    """Extract time information from event text"""
    
    # Look for door/show time patterns
    time_patterns = [
        r'door[s]?\s+at?\s+(\d{1,2}:\d{2}\s*[ap]m)',
        r'music\s+at?\s+(\d{1,2}:\d{2}\s*[ap]m)',
        r'show\s+at?\s+(\d{1,2}:\d{2}\s*[ap]m)',
        r'(\d{1,2}:\d{2}\s*[ap]m)',
    ]
    
    times_found = []
    for pattern in time_patterns:
        matches = re.findall(pattern, text.lower())
        times_found.extend(matches)
    
    if times_found:
        # Join multiple times found
        return " / ".join(times_found)
    
    return ""


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
    scrape_bottomofthehill_events_enhanced()