# Facebook Marketplace Monitor 🛒

> **Get instant Telegram/WhatsApp notifications for new Marketplace listings**

---

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies

```bash
cd fb_marketplace_monitor
pip install -r requirements.txt
```

### Step 2: Create Telegram Bot (2 min)

1. **Open Telegram** → Search **@BotFather** → Start chat
2. Send `/newbot` → Follow prompts → **Copy the token**
3. Search **@userinfobot** → Start → **Copy your Chat ID**

### Step 3: Configure

```bash
# Copy template
copy .env.example .env

# Edit .env with your values:
notepad .env
```

**Required settings in `.env`:**

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
SEARCH_KEYWORDS=iphone,macbook,ps5
```

### Step 4: Test & Run

```bash
# Test Telegram connection
python test_telegram.py

# Run single check
python monitor.py --once

# Run continuously
python monitor.py
```

---

## 📱 Get Your Chat ID

**Your Chat ID is NOT the same as your phone number!**

1. Open Telegram
2. Search for **@userinfobot**
3. Click **Start**
4. It replies: `Id: 123456789` ← **This is your Chat ID**

---

## 🔧 Configuration Options

| Setting | Description | Example |
|---------|-------------|---------|
| `SEARCH_KEYWORDS` | Comma-separated terms | `iphone,macbook` |
| `SEARCH_MAX_PRICE` | Price filter | `500` |
| `SEARCH_LOCATION` | City/State | `Denver, CO` |
| `CHECK_INTERVAL_SECONDS` | Time between checks | `300` |

---

## 🌐 API Mode (Optional)

```bash
# Start REST API server
python api.py --port 5000

# Search via API
curl -X POST http://localhost:5000/search -H "Content-Type: application/json" -d '{"query":"iphone"}'

# Start monitoring
curl -X POST http://localhost:5000/monitor/start
```

---

## 🔍 Troubleshooting

| Error | Solution |
|-------|----------|
| `Chat not found` | Wrong Chat ID - Use @userinfobot |
| `Unauthorized` | Wrong bot token |
| `Login wall` | Facebook blocking - try non-headless mode |

---

## 📁 Files

```
fb_marketplace_monitor/
├── monitor.py        # Main CLI
├── api.py           # REST API server
├── test_telegram.py # Quick test
├── .env            # Your config
└── requirements.txt # Dependencies
```

---

**Need help?** Run `python monitor.py --config` to verify your setup.
