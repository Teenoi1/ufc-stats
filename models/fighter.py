"""Data models for fighter information."""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any


@dataclass
class FighterProfile:
    """Fighter profile information."""
    fighter_id: str
    name: str
    nickname: Optional[str] = None
    record: Optional[str] = None
    height: Optional[float] = None  # Height in inches
    weight: Optional[float] = None  # Weight in lbs
    reach: Optional[float] = None  # Reach in inches
    stance: Optional[str] = None
    dob: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class OverallStatistics:
    """Overall career statistics."""
    slpm: Optional[float] = None
    strike_accuracy: Optional[float] = None  # As percentage (0-100)
    sapm: Optional[float] = None
    strike_defense: Optional[float] = None  # As percentage (0-100)
    td_avg: Optional[float] = None
    td_accuracy: Optional[float] = None  # As percentage (0-100)
    td_defense: Optional[float] = None  # As percentage (0-100)
    submission_avg: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}
