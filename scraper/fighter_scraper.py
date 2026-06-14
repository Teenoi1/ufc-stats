"""Fighter profile scraper."""

from typing import Optional, Tuple
import logging

from scraper.browser import BrowserManager
from parsers.fighter_parser import FighterParser
from models.fighter import FighterProfile, OverallStatistics
from utils.constants import BASE_URL, WAIT_CONDITION

logger = logging.getLogger(__name__)


class FighterScraper:
    """Scraper for UFC fighter profiles."""
    
    def __init__(self, headless: bool = True, timeout: int = 20):
        """
        Initialize fighter scraper.
        
        Args:
            headless: Whether to run browser in headless mode
            timeout: Page load timeout in seconds
        """
        self.browser = BrowserManager(headless=headless, timeout=timeout)
        self.base_url = BASE_URL
    
    def scrape_fighter(self, fighter_id: str) -> Optional[Tuple[FighterProfile, OverallStatistics]]:
        """
        Scrape fighter profile and statistics.
        
        Args:
            fighter_id: UFC fighter ID
            
        Returns:
            Tuple of (FighterProfile, OverallStatistics) or None if failed
        """
        url = f"{self.base_url}/fighter-details/{fighter_id}"
        
        logger.info(f"Scraping fighter profile: {fighter_id}")
        
        html = self.browser.get_page(url, wait_condition=WAIT_CONDITION)
        if not html:
            logger.error(f"Failed to fetch fighter page: {url}")
            return None
        
        profile, stats = FighterParser.parse_full_fighter_data(html, fighter_id)
        
        logger.info(f"Successfully scraped fighter: {profile.name}")
        
        return profile, stats
