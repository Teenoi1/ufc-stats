"""Main UFC stats scraper orchestrator."""

import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path


from scraper.fighter_scraper import FighterScraper
from scraper.fight_scraper import FightScraper
from models.fighter import FighterProfile, OverallStatistics
from models.fight import FightHistory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UFCStatsScraper:
    """Main scraper orchestrator for UFC fighter data."""
    
    def __init__(self, headless: bool = True, timeout: int = 20, output_dir: str = "output"):
        """
        Initialize main scraper.
        
        Args:
            headless: Whether to run browser in headless mode
            timeout: Page load timeout in seconds
            output_dir: Output directory for JSON files
        """
        self.fighter_scraper = FighterScraper(headless=headless, timeout=timeout)
        self.fight_scraper = FightScraper(headless=headless, timeout=timeout)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def scrape_fighter_complete(self, fighter_id: str, 
                                include_fight_details: bool = True) -> Optional[Dict[str, Any]]:
        """
        Scrape complete fighter data including profile, stats, and fight history.
        
        Args:
            fighter_id: UFC fighter ID
            include_fight_details: Whether to scrape detailed stats for each fight
            
        Returns:
            Dictionary with complete fighter data or None if failed
        """
        logger.info(f"Starting complete fighter scrape: {fighter_id}")
        
        # Scrape fighter profile and stats
        result = self.fighter_scraper.scrape_fighter(fighter_id)
        if not result:
            logger.error(f"Failed to scrape fighter: {fighter_id}")
            return None
        
        profile, stats = result
        
        # Build initial data structure
        data = {
            "fighter_profile": profile.to_dict(),
            "overall_statistics": stats.to_dict(),
            "fight_history": []
        }
        
        # Get fighter profile HTML for fight history parsing
        fighter_url = f"http://ufcstats.com/fighter-details/{fighter_id}"
        html = self.fighter_scraper.browser.get_page(fighter_url, wait_condition="Stats | UFC")
        
        if html:
            # Scrape fight history
            if include_fight_details:
                fights = self.fight_scraper.scrape_fight_history_with_details(html, profile.name)
            else:
                fights = self.fight_scraper.scrape_fight_history(html, profile.name)
            
            data["fight_history"] = [fight.to_dict() for fight in fights]
            
            logger.info(f"Successfully scraped {len(fights)} fights for {profile.name}")
        
        return data
    
    def save_json(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Save data to JSON file.
        
        Args:
            data: Data to save
            filename: Optional filename (uses fighter name if not provided)
            
        Returns:
            Path to saved file
        """
        if not filename:
            fighter_name = data.get("fighter_profile", {}).get("name", "fighter")
            filename = fighter_name.replace(" ", "_") + ".json"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved to: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")
            raise
    
    def print_json(self, data: Dict[str, Any]) -> None:
        """
        Print formatted JSON to console.
        
        Args:
            data: Data to print
        """
        print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    """Main execution function."""
    # Example: Scrape Alex Pereira
    FIGHTER_ID = "e5549c82bfb5582d"  # Alex Pereira
    
    scraper = UFCStatsScraper(
        headless=False,  # Set to False to see browser
        timeout=20,
        output_dir="ufcstats_scraper/output"
    )
    
    try:
        # Scrape complete fighter data
        logger.info("Starting UFC stats scraper...")
        data = scraper.scrape_fighter_complete(
            fighter_id=FIGHTER_ID,
            include_fight_details=True
        )
        
        if data:
            # Print to console
            scraper.print_json(data)
            
            # Save to file
            filepath = scraper.save_json(data)
            logger.info(f"Scraping completed successfully!")
            logger.info(f"Output saved to: {filepath}")
        else:
            logger.error("Scraping failed")
    
    except Exception as e:
        logger.error(f"Error during scraping: {e}", exc_info=True)


if __name__ == "__main__":
    main()
