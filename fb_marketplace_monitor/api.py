"""
REST API for Facebook Marketplace Monitor
Provides HTTP endpoints to control and query the monitor.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import asdict
import json
import threading

# Flask for simple REST API
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("Flask not installed. Run: pip install flask flask-cors")
    raise

from config import get_config, Config
from storage import get_storage, ListingStorage
from scraper import FacebookMarketplaceScraper, ScraperConfig
from notifications import NotificationManager, Listing

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global state
config = get_config()
storage = get_storage(config.monitor.storage_file)
monitor_thread: Optional[threading.Thread] = None
monitor_running = False
last_check_time: Optional[datetime] = None
last_check_results: List[Dict] = []


def run_async(coro):
    """Helper to run async functions in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ============================================================
# API ENDPOINTS
# ============================================================

@app.route("/", methods=["GET"])
def root():
    """API root - returns basic info and available endpoints."""
    return jsonify({
        "service": "Facebook Marketplace Monitor API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "GET /": "This endpoint - API information",
            "GET /health": "Health check",
            "GET /config": "Current configuration",
            "GET /status": "Monitor status",
            "GET /listings": "Get tracked listings",
            "POST /search": "Perform a search",
            "POST /notify": "Send a test notification",
            "POST /monitor/start": "Start continuous monitoring",
            "POST /monitor/stop": "Stop monitoring",
            "DELETE /listings": "Clear all tracked listings"
        }
    })


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "monitor_running": monitor_running
    })


@app.route("/config", methods=["GET"])
def get_configuration():
    """Get current configuration (sanitized - no secrets)."""
    return jsonify({
        "search": {
            "keywords": config.search.keywords,
            "location": config.search.location,
            "radius_miles": config.search.radius_miles,
            "min_price": config.search.min_price,
            "max_price": config.search.max_price,
            "category": config.search.category
        },
        "monitor": {
            "check_interval_seconds": config.monitor.check_interval_seconds,
            "headless_browser": config.monitor.headless_browser,
            "max_listings_per_check": config.monitor.max_listings_per_check,
            "cleanup_days": config.monitor.cleanup_days
        },
        "notifications": {
            "telegram_enabled": config.telegram.enabled,
            "whatsapp_enabled": config.whatsapp.enabled
        }
    })


@app.route("/status", methods=["GET"])
def get_status():
    """Get current monitor status."""
    stats = storage.get_stats()
    
    return jsonify({
        "monitor_running": monitor_running,
        "last_check": last_check_time.isoformat() if last_check_time else None,
        "last_results_count": len(last_check_results),
        "storage": stats,
        "configuration_valid": len(config.validate()) == 0,
        "configuration_errors": config.validate()
    })


@app.route("/listings", methods=["GET"])
def get_listings():
    """Get all tracked listings."""
    limit = request.args.get("limit", default=100, type=int)
    offset = request.args.get("offset", default=0, type=int)
    
    # Get listings from storage
    listings = list(storage._listings.values())
    total = len(listings)
    
    # Sort by first_seen (newest first)
    listings.sort(key=lambda x: x.first_seen, reverse=True)
    
    # Paginate
    listings = listings[offset:offset + limit]
    
    return jsonify({
        "total": total,
        "offset": offset,
        "limit": limit,
        "listings": [l.to_dict() for l in listings]
    })


@app.route("/listings", methods=["DELETE"])
def clear_listings():
    """Clear all tracked listings."""
    storage.clear()
    return jsonify({
        "success": True,
        "message": "All listings cleared"
    })


