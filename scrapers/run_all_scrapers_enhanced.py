#!/usr/bin/env python3
"""
Comprehensive scraper runner that executes all enhanced venue scrapers
and provides analytics on event collection performance.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any
from enhanced_scraper_utils import (
    create_comprehensive_event_list,
    logger
)

# Import all enhanced scrapers
from scrape_chapel_enhanced import scrape_chapel_events_enhanced
from scrape_independent_enhanced import scrape_independent_events_enhanced  
from scrape_gamh_enhanced import scrape_gamh_events_enhanced
from scrape_bottomofthehill_enhanced import scrape_bottomofthehill_events_enhanced

def run_all_scrapers_enhanced() -> Dict[str, List[Dict[str, Any]]]:
    """Run all enhanced scrapers and collect results"""
    
    logger.info("=== Starting Enhanced Venue Scraping ===")
    start_time = time.time()
    
    all_venue_events = {}
    scraper_functions = {
        "The Chapel": scrape_chapel_events_enhanced,
        "The Independent": scrape_independent_events_enhanced,
        "Great American Music Hall": scrape_gamh_events_enhanced,
        "Bottom of the Hill": scrape_bottomofthehill_events_enhanced,
    }
    
    for venue_name, scraper_func in scraper_functions.items():
        logger.info(f"\n--- Scraping {venue_name} ---")
        venue_start = time.time()
        
        try:
            events = scraper_func()
            all_venue_events[venue_name] = events or []
            venue_time = time.time() - venue_start
            logger.info(f"✅ {venue_name}: {len(all_venue_events[venue_name])} events in {venue_time:.1f}s")
            
        except Exception as e:
            logger.error(f"❌ {venue_name} failed: {e}")
            all_venue_events[venue_name] = []
            
        # Small delay between venues to be respectful
        time.sleep(2)
    
    total_time = time.time() - start_time
    logger.info(f"\n=== Scraping Complete in {total_time:.1f}s ===")
    
    return all_venue_events


def analyze_scraping_results(all_venue_events: Dict[str, List[Dict[str, Any]]]):
    """Provide detailed analytics on scraping results"""
    
    print("\n" + "="*60)
    print("           ENHANCED SCRAPING ANALYTICS")
    print("="*60)
    
    total_events = 0
    venue_stats = {}
    
    for venue, events in all_venue_events.items():
        event_count = len(events)
        total_events += event_count
        
        # Analyze event dates
        dates = []
        times_found = 0
        links_found = 0
        
        for event in events:
            if event.get('date'):
                try:
                    dates.append(datetime.strptime(event['date'], '%Y-%m-%d'))
                except:
                    pass
            if event.get('time'):
                times_found += 1
            if event.get('link'):
                links_found += 1
        
        venue_stats[venue] = {
            'total_events': event_count,
            'times_found': times_found,
            'links_found': links_found,
            'date_range': get_date_range(dates) if dates else "No valid dates"
        }
    
    # Print venue statistics
    for venue, stats in venue_stats.items():
        print(f"\n📍 {venue}:")
        print(f"   Events found: {stats['total_events']}")
        print(f"   Times found: {stats['times_found']}/{stats['total_events']} ({(stats['times_found']/max(stats['total_events'],1)*100):.1f}%)")
        print(f"   Links found: {stats['links_found']}/{stats['total_events']} ({(stats['links_found']/max(stats['total_events'],1)*100):.1f}%)")
        print(f"   Date range: {stats['date_range']}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total venues scraped: {len(all_venue_events)}")
    print(f"   Total events found: {total_events}")
    print(f"   Average events per venue: {total_events/len(all_venue_events):.1f}")
    
    # Check for potential issues
    check_for_issues(venue_stats)
    
    return venue_stats


def get_date_range(dates: List[datetime]) -> str:
    """Get the date range for a list of dates"""
    if not dates:
        return "No dates"
    
    min_date = min(dates)
    max_date = max(dates)
    
    if min_date.date() == max_date.date():
        return min_date.strftime("%Y-%m-%d")
    else:
        return f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"


def check_for_issues(venue_stats: Dict[str, Dict[str, Any]]):
    """Check for potential issues in scraping results"""
    
    print(f"\n🔍 ISSUE DETECTION:")
    issues_found = False
    
    for venue, stats in venue_stats.items():
        venue_issues = []
        
        # Check for low event count
        if stats['total_events'] < 5:
            venue_issues.append(f"Low event count ({stats['total_events']})")
        
        # Check for missing times
        if stats['total_events'] > 0 and stats['times_found'] / stats['total_events'] < 0.5:
            venue_issues.append(f"Many events missing times ({stats['times_found']}/{stats['total_events']})")
        
        # Check for missing links
        if stats['total_events'] > 0 and stats['links_found'] / stats['total_events'] < 0.5:
            venue_issues.append(f"Many events missing links ({stats['links_found']}/{stats['total_events']})")
        
        # Check for no events at all
        if stats['total_events'] == 0:
            venue_issues.append("No events found - scraper may be broken")
        
        if venue_issues:
            issues_found = True
            print(f"   ⚠️  {venue}: {', '.join(venue_issues)}")
    
    if not issues_found:
        print("   ✅ No issues detected!")


def save_comprehensive_results(all_venue_events: Dict[str, List[Dict[str, Any]]]):
    """Save all results to files for analysis"""
    
    # Create comprehensive event list
    all_events = create_comprehensive_event_list(all_venue_events)
    
    # Save individual venue results
    for venue, events in all_venue_events.items():
        safe_venue_name = venue.lower().replace(" ", "_").replace(".", "")
        filename = f"results_{safe_venue_name}.json"
        with open(filename, 'w') as f:
            json.dump(events, f, indent=2)
        logger.info(f"Saved {len(events)} events for {venue} to {filename}")
    
    # Save comprehensive results
    with open("results_all_venues.json", 'w') as f:
        json.dump(all_events, f, indent=2)
    logger.info(f"Saved {len(all_events)} total events to results_all_venues.json")
    
    # Save summary report
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    summary = {
        "scraping_timestamp": timestamp,
        "total_venues": len(all_venue_events),
        "total_events": len(all_events),
        "venues": {venue: len(events) for venue, events in all_venue_events.items()}
    }
    
    with open("scraping_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Results saved:")
    print(f"   - Individual venue files: results_*.json")
    print(f"   - All events: results_all_venues.json")
    print(f"   - Summary: scraping_summary.json")


if __name__ == "__main__":
    try:
        # Run all scrapers
        all_venue_events = run_all_scrapers_enhanced()
        
        # Analyze results
        analyze_scraping_results(all_venue_events)
        
        # Save results
        save_comprehensive_results(all_venue_events)
        
        print(f"\n🎉 Enhanced scraping complete!")
        
    except Exception as e:
        logger.error(f"Critical error in enhanced scraping: {e}")
        print(f"\n❌ Enhanced scraping failed: {e}")