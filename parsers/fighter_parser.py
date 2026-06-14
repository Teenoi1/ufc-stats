"""Parser for fighter profile information."""

from typing import Optional
from bs4 import BeautifulSoup
import logging
import re

from models.fighter import FighterProfile, OverallStatistics
from parsers.stats_parser import StatsParser
from utils.helpers import (
    extract_text, safe_select, normalize_name, clean_text,
    parse_height, parse_weight, parse_reach
)
from utils.constants import (
    FIGHTER_NAME_SELECTOR,
    FIGHTER_RECORD_SELECTOR,
    FIGHTER_NICKNAME_SELECTOR,
    FIGHTER_STATS_ITEM_SELECTOR,
    FIGHTER_STATS_TITLE_SELECTOR
)

logger = logging.getLogger(__name__)


class FighterParser:
    """Parser for fighter profile data."""
    
    @staticmethod
    def parse_fighter_id(url: str) -> Optional[str]:
        """
        Extract fighter ID from URL.
        
        Args:
            url: Fighter profile URL
            
        Returns:
            Fighter ID or None
        """
        match = re.search(r"/fighter-details/([a-f0-9]+)/?$", url)
        return match.group(1) if match else None
    
    @staticmethod
    def parse_fighter_profile(html: str, fighter_id: Optional[str] = None) -> FighterProfile:
        """
        Parse fighter profile from HTML.
        
        Args:
            html: Fighter profile HTML
            fighter_id: Optional fighter ID (extracted from URL if not provided)
            
        Returns:
            FighterProfile object
        """
        soup = BeautifulSoup(html, "html.parser")
        profile = FighterProfile(fighter_id=fighter_id or "", name="")
        
        try:
            # Name
            name_elem = safe_select(soup, FIGHTER_NAME_SELECTOR)
            if name_elem:
                profile.name = normalize_name(extract_text(name_elem)) or ""
            
            # Record (e.g., "13-3-0")
            record_elem = safe_select(soup, FIGHTER_RECORD_SELECTOR)
            if record_elem:
                record_text = extract_text(record_elem)
                if record_text:
                    record_text = record_text.replace("Record:", "").strip()
                    profile.record = record_text
            
            # Nickname
            nickname_elem = safe_select(soup, FIGHTER_NICKNAME_SELECTOR)
            if nickname_elem:
                profile.nickname = normalize_name(extract_text(nickname_elem))
            
            # Other stats (Height, Weight, Reach, Stance, DOB)
            stat_items = soup.select(FIGHTER_STATS_ITEM_SELECTOR)
            
            for item in stat_items:
                title_elem = safe_select(item, FIGHTER_STATS_TITLE_SELECTOR)
                if not title_elem:
                    continue
                
                title_text = extract_text(title_elem, strip=True)
                if not title_text:
                    continue
                
                key = title_text.replace(":", "").strip().lower()
                
                value_text = extract_text(item, strip=True)
                if value_text:
                    value_text = value_text.replace(title_text, "").strip()
                
                if key == "height":
                    profile.height = parse_height(value_text)
                elif key == "weight":
                    profile.weight = parse_weight(value_text)
                elif key == "reach":
                    profile.reach = parse_reach(value_text)
                elif key == "stance":
                    profile.stance = clean_text(value_text)
                elif key == "dob" or key == "date of birth":
                    profile.dob = clean_text(value_text)
        
        except Exception as e:
            logger.error(f"Error parsing fighter profile: {e}")
        
        return profile
    
    @staticmethod
    def parse_full_fighter_data(html: str, fighter_id: Optional[str] = None) -> tuple:
        """
        Parse both profile and statistics from HTML.
        
        Args:
            html: Fighter profile HTML
            fighter_id: Optional fighter ID
            
        Returns:
            Tuple of (FighterProfile, OverallStatistics)
        """
        profile = FighterParser.parse_fighter_profile(html, fighter_id)
        stats = StatsParser.parse_career_statistics(html)
        
        return profile, stats
