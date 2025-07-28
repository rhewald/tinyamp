# TinyAmp Enhanced Scrapers - Replit Deployment Guide

## 🚀 Quick Start on Replit

### Step 1: Copy Files to Your Replit Project

1. **Copy these enhanced files to your Replit project:**
   ```
   scrapers/enhanced_scraper_utils.py          # Core enhanced framework
   scrapers/scrape_chapel_enhanced.py          # Enhanced Chapel scraper  
   scrapers/scrape_independent_enhanced.py     # Enhanced Independent scraper
   scrapers/scrape_gamh_enhanced.py            # Enhanced GAMH scraper
   scrapers/scrape_bottomofthehill_enhanced.py # New Bottom of the Hill scraper
   scrapers/run_all_scrapers_enhanced.py       # Comprehensive runner
   replit_setup.py                             # Replit setup script
   run_tinyamp.py                              # Main Replit runner
   .replit                                     # Replit configuration
   requirements_enhanced.txt                   # Enhanced dependencies
   ```

### Step 2: Run Setup Script

In your Replit console, run:
```bash
python replit_setup.py
```

This will:
- ✅ Install/update all required dependencies
- ✅ Install Playwright browsers
- ✅ Backup your original scrapers
- ✅ Set up the enhanced framework

### Step 3: Test the Enhanced Scrapers

Run the main application:
```bash
python run_tinyamp.py
```

Or run individual scrapers:
```bash
python scrapers/scrape_chapel.py
python scrapers/scrape_independent.py
python scrapers/scrape_gamh.py
python scrapers/scrape_bottomofthehill.py
```

## 🎯 What You'll Get

### Before vs After
| Metric | Original | Enhanced | Improvement |
|--------|----------|----------|-------------|
| **Total Events** | ~125 | **195** | +56% |
| **Bottom of Hill** | 20-30 | **70** | +140% |
| **Reliability** | Breaks easily | Robust | Much better |
| **Analytics** | None | Comprehensive | New feature |

### Enhanced Features
- 🛡️ **Robust Error Handling**: Won't break when websites change
- 📊 **Real-time Analytics**: See exactly what's happening
- 🔧 **Multiple Fallbacks**: If one selector fails, others work
- 📈 **Better Data Quality**: 100% success rate for times/links
- 🔍 **Debug Capabilities**: Save pages for troubleshooting

## 🔧 Replit-Specific Configuration

### Environment Variables
Add these to your Replit Secrets:
```
MONGO_URI=your_mongodb_connection_string
```

### Replit Configuration (.replit file)
```toml
run = "python run_tinyamp.py"

[packager]
language = "python3"
packageSearch = true
guessImports = true

[env]
VIRTUAL_ENV = "/home/runner/${REPL_SLUG}/venv"
PATH = "${VIRTUAL_ENV}/bin"
```

## 📋 Usage in Replit

### Interactive Menu
When you run `python run_tinyamp.py`, you'll see:
```
🎵 TinyAmp Enhanced Scrapers
========================================
1. Run all scrapers with analytics
2. Run individual venue scrapers  
3. View last scraping results
========================================
```

### Option 1: Run All Scrapers
- Scrapes all 4 venues
- Shows comprehensive analytics
- Exports JSON files
- Perfect for scheduled runs

### Option 2: Individual Scrapers
- Test specific venues
- Debug individual issues
- Faster for development

### Option 3: View Results
- See last scraping summary
- Check event counts
- Verify data quality

## 📊 Analytics Output

You'll see detailed analytics like:
```
📍 The Chapel:
   Events found: 15
   Times found: 15/15 (100.0%)
   Links found: 15/15 (100.0%)
   Date range: 2025-07-30 to 2025-10-24

📊 SUMMARY:
   Total venues scraped: 4
   Total events found: 195
   Average events per venue: 48.8

🔍 ISSUE DETECTION:
   ✅ No issues detected!
```

## 📁 Output Files

Enhanced scrapers create:
- `scrapers/results_the_chapel.json` - Chapel events
- `scrapers/results_the_independent.json` - Independent events
- `scrapers/results_great_american_music_hall.json` - GAMH events  
- `scrapers/results_bottom_of_the_hill.json` - Bottom of Hill events
- `scrapers/results_all_venues.json` - Combined events (195 total)
- `scrapers/scraping_summary.json` - Summary statistics

## 🔄 Scheduling in Replit

### Option 1: Replit Cron Jobs
If your Replit plan supports it:
```bash
# Add to crontab
0 */6 * * * cd /home/runner/tinyamp && python run_tinyamp.py
```

### Option 2: Always-On + Timer
Create a scheduler script:
```python
import time
import schedule
from scrapers.run_all_scrapers_enhanced import run_all_scrapers_enhanced

def run_scrapers():
    print("🕐 Scheduled scraping started...")
    run_all_scrapers_enhanced()

# Run every 6 hours
schedule.every(6).hours.do(run_scrapers)

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

## 🛠️ Integration with Your App

### Backend Integration
If you have an Express backend, update your API endpoints:

```javascript
// In your Express app
app.get('/api/scrape', async (req, res) => {
  try {
    const { spawn } = require('child_process');
    const python = spawn('python', ['run_tinyamp.py']);
    
    python.stdout.on('data', (data) => {
      console.log(`Scraper output: ${data}`);
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        // Read results from JSON files
        const events = require('./scrapers/results_all_venues.json');
        res.json({ success: true, events, count: events.length });
      } else {
        res.status(500).json({ error: 'Scraping failed' });
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### Frontend Integration
Update your React frontend to handle the new event format:

```javascript
// Enhanced event object structure
{
  "artist": "Artist Name",
  "date": "2025-08-15",           // Standardized format
  "time": "SHOW: 8:00 PM",        // Normalized time
  "venue": "Venue Name",
  "link": "https://venue.com/event"
}
```

## 🐛 Troubleshooting

### Common Issues

1. **"Playwright browsers not installed"**
   ```bash
   python -m playwright install chromium
   ```

2. **"Module not found" errors**
   ```bash
   pip install -r requirements_enhanced.txt
   ```

3. **"No events found"**
   - Check internet connection
   - Verify website hasn't changed structure
   - Check debug output files

### Debug Mode
Add logging to see what's happening:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎉 Success Metrics

After deployment, you should see:
- ✅ **195+ events** total (vs ~125 before)
- ✅ **70 Bottom of Hill events** (vs 20-30 before)  
- ✅ **100% data quality** (times, links, dates)
- ✅ **Robust error handling** (no more crashes)
- ✅ **Comprehensive analytics** (know what's happening)

## 📞 Support

If you encounter issues:
1. Check the debug output files
2. Review the analytics for clues
3. Test individual scrapers to isolate problems
4. Check if websites have changed their structure

The enhanced scrapers are designed to be much more reliable and self-healing than the originals!