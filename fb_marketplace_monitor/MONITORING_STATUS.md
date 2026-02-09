# Facebook Marketplace Monitor - Status Report

**Generated:** 2026-02-08 20:15:00  
**Status:** ✅ ACTIVE & RUNNING

---

## 🚀 System Status

### API Server

- **Status:** ✅ Running
- **Port:** 8080
- **Host:** 0.0.0.0 (all interfaces)
- **Endpoints Available:** 9 REST endpoints

### Background Monitor

- **Status:** ✅ Running
- **Mode:** Continuous scanning
- **Check Interval:** 900 seconds (15 minutes)
- **Browser Mode:** Headless (background)

### Telegram Notifications

- **Status:** ✅ Enabled
- **Bot Token:** Configured (8302493445:...)
- **Chat ID:** 8258440957
- **Notification Type:** Instant alerts with images & links

---

## 📊 Current Configuration

### Search Parameters

**Keywords Being Monitored:**

- AUTOMOTIVE / VEHICLES
- ELECTRONICS
- TOOLS / POWER TOOLS
- TOOL SETS
- CAR PARTS
- INDUSTRIAL EQUIPMENT
- WANTED TO BUY
- FAST SALE
- BRAND NEW / LIKE NEW
- BUILDING MATERIALS

**Location Settings:**

- Primary: Montana, USA
- Cities: Missoula, Kalispell, Billings
- Search Radius: 350 miles

**Price Filters:**

- Minimum: None (all listings)
- Maximum: $5,000

**Categories:**

- Automotive / Vehicles
- Electronics
- Tools / Power Tools/Sets
- Car Parts
- Industrial Equipment / Farm Equipment

### Monitor Settings

- **Listings per check:** 10
- **Cleanup period:** 365 days
- **Max retries:** 3
- **Retry delay:** 60 seconds
- **Log level:** INFO

---

## 🔔 Notification System

### How It Works

1. **Continuous Scanning:** Monitor checks Facebook Marketplace every 15 minutes
2. **New Listing Detection:** Compares against database of seen listings
3. **Instant Telegram Alert:** Sends formatted notification with:
   - 📦 Listing title
   - 💰 Price
   - 📍 Location
   - 📝 Description (truncated if long)
   - 🖼️ Image (if available)
   - 🔗 Direct link to listing

### Notification Format Example

```
🆕 New Marketplace Listing!

📦 2015 Ford F-150 - Excellent Condition
💰 $25,000
📍 Missoula, MT
📝 Well maintained truck with only 45k miles...

🔗 [View Listing](https://facebook.com/marketplace/item/...)
```

---

## 🛠️ API Endpoints

### Status & Info

- `GET /` - API information
- `GET /health` - Health check
- `GET /status` - Monitor status & stats
- `GET /config` - Current configuration

### Data Management

- `GET /listings` - View tracked listings (paginated)
- `DELETE /listings` - Clear all tracked listings

### Operations

- `POST /search` - Perform manual search
- `POST /notify` - Send test notification
- `POST /notify/listing` - Send listing notification

### Monitor Control

- `POST /monitor/start` - Start continuous monitoring ✅ ACTIVE
- `POST /monitor/stop` - Stop monitoring

---

## 📁 Project Files

### Core Files

```
fb_marketplace_monitor/fb_marketplace_monitor/
├── api.py                    # REST API server (369 lines)
├── monitor.py                # Main monitoring logic (302 lines)
├── scraper.py                # Facebook scraper (11,701 bytes)
├── notifications.py          # Telegram notifications (201 lines)
├── config.py                 # Configuration management (5,916 bytes)
├── storage.py                # Listing storage/database (5,894 bytes)
├── .env                      # Environment configuration ✅
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── QUICKSTART.md            # Quick start guide
└── marketplace_monitor.log  # Rolling log file
```

### Data Files

- `seen_listings.json` - Database of tracked listings (auto-created)

---

## ⚙️ How to Interact with the Monitor

