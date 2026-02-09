"""
Notification Module for Facebook Marketplace Monitor
Handles sending notifications via Telegram.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class Listing:
    """Represents a Facebook Marketplace listing."""
    listing_id: str
    title: str
    price: str
    location: str
    url: str
    image_url: Optional[str] = None
    description: Optional[str] = None
    
    def format_message(self, include_image: bool = True) -> str:
        """Format listing as a notification message."""
        lines = [
            "🆕 *New Marketplace Listing!*",
            "",
            f"📦 *{self._escape_markdown(self.title)}*",
            f"💰 {self._escape_markdown(self.price)}",
            f"📍 {self._escape_markdown(self.location)}",
        ]
        
        if self.description:
            # Truncate long descriptions
            desc = self.description[:200] + "..." if len(self.description) > 200 else self.description
            lines.append(f"📝 {self._escape_markdown(desc)}")
        
        lines.append("")
        lines.append(f"🔗 [View Listing]({self.url})")
        
        return "\n".join(lines)
    
    def format_plain_message(self) -> str:
        """Format listing as plain text."""
        lines = [
            "🆕 New Marketplace Listing!",
            "",
            f"📦 {self.title}",
            f"💰 {self.price}",
            f"📍 {self.location}",
        ]
        
        if self.description:
            desc = self.description[:200] + "..." if len(self.description) > 200 else self.description
            lines.append(f"📝 {desc}")
        
        lines.append("")
        lines.append(f"🔗 {self.url}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _escape_markdown(text: str) -> str:
        """Escape special markdown characters for Telegram."""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text


class TelegramNotifier:
    """Sends notifications via Telegram bot."""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self._bot = None
    
    async def _get_bot(self):
        """Lazy initialization of Telegram bot."""
        if self._bot is None:
            try:
                from telegram import Bot
                self._bot = Bot(token=self.bot_token)
            except ImportError:
                logger.error("python-telegram-bot not installed. Run: pip install python-telegram-bot")
                raise
        return self._bot
    
    async def send_listing(self, listing: Listing) -> bool:
        """Send a listing notification to Telegram."""
        try:
            bot = await self._get_bot()
            message = listing.format_message()
            
            # Send with image if available
            if listing.image_url:
                try:
                    await bot.send_photo(
                        chat_id=self.chat_id,
                        photo=listing.image_url,
                        caption=message,
                        parse_mode="MarkdownV2"
                    )
                except Exception as e:
                    logger.warning(f"Failed to send image, sending text only: {e}")
                    await bot.send_message(
                        chat_id=self.chat_id,
                        text=message,
                        parse_mode="MarkdownV2",
                        disable_web_page_preview=False
                    )
            else:
                await bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode="MarkdownV2",
                    disable_web_page_preview=False
                )
            
            logger.info(f"Telegram notification sent for listing: {listing.listing_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
    
    async def send_message(self, text: str) -> bool:
        """Send a plain text message to Telegram."""
        try:
            bot = await self._get_bot()
            await bot.send_message(
                chat_id=self.chat_id,
                text=text
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False


class NotificationManager:
    """Manages Telegram notifications."""
    
    def __init__(self, config):
        self.config = config
        self._telegram: Optional[TelegramNotifier] = None
        
        # Initialize Telegram notifier if enabled
        if config.telegram.enabled:
            self._telegram = TelegramNotifier(
                config.telegram.bot_token,
                config.telegram.chat_id
            )
            logger.info("Telegram notifications enabled")
    
    async def notify_listing(self, listing: Listing) -> bool:
        """Send listing notification via Telegram."""
        if self._telegram:
            return await self._telegram.send_listing(listing)
        return False
    
    async def notify_listings(self, listings: List[Listing]) -> int:
        """Send notifications for multiple listings. Returns count of successful notifications."""
        success_count = 0
        for listing in listings:
            if await self.notify_listing(listing):
                success_count += 1
            # Small delay between notifications to avoid rate limiting
            await asyncio.sleep(1)
        return success_count
    
    async def send_status_message(self, message: str) -> bool:
        """Send a status message via Telegram."""
        if self._telegram:
            return await self._telegram.send_message(message)
        return False


if __name__ == "__main__":
    # Test notification formatting
    logging.basicConfig(level=logging.DEBUG)
    
    test_listing = Listing(
        listing_id="12345",
        title="iPhone 14 Pro - Like New",
        price="$750",
        location="Denver, CO",
        url="https://www.facebook.com/marketplace/item/12345",
        image_url="https://example.com/image.jpg",
        description="Excellent condition iPhone 14 Pro, 256GB, unlocked. Comes with original box and charger."
    )
    
    print("=== Telegram Format (Markdown) ===")
    print(test_listing.format_message())
    print()
    print("=== Plain Text Format ===")
    print(test_listing.format_plain_message())
