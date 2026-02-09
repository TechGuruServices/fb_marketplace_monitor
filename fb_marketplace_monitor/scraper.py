"""
Facebook Marketplace Scraper Module
Uses Selenium with undetected-chromedriver for stealth scraping.
"""

import logging
import random
import time
import re
from typing import List, Optional
from dataclasses import dataclass
from urllib.parse import urlencode, quote

from notifications import Listing

logger = logging.getLogger(__name__)


@dataclass
class ScraperConfig:
    """Configuration for the scraper."""
    headless: bool = True
    min_delay: float = 2.0
    max_delay: float = 5.0
    page_load_timeout: int = 30
    implicit_wait: int = 10


class FacebookMarketplaceScraper:
    """
    Scrapes Facebook Marketplace listings.
    Uses undetected-chromedriver to bypass anti-bot measures.
    """
    
    BASE_URL = "https://www.facebook.com/marketplace"
    
    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self._driver = None
    
    def _get_driver(self):
        """Initialize and return the Selenium WebDriver."""
        if self._driver is None:
            try:
                import undetected_chromedriver as uc
                
                options = uc.ChromeOptions()
                
                if self.config.headless:
                    options.add_argument("--headless=new")
                
                # Anti-detection options
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                self._driver = uc.Chrome(options=options)
                self._driver.set_page_load_timeout(self.config.page_load_timeout)
                self._driver.implicitly_wait(self.config.implicit_wait)
                
                logger.info("WebDriver initialized successfully")
                
            except ImportError:
                logger.error("undetected-chromedriver not installed. Run: pip install undetected-chromedriver")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize WebDriver: {e}")
                raise
        
        return self._driver
    
    def _random_delay(self) -> None:
        """Add random delay to mimic human behavior."""
        delay = random.uniform(self.config.min_delay, self.config.max_delay)
        time.sleep(delay)
    
    def _build_search_url(
        self,
        query: str,
        location: str = "",
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        radius_miles: int = 40,
        category: str = ""
    ) -> str:
        """Build Facebook Marketplace search URL."""
        # Base search URL
        if category:
            base = f"{self.BASE_URL}/{category}"
        else:
            base = f"{self.BASE_URL}/search"
        
        # Build query parameters
        params = {
            "query": query,
            "sortBy": "creation_time_descend",  # Newest first
            "exact": "false"
        }
        
        if min_price is not None:
            params["minPrice"] = str(min_price)
        if max_price is not None:
            params["maxPrice"] = str(max_price)
        
        url = f"{base}?{urlencode(params)}"
        logger.debug(f"Built search URL: {url}")
        return url
    
    def _scroll_page(self, scroll_count: int = 3) -> None:
        """Scroll down the page to load more listings."""
        driver = self._get_driver()
        for i in range(scroll_count):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._random_delay()
    
    def _parse_listings(self, max_listings: int = 20) -> List[Listing]:
        """Parse listing elements from the current page."""
        driver = self._get_driver()
        listings = []
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Wait for marketplace listings to load
            # Facebook's DOM structure changes frequently, so we use multiple selectors
            selectors = [
                "[data-testid='marketplace_search_feed']",
                "[role='main'] [role='list']",
                "div.x1lliihq",  # Common listing container class
            ]
            
            listing_elements = []
            for selector in selectors:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    # Find individual listing items
                    listing_elements = driver.find_elements(By.CSS_SELECTOR, f"{selector} a[href*='/marketplace/item/']")
                    if listing_elements:
                        break
                except:
                    continue
            
            if not listing_elements:
                # Fallback: find all marketplace item links
                listing_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/marketplace/item/']")
            
            logger.info(f"Found {len(listing_elements)} listing elements")
            
            for element in listing_elements[:max_listings]:
                try:
                    listing = self._parse_single_listing(element)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    logger.warning(f"Error parsing listing element: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error parsing listings: {e}")
        
        return listings
    
    def _parse_single_listing(self, element) -> Optional[Listing]:
        """Parse a single listing element into a Listing object."""
        try:
            from selenium.webdriver.common.by import By
            
            # Extract listing URL and ID
            url = element.get_attribute("href")
            if not url:
                return None
            
            # Extract listing ID from URL
            match = re.search(r'/marketplace/item/(\d+)', url)
            if not match:
                return None
            listing_id = match.group(1)
            
            # Extract text content
            text_content = element.text.strip()
            lines = text_content.split('\n')
            
            # Parse the text (format varies, but usually: price, title, location)
            title = "Unknown"
            price = "Price not listed"
            location = "Unknown location"
            
            if len(lines) >= 1:
                # First line is usually price
                price = lines[0] if '$' in lines[0] or 'Free' in lines[0] else "Price not listed"
            if len(lines) >= 2:
                title = lines[1] if len(lines[1]) > 0 else lines[0]
            if len(lines) >= 3:
                location = lines[-1]  # Location usually last
            
            # Try to extract image
            image_url = None
            try:
                img = element.find_element(By.TAG_NAME, "img")
                image_url = img.get_attribute("src")
            except:
                pass
            
            return Listing(
                listing_id=listing_id,
                title=title,
                price=price,
                location=location,
                url=url,
                image_url=image_url,
                description=None  # Need to visit individual page for description
            )
            
        except Exception as e:
            logger.debug(f"Error parsing single listing: {e}")
            return None
    
    def search(
        self,
        query: str,
        location: str = "",
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        radius_miles: int = 40,
        category: str = "",
        max_listings: int = 20
    ) -> List[Listing]:
        """
        Search Facebook Marketplace and return listings.
        
        Args:
            query: Search query/keywords
            location: City/area (optional)
            min_price: Minimum price filter
            max_price: Maximum price filter
            radius_miles: Search radius
            category: Category filter
            max_listings: Maximum number of listings to return
        
        Returns:
            List of Listing objects
        """
        driver = self._get_driver()
        
        try:
            # Build and navigate to search URL
            url = self._build_search_url(
                query=query,
                location=location,
                min_price=min_price,
                max_price=max_price,
                radius_miles=radius_miles,
                category=category
            )
            
            logger.info(f"Searching for: {query}")
            driver.get(url)
            self._random_delay()
            
            # Check for login wall
            if "login" in driver.current_url.lower():
                logger.warning("Encountered login wall - Facebook may require authentication")
                # Note: Full login handling would require user credentials
                # For now, we return empty results
                return []
            
            # Scroll to load more listings
            self._scroll_page(scroll_count=2)
            
            # Parse listings
            listings = self._parse_listings(max_listings=max_listings)
            logger.info(f"Found {len(listings)} listings for query: {query}")
            
            return listings
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    def close(self) -> None:
        """Close the WebDriver."""
        if self._driver:
            try:
                self._driver.quit()
                logger.info("WebDriver closed")
            except:
                pass
            self._driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def test_scraper():
    """Test the scraper functionality."""
    logging.basicConfig(level=logging.DEBUG)
    
    config = ScraperConfig(headless=False)  # Set to True for headless
    
    with FacebookMarketplaceScraper(config) as scraper:
        listings = scraper.search(
            query="iphone",
            max_price=500,
            max_listings=5
        )
        
        for listing in listings:
            print(f"\n{'='*50}")
            print(f"ID: {listing.listing_id}")
            print(f"Title: {listing.title}")
            print(f"Price: {listing.price}")
            print(f"Location: {listing.location}")
            print(f"URL: {listing.url}")


if __name__ == "__main__":
    test_scraper()