@app.route("/search", methods=["POST"])
def search():
    """Perform a one-time search."""
    global last_check_time, last_check_results
    
    data = request.get_json() or {}
    
    # Get search parameters (use config defaults if not provided)
    query = data.get("query") or (config.search.keywords[0] if config.search.keywords else None)
    
    if not query:
        return jsonify({"error": "No search query provided"}), 400
    
    try:
        scraper_config = ScraperConfig(headless=config.monitor.headless_browser)
        
        with FacebookMarketplaceScraper(scraper_config) as scraper:
            listings = scraper.search(
                query=query,
                location=data.get("location", config.search.location),
                min_price=data.get("min_price", config.search.min_price),
                max_price=data.get("max_price", config.search.max_price),
                radius_miles=data.get("radius_miles", config.search.radius_miles),
                max_listings=data.get("max_listings", 10)
            )
        
        # Update last check info
        last_check_time = datetime.now()
        last_check_results = [
            {
                "listing_id": l.listing_id,
                "title": l.title,
                "price": l.price,
                "location": l.location,
                "url": l.url,
                "image_url": l.image_url,
                "is_new": not storage.has_seen(l.listing_id)
            }
            for l in listings
        ]
        
        return jsonify({
            "success": True,
            "query": query,
            "count": len(listings),
            "listings": last_check_results
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/notify", methods=["POST"])
def send_notification():
    """Send a test notification."""
    data = request.get_json() or {}
    message = data.get("message", "Test notification from Marketplace Monitor API")
    
    try:
        notifier = NotificationManager(config)
        success = run_async(notifier.send_status_message(message))
        
        return jsonify({
            "success": success,
            "message": "Notification sent" if success else "Failed to send notification"
        })
        
    except Exception as e:
        logger.error(f"Notification error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/notify/listing", methods=["POST"])
def send_listing_notification():
    """Send a notification for a specific listing."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No listing data provided"}), 400
    
    try:
        listing = Listing(
            listing_id=data.get("listing_id", "api-test"),
            title=data.get("title", "Test Listing"),
            price=data.get("price", "$0"),
            location=data.get("location", "Unknown"),
            url=data.get("url", "https://facebook.com/marketplace"),
            image_url=data.get("image_url"),
            description=data.get("description")
        )
        
        notifier = NotificationManager(config)
        success = run_async(notifier.notify_listing(listing))
        
        return jsonify({
            "success": success,
            "message": "Listing notification sent" if success else "Failed to send"
        })
        
    except Exception as e:
        logger.error(f"Notification error: {e}")
        return jsonify({"error": str(e)}), 500


def background_monitor():
    """Background monitoring thread."""
    global monitor_running, last_check_time, last_check_results
    
    from monitor import MarketplaceMonitor
    
    monitor = MarketplaceMonitor(config)
    
    async def run():
        global monitor_running, last_check_time, last_check_results
        
        scraper_config = ScraperConfig(headless=config.monitor.headless_browser)
        monitor.scraper = FacebookMarketplaceScraper(scraper_config)
        
        try:
            while monitor_running:
                try:
                    await monitor.check_once()
                    last_check_time = datetime.now()
                except Exception as e:
                    logger.error(f"Monitor check error: {e}")
                
                await asyncio.sleep(config.monitor.check_interval_seconds)
        finally:
            monitor.scraper.close()
    
    run_async(run())


@app.route("/monitor/start", methods=["POST"])
def start_monitor():
    """Start continuous monitoring in background."""
    global monitor_thread, monitor_running
    
    if monitor_running:
        return jsonify({
            "success": False,
            "message": "Monitor is already running"
        })
    
    # Validate config first
    errors = config.validate()
    if errors:
        return jsonify({
            "success": False,
            "message": "Configuration errors",
            "errors": errors
        }), 400
    
    monitor_running = True
    monitor_thread = threading.Thread(target=background_monitor, daemon=True)
    monitor_thread.start()
    
    return jsonify({
        "success": True,
        "message": "Monitor started"
    })


@app.route("/monitor/stop", methods=["POST"])
def stop_monitor():
    """Stop continuous monitoring."""
    global monitor_running
    
    if not monitor_running:
        return jsonify({
            "success": False,
            "message": "Monitor is not running"
        })
    
    monitor_running = False
    
    return jsonify({
        "success": True,
        "message": "Monitor stopping..."
    })


# ============================================================
# RUN SERVER
# ============================================================

def run_api(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Run the Flask API server."""
    logger.info(f"Starting Marketplace Monitor API on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Marketplace Monitor REST API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    run_api(host=args.host, port=args.port, debug=args.debug)
