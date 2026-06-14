# UFC Stats Scraper

A web scraper for UFC fighter statistics, built with clean architecture principles, type hints, and comprehensive error handling.

## Features

- ✅ **Clean Architecture**: Separated concerns (models, parsers, scrapers, utils)
- ✅ **Type Hints**: Full type annotations throughout
- ✅ **Error Handling**: Comprehensive exception handling and logging
- ✅ **Resilient Parsing**: Parses tables by headers instead of hardcoded indexes
- ✅ **Helper Utilities**: Reusable parsing functions (ratios, percentages, dates, etc.)
- ✅ **Data Models**: Dataclasses with automatic JSON serialization
- ✅ **Structured Output**: Clean, nested JSON with semantic structure

## Project Structure

```
ufcstats_scraper/
├── main.py                 # Main orchestrator
├── models/
│   ├── fighter.py         # Fighter data models
│   └── fight.py           # Fight data models
├── parsers/
│   ├── fighter_parser.py  # Fighter profile parser
│   ├── fight_parser.py    # Fight detail parser
│   └── stats_parser.py    # Statistics parser
├── scraper/
│   ├── browser.py         # Browser management (Selenium)
│   ├── fighter_scraper.py # Fighter profile scraper
│   └── fight_scraper.py   # Fight history scraper
├── utils/
│   ├── helpers.py         # Utility functions
│   └── constants.py       # Constants and selectors
└── output/                # JSON output directory
```

## Data Models

### FighterProfile
```python
fighter_id: str
name: str
nickname: Optional[str]
record: Optional[str]
height: Optional[str]
weight: Optional[str]
reach: Optional[str]
stance: Optional[str]
dob: Optional[str]
```

### OverallStatistics
```python
slpm: Optional[float]
strike_accuracy: Optional[str]
sapm: Optional[float]
strike_defense: Optional[str]
td_avg: Optional[float]
td_accuracy: Optional[str]
td_defense: Optional[str]
submission_avg: Optional[float]
```

### FightHistory Entry
```python
fight_id: Optional[str]
date: Optional[str]
result: Optional[str]
opponent: Opponent
event: Event
fight_detail: FightDetail
```

## Usage

### Basic Usage

```python
from ufcstats_scraper.main import UFCStatsScraper

scraper = UFCStatsScraper(headless=True)

# Scrape complete fighter data
data = scraper.scrape_fighter_complete(
    fighter_id="e5549c82bfb5582d",  # Alex Pereira
    include_fight_details=True
)

# Save to JSON
scraper.save_json(data)
```

### Command Line

```bash
cd ufcstats_scraper
python main.py
```

## Output Format

```json
{
  "fighter_profile": {
    "fighter_id": "...",
    "name": "Alex Pereira",
    "nickname": "Poatan",
    "record": "13-3-0",
    "height": "6'4\"",
    "weight": "205 lbs",
    "reach": "79\"",
    "stance": "Orthodox"
  },
  "overall_statistics": {
    "slpm": 5.16,
    "strike_accuracy": "62%",
    "sapm": 3.50,
    "strike_defense": "53%",
    "td_avg": 0.11,
    "td_accuracy": "50%",
    "td_defense": "79%",
    "submission_avg": 0.2
  },
  "fight_history": [
    {
      "fight_id": "...",
      "date": "2025-10-04",
      "result": "Win",
      "opponent": {
        "fighter_id": "...",
        "name": "Magomed Ankalaev"
      },
      "event": {
        "name": "UFC 320",
        "url": "..."
      },
      "fight_detail": {
        "fight_info": {
          "title": "UFC Light Heavyweight Title Bout",
          "method": "KO/TKO",
          "round": 1,
          "time": "1:20",
          "time_format": "5 Rnd (5-5-5-5-5)",
          "referee": "Herb Dean",
          "finish_details": "Elbows to Head From Half Guard"
        },
        "totals": {
          "fighter": {
            "name": "Alex Pereira",
            "kd": 0,
            "sig_str": "28 of 45",
            "sig_pct": "62%",
            ...
          },
          "opponent": {...}
        },
        "significant_strikes": {...},
        "round_by_round_stats": [...],
        "judges_scorecards": [...]
      }
    }
  ]
}
```

## Key Improvements Over Previous Version

1. **Separated Concerns**: Models, parsers, scrapers, and utilities are in separate modules
2. **Type Hints**: All functions have proper type annotations
3. **Docstrings**: Comprehensive documentation for all functions
4. **Error Handling**: Try-except blocks with logging
5. **Dynamic Table Parsing**: Tables are identified by headers, not hardcoded indexes
6. **Helper Utilities**: Reusable functions for:
   - Text extraction and cleaning
   - Percentage parsing
   - Ratio parsing
   - Date normalization
   - Number extraction
   - Safe DOM navigation

7. **Data Models**: Dataclasses with:
   - Automatic serialization
   - Type validation
   - Clean dictionary conversion

8. **Logging**: Comprehensive logging for debugging and monitoring

9. **Resilience**: HTML structure changes are handled gracefully

## Requirements

- Python 3.8+
- selenium >= 4.0
- beautifulsoup4 >= 4.9

## Installation

```bash
pip install selenium beautifulsoup4
```

## Configuration

Edit `utils/constants.py` to customize:
- URLs and selectors
- Timeout values
- Career statistics fields

## Error Handling

All functions include error handling with logging. Check logs for:
- Failed page fetches
- Parsing errors
- Missing HTML elements
- Invalid data formats

## Future Enhancements

- [ ] Database storage (MongoDB/PostgreSQL)
- [ ] Rate limiting and retry logic
- [ ] Parallel scraping with ThreadPoolExecutor
- [ ] Caching with Redis
- [ ] API endpoints for data access
- [ ] More comprehensive testing suite

## License

Proprietary - Data Engineering Team
