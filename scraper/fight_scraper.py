"""Fight details scraper."""

from typing import Optional, List
from bs4 import BeautifulSoup
import logging
import re

from scraper.browser import BrowserManager
from parsers.fight_parser import FightParser
from models.fight import FightHistory, FightDetail, Opponent, Event
from utils.helpers import normalize_name, normalize_date, extract_text, safe_select
from utils.constants import BASE_URL, WAIT_CONDITION, FIGHT_ROW_SELECTOR

logger = logging.getLogger(__name__)


class FightScraper:
    """Scraper for UFC fight history and details."""
    
    def __init__(self, headless: bool = True, timeout: int = 20):
        """
        Initialize fight scraper.
        
        Args:
            headless: Whether to run browser in headless mode
            timeout: Page load timeout in seconds
        """
        self.browser = BrowserManager(headless=headless, timeout=timeout)
        self.base_url = BASE_URL
    
    def extract_fight_id(self, url: str) -> Optional[str]:
        """
        Extract fight ID from URL.
        
        Args:
            url: Fight detail URL
            
        Returns:
            Fight ID or None
        """
        match = re.search(r"/fight-details/([a-f0-9]+)", url)
        return match.group(1) if match else None
    
    def scrape_fight_history(self, html: str, fighter_name: Optional[str] = None) -> List[FightHistory]:
        """
        Parse fight history from fighter profile HTML.
        
        Args:
            html: Fighter profile HTML
            fighter_name: Fighter name for reference
            
        Returns:
            List of FightHistory objects
        """
        fights: List[FightHistory] = []
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            rows = soup.select(FIGHT_ROW_SELECTOR)
            
            logger.info(f"Found {len(rows)} fight rows")
            
            for row in rows:
                try:
                    fight_url = row.get("data-link")
                    if not fight_url:
                        continue
                    
                    cols = row.select("td")
                    if len(cols) < 10:
                        continue
                    
                    # Parse result
                    result_text = extract_text(safe_select(cols[0], "p", 0), strip=True)
                    if not result_text:
                        result_text = extract_text(cols[0], strip=True)
                    result = result_text.strip() if result_text else None
                    
                    # Parse opponent
                    opponent_name_elem = safe_select(cols[1], "p", 1)
                    opponent_name = normalize_name(extract_text(opponent_name_elem))
                    
                    # Parse date
                    date_elem = safe_select(cols[6], "p", 1)
                    date = normalize_date(extract_text(date_elem))
                    
                    # Parse event
                    event_elem = safe_select(cols[6], "a")
                    event_name = extract_text(event_elem) if event_elem else None
                    
                    # Build fight object
                    fight = FightHistory(
                        fight_id=self.extract_fight_id(fight_url),
                        date=date,
                        result=result,
                        opponent=Opponent(
                            fighter_id=None,  # Would need separate lookup
                            name=opponent_name
                        ),
                        event=Event(
                            name=event_name,
                            url=fight_url
                        ),
                    )
                    
                    fights.append(fight)
                
                except Exception as e:
                    logger.warning(f"Error parsing fight row: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing fight history: {e}")
        
        return fights
    
    def scrape_fight_details(self, fight_url: str, fighter_name: Optional[str] = None,
                             opponent_name: Optional[str] = None) -> Optional[FightDetail]:
        """
        Scrape detailed fight statistics.
        
        Args:
            fight_url: Fight detail URL
            fighter_name: Fighter name for reference
            opponent_name: Opponent name for reference
            
        Returns:
            FightDetail object or None if failed
        """
        logger.info(f"Scraping fight details: {fight_url}")
        
        html = self.browser.get_page(fight_url, wait_condition=WAIT_CONDITION)
        if not html:
            logger.error(f"Failed to fetch fight page: {fight_url}")
            return None
        
        detail = FightParser.parse_fight_detail(html, fighter_name, opponent_name)
        
        logger.info("Successfully scraped fight details")
        
        return detail
    
    def scrape_fight_history_with_details(self, fighter_html: str, fighter_name: Optional[str] = None) -> List[FightHistory]:
        """
        Scrape fight history with full details for each fight.
        
        Args:
            fighter_html: Fighter profile HTML
            fighter_name: Fighter name for reference
            
        Returns:
            List of FightHistory objects with full details
        """
        fights = self.scrape_fight_history(fighter_html, fighter_name)
        
        for fight in fights:
            if fight.event and fight.event.url:
                try:
                    fight.fight_detail = self.scrape_fight_details(
                        fight.event.url,
                        fighter_name,
                        fight.opponent.name if fight.opponent else None
                    )
                except Exception as e:
                    logger.error(f"Failed to scrape fight details for {fight.event.url}: {e}")
                    fight.fight_detail = None
        
        return fights
