"""Constants and configuration for UFC stats scraping."""

# UFC Stats URLs
BASE_URL = "http://ufcstats.com"
FIGHTER_URL_PATTERN = f"{BASE_URL}/fighter-details/{{fighter_id}}"
FIGHT_URL_PATTERN = f"{BASE_URL}/fight-details/{{fight_id}}"

# CSS Selectors
FIGHTER_NAME_SELECTOR = ".b-content__title-highlight"
FIGHTER_RECORD_SELECTOR = ".b-content__title-record"
FIGHTER_NICKNAME_SELECTOR = ".b-content__Nickname"
FIGHTER_STATS_ITEM_SELECTOR = "li.b-list__box-list-item_type_block"
FIGHTER_STATS_TITLE_SELECTOR = ".b-list__box-item-title"

# Fight History
FIGHT_ROW_SELECTOR = "tr.js-fight-details-click"
FIGHT_DETAIL_TITLE_SELECTOR = ".b-fight-details__fight-title"
FIGHT_DETAIL_TEXT_SELECTOR = ".b-fight-details__fight .b-fight-details__text"

# Table selectors
TABLE_SELECTOR = "table"
TABLE_BODY_SELECTOR = "tbody tr"
TABLE_HEADER_SELECTOR = "thead th"

# Career Statistics Keys
CAREER_STATS = [
    "SLpM",
    "Str. Acc.",
    "SApM",
    "Str. Def",
    "TD Avg.",
    "TD Acc.",
    "TD Def.",
    "Sub. Avg."
]

# Wait conditions
WAIT_TIMEOUT = 20
WAIT_CONDITION = "Stats | UFC"

# Parsing patterns
PERCENTAGE_PATTERN = r"(\d+(?:\.\d{1,2})?)\s*%"
RATIO_PATTERN = r"(\d+)\s*of\s*(\d+)"
