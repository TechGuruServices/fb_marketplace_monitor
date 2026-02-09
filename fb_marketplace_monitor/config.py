"""
Configuration Module for Facebook Marketplace Monitor
Loads environment variables and provides configuration settings.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class TelegramConfig:
    """Telegram bot configuration."""
    enabled: bool = False
    bot_token: str = ""
    chat_id: str = ""
    
    def __post_init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.enabled = bool(self.bot_token and self.chat_id)


@dataclass
class WhatsAppConfig:
    """WhatsApp (Twilio) configuration."""
    enabled: bool = False
    account_sid: str = ""
    auth_token: str = ""
    from_number: str = ""  # Twilio WhatsApp number (e.g., whatsapp:+14155238886)
    to_number: str = ""    # Your WhatsApp number (e.g., whatsapp:+1234567890)
    
    def __post_init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.from_number = os.getenv("TWILIO_WHATSAPP_FROM", "")
        self.to_number = os.getenv("TWILIO_WHATSAPP_TO", "")
        self.enabled = bool(
            self.account_sid and self.auth_token and 
            self.from_number and self.to_number
        )


@dataclass
class SearchConfig:
    """Facebook Marketplace search configuration."""
    keywords: List[str] = field(default_factory=list)
    location: str = ""
    radius_miles: int = 40
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    category: str = ""  # e.g., "vehicles", "electronics", "furniture"
    
    def __post_init__(self):
        keywords_str = os.getenv("SEARCH_KEYWORDS", "")
        self.keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
        self.location = os.getenv("SEARCH_LOCATION", "")
        self.radius_miles = int(os.getenv("SEARCH_RADIUS_MILES", "40"))
        self.min_price = int(os.getenv("SEARCH_MIN_PRICE")) if os.getenv("SEARCH_MIN_PRICE") else None
        self.max_price = int(os.getenv("SEARCH_MAX_PRICE")) if os.getenv("SEARCH_MAX_PRICE") else None
        self.category = os.getenv("SEARCH_CATEGORY", "")


@dataclass
class MonitorConfig:
    """Monitoring behavior configuration."""
    check_interval_seconds: int = 300  # 5 minutes default
    max_retries: int = 3
    retry_delay_seconds: int = 60
    headless_browser: bool = True
    log_level: str = "INFO"
    storage_file: str = "seen_listings.json"
    max_listings_per_check: int = 20
    cleanup_days: int = 7  # Remove listings older than this
    
    def __post_init__(self):
        self.check_interval_seconds = int(os.getenv("CHECK_INTERVAL_SECONDS", "300"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay_seconds = int(os.getenv("RETRY_DELAY_SECONDS", "60"))
        self.headless_browser = os.getenv("HEADLESS_BROWSER", "true").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.storage_file = os.getenv("STORAGE_FILE", "seen_listings.json")
        self.max_listings_per_check = int(os.getenv("MAX_LISTINGS_PER_CHECK", "20"))
        self.cleanup_days = int(os.getenv("CLEANUP_DAYS", "7"))


class Config:
    """Main configuration class that aggregates all config sections."""
    
    def __init__(self):
        self.telegram = TelegramConfig()
        self.whatsapp = WhatsAppConfig()
        self.search = SearchConfig()
        self.monitor = MonitorConfig()
        
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Check if at least one notification method is enabled
        if not self.telegram.enabled and not self.whatsapp.enabled:
            errors.append("No notification method configured. Enable Telegram or WhatsApp.")
        
        # Check search keywords
        if not self.search.keywords:
            errors.append("No search keywords configured. Set SEARCH_KEYWORDS env var.")
        
        return errors
    
    def __str__(self) -> str:
        """Return human-readable config summary."""
        lines = [
            "=== Facebook Marketplace Monitor Configuration ===",
            f"",
            f"📱 Notifications:",
            f"   Telegram: {'✅ Enabled' if self.telegram.enabled else '❌ Disabled'}",
            f"   WhatsApp:  {'✅ Enabled' if self.whatsapp.enabled else '❌ Disabled'}",
            f"",
            f"🔍 Search:",
            f"   Keywords: {', '.join(self.search.keywords) or 'None'}",
            f"   Location: {self.search.location or 'Not set'}",
            f"   Radius: {self.search.radius_miles} miles",
            f"   Price: ${self.search.min_price or 0} - ${self.search.max_price or '∞'}",
            f"   Category: {self.search.category or 'All'}",
            f"",
            f"⚙️ Monitor:",
            f"   Check Interval: {self.monitor.check_interval_seconds}s",
            f"   Headless Browser: {self.monitor.headless_browser}",
            f"   Log Level: {self.monitor.log_level}",
        ]
        return "\n".join(lines)


# Singleton instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the singleton config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


if __name__ == "__main__":
    # Test configuration loading
    config = get_config()
    print(config)
    
    errors = config.validate()
    if errors:
        print("\n⚠️ Configuration Errors:")
        for error in errors:
            print(f"   - {error}")
