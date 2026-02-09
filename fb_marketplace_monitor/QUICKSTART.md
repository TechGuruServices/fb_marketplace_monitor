# 🚀 Facebook Marketplace Monitor - Quick Start Guide

## 📋 Prerequisites

Before running the monitor, ensure you have:

| Requirement | Status |
|-------------|--------|
| Python 3.10+ | ✅ Installed (3.14) |
| Google Chrome | ✅ Installed |
| Selenium | ✅ Installed (4.40.0) |
| undetected-chromedriver | ✅ Installed (3.5.5) |
| Telegram Bot (optional) | Configure in `.env` |

---

## 📁 Project Location

```
C:\Users\lucas\fb_marketplace_monitor\fb_marketplace_monitor\
```

---

## ⚡ Quick Setup (One-Time)

### Step 1: Open Terminal in Project Directory

```powershell
cd C:\Users\lucas\fb_marketplace_monitor\fb_marketplace_monitor
```

### Step 2: Install Dependencies (if not already done)

```powershell
python -m pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Edit the `.env` file with your settings:

```powershell
notepad .env
```

**Key settings to configure:**

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather | `123456:ABC...` |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID from @userinfobot | `123456789` |
| `SEARCH_KEYWORDS` | Comma-separated search terms | `iphone, macbook, ps5` |
| `SEARCH_LOCATION` | Your city/area | `Missoula, Montana` |
| `CHECK_INTERVAL_SECONDS` | How often to check (seconds) | `120` |

---

## 🎯 Running the Monitor

### Option 1: Continuous Monitoring (Recommended)

Runs continuously and sends Telegram notifications for new listings:

```powershell
cd C:\Users\lucas\fb_marketplace_monitor\fb_marketplace_monitor
python monitor.py
```

**Stop the monitor:** Press `Ctrl + C`

---

### Option 2: Single Check

Run once, check for listings, then exit:

```powershell
python monitor.py --once
```

---

### Option 3: Test Notification

Send a test notification to verify Telegram is working:

```powershell
python monitor.py --test-notify
```

---

### Option 4: View Configuration

Display current configuration settings:

```powershell
python monitor.py --config
```

---

### Option 5: Run REST API Server

Start the web API for remote control:

```powershell
python api.py
```

API will be available at: `http://localhost:5000`

**Useful API Endpoints:**

- `GET /` - API info
- `GET /health` - Health check
- `GET /status` - Monitor status
- `POST /search` - Perform a search
- `POST /notify` - Send test notification
- `POST /monitor/start` - Start monitoring
- `POST /monitor/stop` - Stop monitoring

---

## 🧪 Testing Commands

### Test Telegram Connection

```powershell
python test_telegram.py
```

### Verify Chat ID

```powershell
python verify_chat.py
```

### Test Scraper Only

```powershell
python scraper.py
```

---

## 📊 Command Line Options

| Command | Description |
|---------|-------------|
| `python monitor.py` | Start continuous monitoring |
| `python monitor.py --once` | Run single check and exit |
| `python monitor.py --test-notify` | Send test notification |
| `python monitor.py --config` | Show configuration |
| `python monitor.py --log-level DEBUG` | Enable debug logging |
| `python api.py` | Start REST API server |
| `python api.py --port 8080` | Start API on custom port |

---

## 🔧 Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'X'"**

```powershell
python -m pip install -r requirements.txt
```

**2. Chrome not found**

- Ensure Google Chrome is installed
- undetected-chromedriver auto-downloads the correct driver

**3. Telegram notifications not working**

- Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`
- Run `python test_telegram.py` to test connection
- Make sure you've started a chat with your bot first

**4. Login wall appearing**

- Facebook may require login for some searches
- Try different search terms or locations
- The scraper will log warnings if this occurs

---

## 📝 Example Workflow

```powershell
# 1. Navigate to project
cd C:\Users\lucas\fb_marketplace_monitor\fb_marketplace_monitor

# 2. Test Telegram first
python test_telegram.py

# 3. Start monitoring
python monitor.py

# The monitor will now:
# - Search for configured keywords every 2 minutes
# - Send Telegram notifications for NEW listings only
# - Save seen listings to avoid duplicates
```

---

## 📂 File Structure

```
fb_marketplace_monitor/
├── .env              # Your configuration (edit this!)
├── .env.example      # Example configuration template
├── api.py            # REST API server
├── config.py         # Configuration loader
├── monitor.py        # Main monitoring script ⭐
├── notifications.py  # Telegram/WhatsApp notifications
├── requirements.txt  # Python dependencies
├── scraper.py        # Facebook Marketplace scraper
├── storage.py        # Tracks seen listings
├── test_telegram.py  # Test Telegram connection
└── verify_chat.py    # Verify Telegram chat ID
```

---

## 🎉 You're Ready

Start monitoring with:

```powershell
cd C:\Users\lucas\fb_marketplace_monitor\fb_marketplace_monitor
python monitor.py
```

Happy hunting! 🛒
