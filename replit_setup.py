#!/usr/bin/env python3
"""
Replit Setup Script for Enhanced TinyAmp Scrapers
Run this script in your Replit environment to integrate the enhanced scrapers.
"""

import os
import shutil
import subprocess
import sys

def setup_enhanced_scrapers():
    """Set up enhanced scrapers in Replit environment"""
    
    print("🚀 Setting up Enhanced TinyAmp Scrapers for Replit...")
    
    # 1. Verify we're in the right directory
    if not os.path.exists("scrapers"):
        print("❌ Error: 'scrapers' directory not found. Please run this script from your tinyamp root directory.")
        return False
    
    # 2. Install additional dependencies if needed
    print("📦 Installing/updating dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "playwright", "pymongo", "python-dotenv", "requests"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not install some dependencies: {e}")
    
    # 3. Install Playwright browsers
    print("🌐 Installing Playwright browsers...")
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        print("✅ Playwright browsers installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not install Playwright browsers: {e}")
        print("   You may need to run: playwright install chromium")
    
    # 4. Backup original scrapers
    print("💾 Backing up original scrapers...")
    backup_files = [
        "scrapers/scrape_chapel.py",
        "scrapers/scrape_independent.py", 
        "scrapers/scrape_gamh.py",
        "scrapers/scrape_bottomofthehill.py"
    ]
    
    for file_path in backup_files:
        if os.path.exists(file_path):
            backup_path = file_path.replace(".py", "_original_backup.py")
            shutil.copy2(file_path, backup_path)
            print(f"   ✅ Backed up {file_path} -> {backup_path}")
    
    print("\n🎉 Setup complete! Your enhanced scrapers are ready to use.")
    print("\n📋 Next Steps:")
    print("1. Test individual scrapers:")
    print("   python scrapers/scrape_chapel.py")
    print("   python scrapers/scrape_independent.py")
    print("   python scrapers/scrape_gamh.py")
    print("   python scrapers/scrape_bottomofthehill.py")
    print("\n2. Run comprehensive scraping:")
    print("   python scrapers/run_all_scrapers_enhanced.py")
    print("\n3. Check results in the generated JSON files")
    
    return True

def create_replit_runner():
    """Create a simple runner script for Replit"""
    runner_content = '''#!/usr/bin/env python3
"""
Replit Runner for Enhanced TinyAmp Scrapers
"""

import os
import sys

# Add scrapers directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scrapers'))

def main():
    print("🎵 TinyAmp Enhanced Scrapers")
    print("=" * 40)
    print("1. Run all scrapers with analytics")
    print("2. Run individual venue scrapers")
    print("3. View last scraping results")
    print("=" * 40)
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\\n🚀 Running all enhanced scrapers...")
        try:
            from scrapers.run_all_scrapers_enhanced import run_all_scrapers_enhanced, analyze_scraping_results, save_comprehensive_results
            
            # Run all scrapers
            all_venue_events = run_all_scrapers_enhanced()
            
            # Analyze results
            analyze_scraping_results(all_venue_events)
            
            # Save results
            save_comprehensive_results(all_venue_events)
            
        except ImportError as e:
            print(f"❌ Error importing enhanced scrapers: {e}")
            print("Please run replit_setup.py first")
    
    elif choice == "2":
        print("\\n🏟️  Available venue scrapers:")
        print("1. The Chapel")
        print("2. The Independent") 
        print("3. Great American Music Hall")
        print("4. Bottom of the Hill")
        
        venue_choice = input("Enter venue number (1-4): ").strip()
        
        venue_map = {
            "1": ("The Chapel", "scrape_chapel"),
            "2": ("The Independent", "scrape_independent"),
            "3": ("Great American Music Hall", "scrape_gamh"), 
            "4": ("Bottom of the Hill", "scrape_bottomofthehill")
        }
        
        if venue_choice in venue_map:
            venue_name, module_name = venue_map[venue_choice]
            print(f"\\n🎯 Running {venue_name} scraper...")
            
            try:
                module = __import__(f"scrapers.{module_name}", fromlist=[module_name])
                if hasattr(module, 'scrape_chapel_events'):
                    module.scrape_chapel_events()
                elif hasattr(module, 'scrape_independent_events'):
                    module.scrape_independent_events()
                elif hasattr(module, 'scrape_gamh_events'):
                    module.scrape_gamh_events()
                elif hasattr(module, 'scrape_bottomofthehill_events'):
                    module.scrape_bottomofthehill_events()
                else:
                    print(f"❌ Could not find main function in {module_name}")
            except ImportError as e:
                print(f"❌ Error importing {module_name}: {e}")
        else:
            print("❌ Invalid choice")
    
    elif choice == "3":
        print("\\n📊 Last scraping results:")
        results_files = [
            "scrapers/scraping_summary.json",
            "scrapers/results_all_venues.json"
        ]
        
        for file_path in results_files:
            if os.path.exists(file_path):
                print(f"\\n📄 {file_path}:")
                with open(file_path, 'r') as f:
                    content = f.read()
                    if len(content) > 1000:
                        print(content[:1000] + "... (truncated)")
                    else:
                        print(content)
            else:
                print(f"❌ {file_path} not found. Run scrapers first.")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
'''
    
    with open("run_tinyamp.py", "w") as f:
        f.write(runner_content)
    
    print("✅ Created run_tinyamp.py - main runner for Replit")

if __name__ == "__main__":
    success = setup_enhanced_scrapers()
    if success:
        create_replit_runner()
        print("\n🎉 Replit setup complete!")
        print("   Run: python run_tinyamp.py to get started")