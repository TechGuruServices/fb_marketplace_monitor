"""
Storage Module for Facebook Marketplace Monitor
Tracks seen listings to prevent duplicate notifications.
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
from dataclasses import dataclass, asdict
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class ListingRecord:
    """Record of a seen listing."""
    listing_id: str
    title: str
    first_seen: str  # ISO format datetime
    last_seen: str   # ISO format datetime
    notified: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ListingRecord":
        return cls(**data)
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ListingStorage:
    """
    Persistent storage for tracking seen listings.
    Uses JSON file for simplicity and portability.
    """
    
    def __init__(self, storage_file: str = "seen_listings.json"):
        self.storage_file = storage_file
        self._lock = Lock()
        self._listings: Dict[str, ListingRecord] = {}
        self._load()
    
    def _load(self) -> None:
        """Load listings from storage file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._listings = {
                        listing_id: ListingRecord.from_dict(record)
                        for listing_id, record in data.items()
                    }
                logger.info(f"Loaded {len(self._listings)} listings from storage")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Error loading storage file, starting fresh: {e}")
                self._listings = {}
        else:
            logger.info("No existing storage file, starting fresh")
    
    def _save(self) -> None:
        """Save listings to storage file."""
        try:
            data = {
                listing_id: record.to_dict()
                for listing_id, record in self._listings.items()
            }
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Error saving storage file: {e}")
    
    def has_seen(self, listing_id: str) -> bool:
        """Check if a listing has been seen before."""
        with self._lock:
            return listing_id in self._listings
    
    def mark_seen(self, listing_id: str, title: str, notified: bool = True) -> None:
        """Mark a listing as seen."""
        now = datetime.now().isoformat()
        with self._lock:
            if listing_id in self._listings:
                # Update last seen time
                self._listings[listing_id].last_seen = now
            else:
                # New listing
                self._listings[listing_id] = ListingRecord(
                    listing_id=listing_id,
                    title=title,
                    first_seen=now,
                    last_seen=now,
                    notified=notified
                )
            self._save()
    
    def get_new_listings(self, listing_ids: Set[str]) -> Set[str]:
        """Return set of listing IDs that haven't been seen before."""
        with self._lock:
            return listing_ids - set(self._listings.keys())
    
    def cleanup(self, days: int = 7) -> int:
        """Remove listings older than specified days. Returns count removed."""
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        with self._lock:
            old_listings = [
                listing_id for listing_id, record in self._listings.items()
                if record.last_seen < cutoff_str
            ]
            for listing_id in old_listings:
                del self._listings[listing_id]
            
            if old_listings:
                self._save()
                logger.info(f"Cleaned up {len(old_listings)} old listings")
            
            return len(old_listings)
    
    def get_stats(self) -> Dict:
        """Get storage statistics."""
        with self._lock:
            return {
                "total_listings": len(self._listings),
                "storage_file": self.storage_file,
                "file_exists": os.path.exists(self.storage_file),
                "file_size_bytes": os.path.getsize(self.storage_file) if os.path.exists(self.storage_file) else 0
            }
    
    def clear(self) -> None:
        """Clear all stored listings."""
        with self._lock:
            self._listings = {}
            self._save()
            logger.info("Cleared all stored listings")


# Singleton instance
_storage: Optional[ListingStorage] = None


def get_storage(storage_file: str = "seen_listings.json") -> ListingStorage:
    """Get or create the singleton storage instance."""
    global _storage
    if _storage is None:
        _storage = ListingStorage(storage_file)
    return _storage


if __name__ == "__main__":
    # Test storage functionality
    logging.basicConfig(level=logging.DEBUG)
    
    storage = ListingStorage("test_listings.json")
    
    # Test marking listings
    storage.mark_seen("123", "Test Item 1")
    storage.mark_seen("456", "Test Item 2")
    
    print(f"Has seen 123: {storage.has_seen('123')}")
    print(f"Has seen 789: {storage.has_seen('789')}")
    
    new_ids = storage.get_new_listings({"123", "789", "101"})
    print(f"New listings: {new_ids}")
    
    print(f"Stats: {storage.get_stats()}")
    
    # Cleanup test file
    os.remove("test_listings.json")
    print("Test complete!")
