"""Browser and HTTP handling for web scraping."""

from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages browser instances for web scraping."""
    
    def __init__(self, headless: bool = True, timeout: int = 20):
        """
        Initialize browser manager.
        
        Args:
            headless: Whether to run browser in headless mode
            timeout: Timeout for page loads in seconds
        """
        self.headless = headless
        self.timeout = timeout
        self.driver: Optional[webdriver.Chrome] = None
    
    def create_driver(self) -> webdriver.Chrome:
        """
        Create and configure Chrome driver.
        
        Returns:
            Configured Chrome WebDriver instance
        """
        options = Options()
        
        if self.headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            driver = webdriver.Chrome(options=options)
            logger.info("Chrome driver created successfully")
            return driver
        except WebDriverException as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            raise
    
    def get_page(self, url: str, wait_condition: Optional[str] = None) -> Optional[str]:
        """
        Fetch and return page HTML.
        
        Args:
            url: URL to fetch
            wait_condition: Text to wait for in page title
            
        Returns:
            Page HTML or None if failed
        """
        driver = None
        try:
            driver = self.create_driver()
            
            logger.info(f"Fetching: {url}")
            driver.get(url)
            
            # Wait for page to load
            if wait_condition:
                try:
                    WebDriverWait(driver, self.timeout).until(
                        EC.title_contains(wait_condition)
                    )
                    logger.info(f"Page loaded with condition: {wait_condition}")
                except TimeoutException:
                    logger.warning(f"Timeout waiting for condition: {wait_condition}")
            
            return driver.page_source
        
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        
        finally:
            if driver:
                try:
                    driver.quit()
                    logger.info("Browser closed")
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")
