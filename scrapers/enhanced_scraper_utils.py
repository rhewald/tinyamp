import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from pymongo import MongoClient
from playwright.sync_api import sync_playwright, Page, Browser
import requests

# Load environment variables
load_dotenv(dotenv_path="../server/.env")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedScraper:
    """Enhanced scraper with better error handling and robustness"""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        
        # Set a realistic user agent
        self.page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def safe_navigate(self, url: str, wait_for: Optional[str] = None) -> bool:
        """Safely navigate to a URL with retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Navigating to {url} (attempt {attempt + 1})")
                self.page.goto(url, timeout=self.timeout)
                
                if wait_for:
                    self.page.wait_for_selector(wait_for, timeout=10000)
                else:
                    self.page.wait_for_load_state("networkidle", timeout=15000)
                
                time.sleep(2)  # Additional wait for dynamic content
                return True
                
            except Exception as e:
                logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to navigate to {url} after {max_retries} attempts")
                    return False
                time.sleep(5)  # Wait before retry
        
        return False
    
    def safe_query_selector_all(self, selector: str) -> List[Any]:
        """Safely query elements with multiple selector fallbacks"""
        try:
            elements = self.page.query_selector_all(selector)
            logger.info(f"Found {len(elements)} elements with selector: {selector}")
            return elements
        except Exception as e:
            logger.warning(f"Selector failed: {selector} - {e}")
            return []
    
    def extract_text_safe(self, element, default: str = "") -> str:
        """Safely extract text from an element"""
        try:
            if element:
                return element.inner_text().strip()
        except Exception as e:
            logger.warning(f"Text extraction failed: {e}")
        return default
    
    def extract_attribute_safe(self, element, attribute: str, default: str = "") -> str:
        """Safely extract an attribute from an element"""
        try:
            if element:
                return element.get_attribute(attribute) or default
        except Exception as e:
            logger.warning(f"Attribute extraction failed: {e}")
        return default


def normalize_date_enhanced(date_str: str, venue_context: str = "") -> Optional[str]:
    """Enhanced date normalization with better handling of different formats"""
    if not date_str:
        return None
    
    date_str = date_str.strip()
    current_year = datetime.now().year
    
    # Common date patterns
    patterns = [
        ("%a %b %d", "%Y-%m-%d"),  # "Fri Aug 29"
        ("%B %d", "%Y-%m-%d"),     # "August 29"
        ("%m.%d", "%Y-%m-%d"),     # "8.29"
        ("%m/%d", "%Y-%m-%d"),     # "8/29"
        ("%b %d", "%Y-%m-%d"),     # "Aug 29"
        ("%a, %b %d", "%Y-%m-%d"), # "Fri, Aug 29"
    ]
    
    for input_pattern, output_pattern in patterns:
        try:
            # Parse without year first
            parsed = datetime.strptime(date_str, input_pattern)
            # Add current year
            parsed = parsed.replace(year=current_year)
            
            # If date is in the past, assume next year
            if parsed < datetime.now():
                parsed = parsed.replace(year=current_year + 1)
            
            return parsed.strftime(output_pattern)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse date '{date_str}' for venue {venue_context}")
    return None


def normalize_time_enhanced(time_str: str) -> str:
    """Enhanced time normalization"""
    if not time_str:
        return ""
    
    time_str = time_str.strip()
    
    # Remove common prefixes
    prefixes_to_remove = ["SHOW:", "DOORS:", "STARTS:", "TIME:"]
    for prefix in prefixes_to_remove:
        time_str = time_str.replace(prefix, "").strip()
    
    # Handle 24-hour format conversion
    try:
        if ":" in time_str and len(time_str) <= 5 and time_str[0].isdigit():
            hour, minute = map(int, time_str.split(":"))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                dt = datetime.strptime(f"{hour}:{minute}", "%H:%M")
                return f"SHOW: {dt.strftime('%-I:%M %p')}"
    except:
        pass
    
    # Return formatted string
    if not time_str.upper().startswith("SHOW:"):
        return f"SHOW: {time_str.upper()}"
    return time_str.upper()


def insert_unique_events_enhanced(
    events: List[Dict[str, Any]], 
    venue_name: str,
    db_name: str = "tinyamp", 
    collection_name: str = "events"
) -> Dict[str, int]:
    """Enhanced event insertion with better duplicate detection and validation"""
    
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        logger.warning("MONGO_URI not set. Events will not be saved to database.")
        # Return mock results for testing
        return {"inserted": len(events), "skipped": 0, "errors": 0}
    
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        
        inserted = 0
        skipped = 0
        errors = 0
        
        for event in events:
            try:
                # Validate required fields
                if not all(event.get(field) for field in ["artist", "date", "venue"]):
                    logger.warning(f"Skipping event with missing required fields: {event}")
                    errors += 1
                    continue
                
                # Enhanced duplicate detection
                query = {
                    "artist": {"$regex": f"^{event['artist']}$", "$options": "i"},
                    "date": event["date"],
                    "venue": event["venue"]
                }
                
                if collection.find_one(query):
                    logger.info(f"Duplicate found, skipping: {event['artist']} @ {event['venue']} on {event['date']}")
                    skipped += 1
                else:
                    # Add metadata
                    event["scraped_at"] = datetime.now().isoformat()
                    event["scraper_version"] = "enhanced_v1.0"
                    
                    collection.insert_one(event)
                    logger.info(f"Inserted: {event['artist']} @ {event['venue']} on {event['date']}")
                    inserted += 1
                    
            except Exception as e:
                logger.error(f"Error processing event {event}: {e}")
                errors += 1
        
        logger.info(f"Venue {venue_name} - Inserted: {inserted}, Skipped: {skipped}, Errors: {errors}")
        client.close()
        
        return {"inserted": inserted, "skipped": skipped, "errors": errors}
        
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return {"inserted": 0, "skipped": 0, "errors": len(events)}


def validate_event_data(events: List[Dict[str, Any]], venue_name: str) -> List[Dict[str, Any]]:
    """Validate and clean event data"""
    valid_events = []
    
    for event in events:
        # Check required fields
        if not event.get("artist") or not event.get("date") or not event.get("venue"):
            logger.warning(f"Skipping invalid event from {venue_name}: {event}")
            continue
        
        # Clean artist name
        artist = event["artist"].strip()
        if len(artist) > 200:  # Suspiciously long artist name
            logger.warning(f"Suspiciously long artist name, truncating: {artist[:50]}...")
            artist = artist[:200]
        event["artist"] = artist
        
        # Validate date format
        date_str = event.get("date", "")
        if not date_str or len(date_str) < 8:
            logger.warning(f"Invalid date format: {date_str}")
            continue
        
        valid_events.append(event)
    
    logger.info(f"Validated {len(valid_events)} out of {len(events)} events for {venue_name}")
    return valid_events


def create_comprehensive_event_list(all_venue_events: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Combine events from multiple venues and remove duplicates"""
    all_events = []
    
    for venue, events in all_venue_events.items():
        logger.info(f"Processing {len(events)} events from {venue}")
        validated_events = validate_event_data(events, venue)
        all_events.extend(validated_events)
    
    # Sort by date
    def sort_key(event):
        try:
            return datetime.strptime(event["date"], "%Y-%m-%d")
        except:
            return datetime.now() + timedelta(days=365)  # Put unparseable dates at the end
    
    all_events.sort(key=sort_key)
    
    logger.info(f"Total events collected: {len(all_events)}")
    return all_events