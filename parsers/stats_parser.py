"""Parser for career statistics."""

from typing import Optional, Dict, Any
from bs4 import BeautifulSoup, Tag
import logging

from models.fighter import OverallStatistics
from utils.helpers import extract_text, safe_select, parse_numeric, parse_percentage
from utils.constants import FIGHTER_STATS_ITEM_SELECTOR, FIGHTER_STATS_TITLE_SELECTOR, CAREER_STATS

logger = logging.getLogger(__name__)


class StatsParser:
    """Parser for fighter statistics."""
    
    @staticmethod
    def parse_career_statistics(html: str) -> OverallStatistics:
        """
        Parse career statistics from fighter profile HTML.
        
        Args:
            html: Fighter profile HTML
            
        Returns:
            OverallStatistics object
        """
        soup = BeautifulSoup(html, "html.parser")
        stats = OverallStatistics()
        
        try:
            stat_items = soup.select(FIGHTER_STATS_ITEM_SELECTOR)
            
            for item in stat_items:
                title_elem = safe_select(item, FIGHTER_STATS_TITLE_SELECTOR)
                if not title_elem:
                    continue
                
                title_text = extract_text(title_elem, strip=True)
                if not title_text:
                    continue
                
                title_text = title_text.replace(":", "").strip()
                
                # Extract value
                value_text = extract_text(item, strip=True)
                if value_text:
                    value_text = value_text.replace(title_text, "").strip()
                
                # Parse statistics
                if title_text == "SLpM":
                    stats.slpm = parse_numeric(value_text)
                elif title_text == "Str. Acc.":
                    stats.strike_accuracy = parse_percentage(value_text)
                elif title_text == "SApM":
                    stats.sapm = parse_numeric(value_text)
                elif title_text == "Str. Def":
                    stats.strike_defense = parse_percentage(value_text)
                elif title_text == "TD Avg.":
                    stats.td_avg = parse_numeric(value_text)
                elif title_text == "TD Acc.":
                    stats.td_accuracy = parse_percentage(value_text)
                elif title_text == "TD Def.":
                    stats.td_defense = parse_percentage(value_text)
                elif title_text == "Sub. Avg.":
                    stats.submission_avg = parse_numeric(value_text)
        
        except Exception as e:
            logger.error(f"Error parsing career statistics: {e}")
        
        return stats
