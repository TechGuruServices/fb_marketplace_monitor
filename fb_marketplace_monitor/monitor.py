"""
Facebook Marketplace Monitor - Main Entry Point
Continuously monitors marketplace for new listings and sends notifications.
"""

import asyncio
import logging
import signal
import sys
import argparse
from datetime import datetime
from typing import List

from config import get_config, Config
from storage import get_storage, ListingStorage
from scraper import FacebookMarketplaceScraper, ScraperConfig
from notifications import NotificationManager, Listing

# Setup logging
def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure logging with console and file handlers."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # File handler
    file_handler = logging.FileHandler("marketplace_monitor.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    return logging.getLogger(__name__)


class MarketplaceMonitor:
    """Main monitoring class that orchestrates scraping and notifications."""
    
    def __init__(self, config: Config):
        self.config = config
        self.storage = get_storage(config.monitor.storage_file)
        self.notifier = NotificationManager(config)
        self.scraper: FacebookMarketplaceScraper = None
        self._running = False
        self._logger = logging.getLogger(__name__)
    
    async def _search_all_keywords(self) -> List[Listing]:
        """Search for all configured keywords and return combined results."""
        all_listings = []
        
        for keyword in self.config.search.keywords:
            try:
                listings = self.scraper.search(
                    query=keyword,
                    location=self.config.search.location,
                    min_price=self.config.search.min_price,
                    max_price=self.config.search.max_price,
                    radius_miles=self.config.search.radius_miles,
                    category=self.config.search.category,
                    max_listings=self.config.monitor.max_listings_per_check
                )
                all_listings.extend(listings)
                
                # Delay between keyword searches
                await asyncio.sleep(2)
                
            except Exception as e:
                self._logger.error(f"Error searching for '{keyword}': {e}")
        
        # Deduplicate by listing ID
        seen_ids = set()
        unique_listings = []
        for listing in all_listings:
            if listing.listing_id not in seen_ids:
                seen_ids.add(listing.listing_id)
                unique_listings.append(listing)
        
        return unique_listings
    
    async def _process_listings(self, listings: List[Listing]) -> int:
        """Process listings, filter new ones, and send notifications. Returns count of new listings."""
        if not listings:
            return 0
        
        # Get IDs of listings we haven't seen
        listing_ids = {l.listing_id for l in listings}
        new_ids = self.storage.get_new_listings(listing_ids)
        
        if not new_ids:
            self._logger.info("No new listings found")
            return 0
        
        # Filter to only new listings
        new_listings = [l for l in listings if l.listing_id in new_ids]
        self._logger.info(f"Found {len(new_listings)} new listings!")
        
        # Send notifications
        success_count = await self.notifier.notify_listings(new_listings)
        
        # Mark all as seen
        for listing in new_listings:
            self.storage.mark_seen(listing.listing_id, listing.title)
        
        return success_count
    
    async def check_once(self) -> int:
        """Perform a single check for new listings. Returns count of notifications sent."""
        self._logger.info("Starting marketplace check...")
        
        try:
            # Search for all keywords
            listings = await self._search_all_keywords()
            self._logger.info(f"Found {len(listings)} total listings")
            
            # Process and notify
            notification_count = await self._process_listings(listings)
            
            # Cleanup old entries
            self.storage.cleanup(days=self.config.monitor.cleanup_days)
            
            return notification_count
            
        except Exception as e:
            self._logger.error(f"Error during check: {e}")
            return 0
    
    async def run(self) -> None:
        """Run the monitor continuously."""
        self._running = True
        self._logger.info("Starting Facebook Marketplace Monitor...")
        self._logger.info(str(self.config))
        
        # Validate configuration
        errors = self.config.validate()
        if errors:
            self._logger.error("Configuration errors:")
            for error in errors:
                self._logger.error(f"  - {error}")
            return
        
        # Initialize scraper
        scraper_config = ScraperConfig(headless=self.config.monitor.headless_browser)
        self.scraper = FacebookMarketplaceScraper(scraper_config)
        
        # Send startup notification
        await self.notifier.send_status_message(
            f"🚀 Marketplace Monitor Started\n"
            f"📍 Keywords: {', '.join(self.config.search.keywords)}\n"
            f"⏰ Check interval: {self.config.monitor.check_interval_seconds}s"
        )
        
        retry_count = 0
        
        try:
            while self._running:
                try:
                    notification_count = await self.check_once()
                    
                    if notification_count > 0:
                        self._logger.info(f"Sent {notification_count} notifications")
                    
                    retry_count = 0  # Reset on success
                    
                except Exception as e:
                    retry_count += 1
                    self._logger.error(f"Check failed (attempt {retry_count}): {e}")
                    
                    if retry_count >= self.config.monitor.max_retries:
                        self._logger.error("Max retries reached, waiting before next attempt")
                        await asyncio.sleep(self.config.monitor.retry_delay_seconds)
                        retry_count = 0
                    
                    # Exponential backoff on errors
                    await asyncio.sleep(min(30 * retry_count, 300))
                    continue
                
                # Wait for next check
                self._logger.info(f"Next check in {self.config.monitor.check_interval_seconds} seconds...")
                await asyncio.sleep(self.config.monitor.check_interval_seconds)
                
        except asyncio.CancelledError:
            self._logger.info("Monitor cancelled")
        finally:
            await self.shutdown()
    
    async def shutdown(self) -> None:
        """Clean shutdown of the monitor."""
        self._running = False
        self._logger.info("Shutting down...")
        
        if self.scraper:
            self.scraper.close()
        
        await self.notifier.send_status_message("🛑 Marketplace Monitor Stopped")
        self._logger.info("Shutdown complete")
    
    def stop(self) -> None:
        """Signal the monitor to stop."""
        self._running = False


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Facebook Marketplace Monitor - Get notified of new listings"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single check and exit"
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show current configuration and exit"
    )
    parser.add_argument(
        "--test-notify",
        action="store_true",
        help="Send a test notification and exit"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = get_config()
    
    # Setup logging
    logger = setup_logging(args.log_level or config.monitor.log_level)
    
    # Handle config display
    if args.config:
        print(config)
        errors = config.validate()
        if errors:
            print("\n⚠️ Configuration Errors:")
            for error in errors:
                print(f"   - {error}")
        return
    
    # Create monitor
    monitor = MarketplaceMonitor(config)
    
    # Handle test notification
    if args.test_notify:
        async def test_notify():
            test_listing = Listing(
                listing_id="test123",
                title="Test Listing - Marketplace Monitor",
                price="$0",
                location="Test Location",
                url="https://www.facebook.com/marketplace",
                description="This is a test notification from the Marketplace Monitor."
            )
            success = await monitor.notifier.notify_listing(test_listing)
            if success:
                print("✅ Test notification sent successfully!")
            else:
                print("❌ Failed to send test notification")
        
        asyncio.run(test_notify())
        return
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, stopping...")
        monitor.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run monitor
    if args.once:
        async def run_once():
            monitor.scraper = FacebookMarketplaceScraper(
                ScraperConfig(headless=config.monitor.headless_browser)
            )
            try:
                count = await monitor.check_once()
                print(f"Check complete. Sent {count} notifications.")
            finally:
                monitor.scraper.close()
        
        asyncio.run(run_once())
    else:
        asyncio.run(monitor.run())


if __name__ == "__main__":
    main()
