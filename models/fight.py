"""Data models for fight information."""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List


@dataclass
class Opponent:
    """Opponent information."""
    fighter_id: Optional[str] = None
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Event:
    """Event information."""
    name: Optional[str] = None
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class FighterStats:
    """Stats for a single fighter."""
    name: Optional[str] = None
    kd: Optional[int] = None
    sig_str: Optional[str] = None
    sig_pct: Optional[float] = None  # As percentage (0-100)
    total_str: Optional[str] = None
    td: Optional[str] = None
    td_pct: Optional[float] = None  # As percentage (0-100)
    sub_att: Optional[int] = None
    rev: Optional[int] = None
    ctrl: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class SignificantStrikesStats:
    """Significant strikes breakdown."""
    head: Optional[str] = None
    body: Optional[str] = None
    leg: Optional[str] = None
    distance: Optional[str] = None
    clinch: Optional[str] = None
    ground: Optional[str] = None
    head_pct: Optional[float] = None  # Head percentage (0-100)
    body_pct: Optional[float] = None  # Body percentage (0-100)
    leg_pct: Optional[float] = None   # Leg percentage (0-100)
    distance_pct: Optional[float] = None  # Distance percentage (0-100)
    clinch_pct: Optional[float] = None  # Clinch percentage (0-100)
    ground_pct: Optional[float] = None  # Ground percentage (0-100)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class RoundStats:
    """Statistics for a single round."""
    round: Optional[int] = None
    fighter: Optional[FighterStats] = None
    opponent: Optional[FighterStats] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        data = {
            "round": self.round,
            "fighter": self.fighter.to_dict() if self.fighter else None,
            "opponent": self.opponent.to_dict() if self.opponent else None,
        }
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class JudgeScore:
    """Judge scorecard."""
    judge: Optional[str] = None
    fighter_score: Optional[int] = None
    opponent_score: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class FightInfo:
    """Basic fight information."""
    title: Optional[str] = None
    method: Optional[str] = None
    round: Optional[int] = None
    time: Optional[str] = None
    time_format: Optional[str] = None
    referee: Optional[str] = None
    finish_details: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class FightDetail:
    """Detailed fight statistics."""
    fight_info: Optional[FightInfo] = None
    totals: Optional[Dict[str, FighterStats]] = None
    significant_strikes: Optional[Dict[str, SignificantStrikesStats]] = None
    round_by_round_stats: List[RoundStats] = field(default_factory=list)
    judges_scorecards: List[JudgeScore] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        data = {
            "fight_info": self.fight_info.to_dict() if self.fight_info else None,
            "totals": {
                k: v.to_dict() if isinstance(v, FighterStats) else v 
                for k, v in self.totals.items()
            } if self.totals else None,
            "significant_strikes": {
                k: v.to_dict() if isinstance(v, SignificantStrikesStats) else v 
                for k, v in self.significant_strikes.items()
            } if self.significant_strikes else None,
            "round_by_round_stats": [r.to_dict() for r in self.round_by_round_stats],
            "judges_scorecards": [j.to_dict() for j in self.judges_scorecards],
        }
        return {k: v for k, v in data.items() if v is not None and (not isinstance(v, list) or v)}


@dataclass
class FightHistory:
    """Fight history entry."""
    fight_id: Optional[str] = None
    date: Optional[str] = None
    result: Optional[str] = None
    opponent: Optional[Opponent] = None
    event: Optional[Event] = None
    fight_detail: Optional[FightDetail] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        data = {
            "fight_id": self.fight_id,
            "date": self.date,
            "result": self.result,
            "opponent": self.opponent.to_dict() if self.opponent else None,
            "event": self.event.to_dict() if self.event else None,
            "fight_detail": self.fight_detail.to_dict() if self.fight_detail else None,
        }
        return {k: v for k, v in data.items() if v is not None}