### Check Status

```powershell
curl http://localhost:8080/status
```

### View Recent Listings

```powershell
curl http://localhost:8080/listings?limit=20
```

### Send Test Notification

```powershell
curl -X POST http://localhost:8080/notify -H "Content-Type: application/json" -d "{\"message\": \"Test message\"}"
```

### Manual Search

```powershell
curl -X POST http://localhost:8080/search -H "Content-Type: application/json" -d "{\"query\": \"ford f150\", \"max_listings\": 10}"
```

### Stop Monitoring

```powershell
curl -X POST http://localhost:8080/monitor/stop
```

### Restart Monitoring

```powershell
curl -X POST http://localhost:8080/monitor/start
```

---

## 🔧 Known Issues & Notes

### ChromeDriver Version Warning

- **Issue:** Monitor shows warning about ChromeDriver version detection
- **Impact:** Minor - does not affect functionality
- **Status:** Monitor is still functional despite warning
- **Solution (if needed):** Update `undetected-chromedriver` package

### Performance Notes

- First check may take 2-3 minutes as browser initializes
- Subsequent checks are faster (cached browser session)
- Rate limiting: 1 second delay between notifications to avoid spam

---

## 📝 Maintenance Commands

### View Logs (Live)

```powershell
Get-Content C:\Users\lucas\fb_marketplace_monitor\fb_marketplace_monitor\marketplace_monitor.log -Wait
```

### Restart API Server

1. Stop current server (Ctrl+C in terminal)
2. Restart: `python api.py --port 8080`

### Update Configuration

1. Edit `.env` file with your changes
2. Restart API server for changes to take effect

### Clear Listing Database

```powershell
curl -X DELETE http://localhost:8080/listings
```

---

## ✅ Verification Checklist

- [x] API server running on port 8080
- [x] Background monitor active and scanning
- [x] Telegram bot configured and ready
- [x] 10 keywords configured for monitoring
- [x] Geographic filters set (Montana + 350 mile radius)
- [x] Price filter active (max $5,000)
- [x] Category filters applied
- [x] Notification system operational
- [x] Storage system initialized
- [x] Configuration validated (no errors)

---

## 📞 How to Get Notified

You will receive **automatic Telegram notifications** to chat ID `8258440957` when:

1. ✅ Monitor starts (startup notification sent)
2. 🆕 New listing matches your search criteria
3. 🛑 Monitor stops (shutdown notification)

**No manual checking required!** Just keep Telegram open and wait for alerts.

---

## 🎯 What Happens Next

### Automatic Process

1. **Every 15 minutes**, the monitor will:
   - Search Facebook Marketplace for all 10 keywords
   - Check each category and location
   - Filter by price (under $5,000)
   - Compare against seen listings database

2. **When new listings are found:**
   - Send Telegram notification with full details
   - Save listing ID to prevent duplicate alerts
   - Include clickable link and image

3. **Database maintenance:**
   - Auto-cleanup listings older than 365 days
   - Efficient storage management

### You Should

- ✅ Keep API server running (don't close terminal)
- ✅ Keep Telegram app open/logged in
- ✅ Click links in notifications to view listings immediately
- ✅ Adjust `.env` configuration if you want different filters

---

## 🚨 Troubleshooting

### Not receiving notifications?

```powershell
# Test Telegram connection
curl -X POST http://localhost:8080/notify -H "Content-Type: application/json" -d "{\"message\": \"Test\"}"
```

### Check if monitor is running

```powershell
curl http://localhost:8080/status
```

### View recent activity

```powershell
curl http://localhost:8080/listings
```

### Restart everything

```powershell
# Stop monitor
curl -X POST http://localhost:8080/monitor/stop

# Wait 5 seconds

# Restart monitor
curl -X POST http://localhost:8080/monitor/start
```

---

**🎉 Your Facebook Marketplace Monitor is now actively scanning and will alert you of new listings matching your criteria!**
