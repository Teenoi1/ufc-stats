"""Parser for fight details and statistics."""

from typing import Optional, Dict, List
from bs4 import BeautifulSoup, Tag
import logging
import re

from models.fight import (
    FightDetail, FightInfo, FighterStats, SignificantStrikesStats,
    RoundStats, JudgeScore
)
from utils.helpers import (
    extract_text, safe_select, parse_numeric, parse_ratio_str,
    parse_percentage, extract_number, normalize_name, parse_time,
    split_fighter_opponents
)

logger = logging.getLogger(__name__)


class FightParser:
    """Parser for fight detail data."""
    
    @staticmethod
    def parse_fight_id(url: str) -> Optional[str]:
        """
        Extract fight ID from URL.
        
        Args:
            url: Fight detail URL
            
        Returns:
            Fight ID or None
        """
        match = re.search(r"/fight-details/([a-f0-9]+)/?$", url)
        return match.group(1) if match else None
    
    @staticmethod
    def parse_fight_info(soup: BeautifulSoup) -> FightInfo:
        """
        Parse basic fight information.
        
        Args:
            soup: BeautifulSoup object of fight detail page
            
        Returns:
            FightInfo object
        """
        info = FightInfo()
        
        try:
            # Title
            title_elem = safe_select(soup, ".b-fight-details__fight-title")
            if title_elem:
                info.title = extract_text(title_elem)
            
            # Summary text
            summary_text = extract_text(
                safe_select(soup, ".b-fight-details__fight .b-fight-details__text")
            )
            
            if summary_text:
                # Extract method (KO/TKO, Decision - Unanimous, etc.)
                if "Method:" in summary_text:
                    method_part = summary_text.split("Method:")[1]
                    method_full = method_part.split("Round:")[0].strip() if "Round:" in method_part else ""
                    info.method = method_full if method_full else None
                
                # Extract round
                round_match = re.search(r"Round:\s*(\d+)", summary_text)
                if round_match:
                    info.round = int(round_match.group(1))
                
                # Extract time
                time_match = re.search(r"Time:\s*([\d:]+)", summary_text)
                if time_match:
                    info.time = parse_time(time_match.group(1))
                
                # Extract time format (without referee)
                format_match = re.search(r"Time format:\s*(.+?)(?:\s*Referee:|$)", summary_text)
                if format_match:
                    info.time_format = format_match.group(1).strip()
            
            # Referee
            referee_elem = soup.find(
                string=lambda x: x and "Referee:" in x
            )
            if referee_elem:
                span = referee_elem.parent.find_next("span")
                if span:
                    info.referee = extract_text(span)
            
            # Finish details
            detail_sections = soup.select(".b-fight-details__text")
            if len(detail_sections) > 1:
                details_text = extract_text(detail_sections[1])
                if details_text:
                    info.finish_details = details_text.replace("Details:", "").strip()
        
        except Exception as e:
            logger.error(f"Error parsing fight info: {e}")
        
        return info
    
    @staticmethod
    def parse_totals_table(soup: BeautifulSoup, fighter_name: Optional[str] = None,
                          opponent_name: Optional[str] = None) -> Optional[Dict[str, FighterStats]]:
        """
        Parse total stats table and ensure consistent fighter/opponent ordering.
        
        Args:
            soup: BeautifulSoup object
            fighter_name: Fighter name for consistent positioning
            opponent_name: Opponent name for consistent positioning
            
        Returns:
            Dictionary with 'fighter' and 'opponent' keys
        """
        try:
            tables = soup.select("table")
            if not tables:
                return None
            
            totals_table = tables[0]
            rows = totals_table.select("tbody tr")
            
            if len(rows) < 1:
                return None
            
            row = rows[0]
            cols = row.select("td")
            
            if len(cols) < 10:
                return None
            
            # Get fighter names from table
            name_col = cols[0]
            extracted_fighter, extracted_opponent = split_fighter_opponents(name_col)
            
            # Parse both sets of stats
            first_stats = FighterStats(
                name=extracted_fighter,
                kd=extract_number(extract_text(safe_select(cols[1], "p", 0))),
                sig_str=parse_ratio_str(extract_text(safe_select(cols[2], "p", 0))),
                sig_pct=parse_percentage(extract_text(safe_select(cols[3], "p", 0))),
                total_str=parse_ratio_str(extract_text(safe_select(cols[4], "p", 0))),
                td=parse_ratio_str(extract_text(safe_select(cols[5], "p", 0))),
                td_pct=parse_percentage(extract_text(safe_select(cols[6], "p", 0))),
                sub_att=extract_number(extract_text(safe_select(cols[7], "p", 0))),
                rev=extract_number(extract_text(safe_select(cols[8], "p", 0))),
                ctrl=extract_text(safe_select(cols[9], "p", 0)),
            )
            
            second_stats = FighterStats(
                name=extracted_opponent,
                kd=extract_number(extract_text(safe_select(cols[1], "p", 1))),
                sig_str=parse_ratio_str(extract_text(safe_select(cols[2], "p", 1))),
                sig_pct=parse_percentage(extract_text(safe_select(cols[3], "p", 1))),
                total_str=parse_ratio_str(extract_text(safe_select(cols[4], "p", 1))),
                td=parse_ratio_str(extract_text(safe_select(cols[5], "p", 1))),
                td_pct=parse_percentage(extract_text(safe_select(cols[6], "p", 1))),
                sub_att=extract_number(extract_text(safe_select(cols[7], "p", 1))),
                rev=extract_number(extract_text(safe_select(cols[8], "p", 1))),
                ctrl=extract_text(safe_select(cols[9], "p", 1)),
            )
            
            # Reorder to ensure fighter_name is always "fighter" if provided
            if fighter_name:
                fighter_name_normalized = normalize_name(fighter_name)
                extracted_fighter_normalized = normalize_name(extracted_fighter)
                extracted_opponent_normalized = normalize_name(extracted_opponent)

                if fighter_name_normalized and extracted_opponent_normalized == fighter_name_normalized:
                    # Swap them
                    first_stats, second_stats = second_stats, first_stats
            
            return {
                "fighter": first_stats,
                "opponent": second_stats
            }
        
        except Exception as e:
            logger.error(f"Error parsing totals table: {e}")
            return None
    
    @staticmethod
    def parse_significant_strikes_table(soup: BeautifulSoup, fighter_name: Optional[str] = None, opponent_name: Optional[str] = None) -> Optional[Dict[str, SignificantStrikesStats]]:
        """
        Parse significant strikes table.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary with 'fighter' and 'opponent' keys
        """
        try:
            tables = soup.select("table")
            if len(tables) < 3:
                return None
            
            sig_strikes_table = tables[2]
            rows = sig_strikes_table.select("tbody tr")
            
            if len(rows) < 1:
                return None
            
            row = rows[0]
            cols = row.select("td")
            
            if len(cols) < 9:
                return None
            
            # Get fighter names
            name_col = cols[0]
            fighter_name, opponent_name = split_fighter_opponents(name_col)
            
            # Parse fighter strikes
            fighter_strikes = SignificantStrikesStats(
                head=parse_ratio_str(extract_text(safe_select(cols[3], "p", 0))),
                body=parse_ratio_str(extract_text(safe_select(cols[4], "p", 0))),
                leg=parse_ratio_str(extract_text(safe_select(cols[5], "p", 0))),
                distance=parse_ratio_str(extract_text(safe_select(cols[6], "p", 0))),
                clinch=parse_ratio_str(extract_text(safe_select(cols[7], "p", 0))),
                ground=parse_ratio_str(extract_text(safe_select(cols[8], "p", 0))),
            )
            
            # Parse opponent strikes
            opponent_strikes = SignificantStrikesStats(
                head=parse_ratio_str(extract_text(safe_select(cols[3], "p", 1))),
                body=parse_ratio_str(extract_text(safe_select(cols[4], "p", 1))),
                leg=parse_ratio_str(extract_text(safe_select(cols[5], "p", 1))),
                distance=parse_ratio_str(extract_text(safe_select(cols[6], "p", 1))),
                clinch=parse_ratio_str(extract_text(safe_select(cols[7], "p", 1))),
                ground=parse_ratio_str(extract_text(safe_select(cols[8], "p", 1))),
            )
            
            return {
                "fighter": fighter_strikes,
                "opponent": opponent_strikes
            }
        
        except Exception as e:
            logger.error(f"Error parsing significant strikes table: {e}")
            return None
    
    @staticmethod
    def parse_round_stats_table(soup: BeautifulSoup, fighter_name: Optional[str] = None, 
                                opponent_name: Optional[str] = None) -> List[RoundStats]:
        """
        Parse round-by-round statistics.
        
        Args:
            soup: BeautifulSoup object
            fighter_name: Fighter name for reference
            opponent_name: Opponent name for reference
            
        Returns:
            List of RoundStats objects
        """
        round_stats_list: List[RoundStats] = []
        
        try:
            tables = soup.select("table")

            if len(tables) < 4:
                return round_stats_list
            
            # debug: print table headers to identify the correct one
            for idx, table in enumerate(tables):
                headers = [th.get_text(strip=True) for th in table.select("thead th")]
                print(f"\nTABLE {idx}")
                print(headers)

                first_row = table.select_one("tbody tr")
                if first_row:
                    print(
                        [td.get_text(" ", strip=True)
                        for td in first_row.select("td")]
                    )
            
            # Try to find round stats table by checking headers
            round_table = None
            for table in tables:
                headers = [th.get_text(strip=True) for th in table.select("thead th")]
                if any("round" in h.lower() for h in headers):
                    round_table = table
                    break
            
            if not round_table:
                return round_stats_list
            
            rows = round_table.select("tbody tr")
            
            for row in rows:
                cols = row.select("td")
                
                if len(cols) < 3:
                    continue
                
                try:
                    round_num = extract_number(extract_text(safe_select(cols[0], "p", 0)))
                    
                    # Get fighter name from first column if available
                    # fighter_col = extract_text(safe_select(cols[1], "p", 0))
                    # opponent_col = extract_text(safe_select(cols[1], "p", 1))
                    
                    fighter_sig_str = parse_ratio_str(extract_text(safe_select(cols[2], "p", 0)))
                    fighter_sig_pct = parse_percentage(extract_text(safe_select(cols[3], "p", 0))) if len(cols) > 3 else None
                    
                    opponent_sig_str = parse_ratio_str(extract_text(safe_select(cols[2], "p", 1)))
                    opponent_sig_pct = parse_percentage(extract_text(safe_select(cols[3], "p", 1))) if len(cols) > 3 else None
                    
                    round_stat = RoundStats(
                        round=round_num,
                        fighter=FighterStats(
                            name=fighter_name,
                            sig_str=fighter_sig_str,
                            sig_pct=fighter_sig_pct,
                        ),
                        opponent=FighterStats(
                            name=opponent_name,
                            sig_str=opponent_sig_str,
                            sig_pct=opponent_sig_pct,
                        ),
                    )
                    
                    round_stats_list.append(round_stat)
                
                except Exception as e:
                    logger.warning(f"Error parsing round {round_num}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing round stats table: {e}")
        
        return round_stats_list
    
    @staticmethod
    def parse_judges_scorecards(soup: BeautifulSoup) -> List[JudgeScore]:
        """
        Parse judge scorecards.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of JudgeScore objects
        """
        judges_list: List[JudgeScore] = []
        
        try:
            # Look for judge scores in text format
            text_content = soup.get_text()
            
            # Pattern: "Judge Name score-score" or similar
            judge_patterns = re.finditer(
                r"([A-Z][a-z]+ [A-Z][a-z']+ \d{1,2}-\d{1,2})",
                text_content
            )
            
            for match in judge_patterns:
                judge_text = match.group(1)
                # Split by last space-digit pattern
                score_match = re.search(r"(.+?)\s+(\d{1,2})-(\d{1,2})$", judge_text)
                
                if score_match:
                    judge_name = score_match.group(1).strip()
                    fighter_score = int(score_match.group(2))
                    opponent_score = int(score_match.group(3))
                    
                    judges_list.append(JudgeScore(
                        judge=judge_name,
                        fighter_score=fighter_score,
                        opponent_score=opponent_score
                    ))
            
            # Try finding in tables if text search found nothing
            if not judges_list:
                tables = soup.select("table")
                for table in tables:
                    headers = [th.get_text(strip=True) for th in table.select("thead th")]
                    if any("judge" in h.lower() for h in headers):
                        rows = table.select("tbody tr")
                        
                        for row in rows:
                            cols = row.select("td")
                            if len(cols) >= 3:
                                judge_name = extract_text(cols[0])
                                score_text = extract_text(cols[1])
                                
                                if judge_name and score_text:
                                    scores = re.findall(r"(\d{1,2})", score_text)
                                    if len(scores) >= 2:
                                        judges_list.append(JudgeScore(
                                            judge=judge_name,
                                            fighter_score=int(scores[0]),
                                            opponent_score=int(scores[1])
                                        ))
        
        except Exception as e:
            logger.error(f"Error parsing judges scorecards: {e}")
        
        return judges_list
    
    @staticmethod
    def parse_fight_detail(html: str, fighter_name: Optional[str] = None, 
                          opponent_name: Optional[str] = None) -> FightDetail:
        """
        Parse complete fight detail from HTML.
        
        Args:
            html: Fight detail page HTML
            fighter_name: Optional fighter name for reference and consistent positioning
            opponent_name: Optional opponent name for reference
            
        Returns:
            FightDetail object
        """
        soup = BeautifulSoup(html, "html.parser")
        detail = FightDetail()
        
        try:
            detail.fight_info = FightParser.parse_fight_info(soup)
            detail.totals = FightParser.parse_totals_table(soup, fighter_name, opponent_name)
            detail.significant_strikes = FightParser.parse_significant_strikes_table(soup, fighter_name, opponent_name)
            detail.round_by_round_stats = FightParser.parse_round_stats_table(
                soup, fighter_name, opponent_name
            )
            detail.judges_scorecards = FightParser.parse_judges_scorecards(soup)
        
        except Exception as e:
            logger.error(f"Error parsing fight detail: {e}")
        
        return detail
