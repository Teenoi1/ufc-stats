"""Helper utilities for parsing and data processing."""

import re
from typing import Optional, List, Any, Dict
from datetime import datetime
from bs4 import Tag


def extract_text(element: Optional[Tag], selector: Optional[str] = None, strip: bool = True) -> Optional[str]:
    """
    Safely extract text from an element.
    
    Args:
        element: BeautifulSoup Tag object
        selector: CSS selector to find element within parent
        strip: Whether to strip whitespace
        
    Returns:
        Extracted text or None if element not found
    """
    if element is None:
        return None
    
    try:
        if selector:
            element = element.select_one(selector)
        
        if element is None:
            return None
        
        text = element.get_text(strip=strip)
        return text if text else None
    except Exception:
        return None


def safe_select(element: Optional[Tag], selector: str, index: int = 0) -> Optional[Tag]:
    """
    Safely select element with optional indexing.
    
    Args:
        element: BeautifulSoup Tag object
        selector: CSS selector
        index: Index of result to return
        
    Returns:
        Selected element or None if not found
    """
    if element is None:
        return None
    
    try:
        elements = element.select(selector)
        if len(elements) > index:
            return elements[index]
        return None
    except Exception:
        return None


def parse_percentage(text: Optional[str]) -> Optional[float]:
    """
    Extract percentage from text and return as numeric value.
    
    Args:
        text: Text containing percentage (e.g., "62%" or "62.5%")
        
    Returns:
        Percentage as float (0-100) or None if not found
    """
    if not text:
        return None
    
    match = re.search(r"(\d+(?:\.\d{1,2})?)\s*%", text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def parse_height(text: Optional[str]) -> Optional[float]:
    """
    Parse height from text and return as inches.
    
    Args:
        text: Height text (e.g., "6 4", "5'10\"", "6'4\"")
        
    Returns:
        Height in inches as float or None if not found
    """
    if not text:
        return None
    
    text = text.strip()
    
    # Try format: "6 4" (6 feet 4 inches)
    match = re.search(r"(\d+)\s+(\d+)", text)
    if match:
        try:
            feet = int(match.group(1))
            inches = int(match.group(2))
            return float(feet * 12 + inches)
        except (ValueError, TypeError):
            pass
    
    # Try format: "6'4\"" or "6'4"
    match = re.search(r"(\d+)['\s]+(\d+)", text)
    if match:
        try:
            feet = int(match.group(1))
            inches = int(match.group(2))
            return float(feet * 12 + inches)
        except (ValueError, TypeError):
            pass
    
    return None


def parse_weight(text: Optional[str]) -> Optional[float]:
    """
    Parse weight from text and return as lbs.
    
    Args:
        text: Weight text (e.g., "205 lbs", "205 lbs.", "205 lbs.‬")
        
    Returns:
        Weight in lbs as float or None if not found
    """
    if not text:
        return None
    
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lbs?|lb)", text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, TypeError):
            pass
    
    return None


def parse_reach(text: Optional[str]) -> Optional[float]:
    """
    Parse reach from text and return as inches.
    
    Args:
        text: Reach text (e.g., "79 in", "79 in.", "79\"")
        
    Returns:
        Reach in inches as float or None if not found
    """
    if not text:
        return None
    
    # Remove extra whitespace and special characters
    text = text.strip().rstrip('."‬')
    
    # Try to extract just the number
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, TypeError):
            pass
    
    return None


def parse_ratio(text: Optional[str]) -> Optional[Dict[str, int]]:
    """
    Parse ratio from text (e.g., "28 of 45" -> {"landed": 28, "attempted": 45}).
    
    Args:
        text: Text containing ratio
        
    Returns:
        Dictionary with 'landed' and 'attempted' keys or None
    """
    if not text:
        return None
    
    match = re.search(r"(\d+)\s*of\s*(\d+)", text)
    if match:
        return {
            "landed": int(match.group(1)),
            "attempted": int(match.group(2))
        }
    return None


def parse_ratio_str(text: Optional[str]) -> Optional[str]:
    """
    Extract ratio as string (e.g., "28 of 45").
    
    Args:
        text: Text containing ratio
        
    Returns:
        Ratio string or None if not found
    """
    if not text:
        return None
    
    match = re.search(r"(\d+)\s*of\s*(\d+)", text)
    if match:
        return f"{match.group(1)} of {match.group(2)}"
    return None


def parse_numeric(text: Optional[str]) -> Optional[float]:
    """
    Extract first numeric value from text.
    
    Args:
        text: Text containing number
        
    Returns:
        Float value or None if not found
    """
    if not text:
        return None
    
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def clean_text(text: Optional[str]) -> Optional[str]:
    """
    Clean text by removing quotes and extra whitespace.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text or None
    """
    if not text:
        return None
    
    return text.replace('"', '').replace("'", '').strip()


def normalize_name(name: Optional[str]) -> Optional[str]:
    """
    Normalize fighter name (strip and clean).
    
    Args:
        name: Fighter name
        
    Returns:
        Normalized name or None
    """
    if not name:
        return None
    
    return clean_text(name)


def normalize_date(date_str: Optional[str]) -> Optional[str]:
    """
    Normalize and validate date string.
    
    Args:
        date_str: Date string
        
    Returns:
        ISO format date string (YYYY-MM-DD) or None
    """
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    # Try common date formats
    formats = [
        "%B %d, %Y",  # January 01, 2023
        "%b. %d, %Y",  # Jan. 01, 2023
        "%m/%d/%Y",    # 01/01/2023
        "%Y-%m-%d",    # 2023-01-01
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return None


def extract_number(text: Optional[str]) -> Optional[int]:
    """
    Extract first integer from text.
    
    Args:
        text: Text containing number
        
    Returns:
        Integer value or None
    """
    if not text:
        return None
    
    match = re.search(r"(\d+)", text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def parse_time(time_str: Optional[str]) -> Optional[str]:
    """
    Validate and format time string (MM:SS format).
    
    Args:
        time_str: Time string
        
    Returns:
        Formatted time (MM:SS) or None
    """
    if not time_str:
        return None
    
    match = re.search(r"(\d+):(\d{2})", time_str)
    if match:
        return f"{match.group(1)}:{match.group(2)}"
    return None


def parse_table_by_headers(soup: Any, table_headers: List[str]) -> Optional[Any]:
    """
    Find table by headers instead of hardcoded index.
    
    Args:
        soup: BeautifulSoup object
        table_headers: List of header text to match
        
    Returns:
        Table element or None if not found
    """
    tables = soup.select("table")
    
    for table in tables:
        headers = [th.get_text(strip=True) for th in table.select("thead th")]
        
        # Check if any headers match
        if any(header in headers for header in table_headers):
            return table
    
    return None


def split_fighter_opponents(soup_tag: Any) -> tuple:
    """
    Split fighter and opponent data from a row with 2 fighters.
    
    Args:
        soup_tag: BeautifulSoup tag containing fighter data
        
    Returns:
        Tuple of (fighter_text, opponent_text)
    """
    paragraphs = soup_tag.select("p")
    
    fighter = clean_text(extract_text(paragraphs[0])) if len(paragraphs) > 0 else None
    opponent = clean_text(extract_text(paragraphs[1])) if len(paragraphs) > 1 else None
    
    return fighter, opponent
