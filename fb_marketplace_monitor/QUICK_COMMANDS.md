# Quick Reference Commands

## 🚀 Starting the System

### Start API Server (from project directory)

```powershell
cd C:\Users\lucas\fb_marketplace_monitor\fb_marketplace_monitor
python api.py --port 8080
```

### Start Monitoring (after API is running)

```powershell
curl -X POST http://localhost:8080/monitor/start
```

---

## 📊 Check Status

### Quick Health Check

```powershell
curl http://localhost:8080/health
```

### Detailed Status

```powershell
curl http://localhost:8080/status
```

### View Configuration

```powershell
curl http://localhost:8080/config
```

---

## 🔍 View Listings

### Get Last 20 Listings

```powershell
curl http://localhost:8080/listings?limit=20
```

### Get All Listings

```powershell
curl http://localhost:8080/listings?limit=1000
```

---

## 🔔 Test Notifications

### Send Test Message

```powershell
curl -X POST http://localhost:8080/notify -H "Content-Type: application/json" -d "{\"message\": \"Test notification!\"}"
```

### Test Listing Notification

```powershell
curl -X POST http://localhost:8080/notify/listing -H "Content-Type: application/json" -d "{\"title\": \"Test Item\", \"price\": \"$100\", \"location\": \"Missoula, MT\", \"url\": \"https://facebook.com\"}"
```

---

## 🔧 Control Monitor

### Stop Monitoring

```powershell
curl -X POST http://localhost:8080/monitor/stop
```

### Start Monitoring

```powershell
curl -X POST http://localhost:8080/monitor/start
```

---

## 🗑️ Data Management

### Clear All Tracked Listings

```powershell
curl -X DELETE http://localhost:8080/listings
```

### Manual Search

```powershell
curl -X POST http://localhost:8080/search -H "Content-Type: application/json" -d "{\"query\": \"ford f150\", \"max_listings\": 10}"
```

---

## 📝 View Logs

### Live Log Monitoring

```powershell
Get-Content C:\Users\lucas\fb_marketplace_monitor\fb_marketplace_monitor\marketplace_monitor.log -Wait -Tail 50
```

### View Last 50 Lines

```powershell
Get-Content C:\Users\lucas\fb_marketplace_monitor\fb_marketplace_monitor\marketplace_monitor.log -Tail 50
```

---

## 🛑 Shutdown

### Stop Monitoring (graceful)

```powershell
curl -X POST http://localhost:8080/monitor/stop
```

### Stop API Server

Press `Ctrl+C` in the terminal running the API

---

## ⚡ One-Line Full Status Check

```powershell
curl http://localhost:8080/health; curl http://localhost:8080/status
```

---

## 🔐 API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | API info |
| GET | /health | Health check |
| GET | /status | Monitor status |
| GET | /config | Configuration |
| GET | /listings | Get tracked listings |
| DELETE | /listings | Clear all listings |
| POST | /search | Manual search |
| POST | /notify | Test notification |
| POST | /notify/listing | Test listing notification |
| POST | /monitor/start | Start monitoring |
| POST | /monitor/stop | Stop monitoring |

---

## 📍 Key Locations

- **Project Directory:** `C:\Users\lucas\fb_marketplace_monitor\fb_marketplace_monitor`
- **API Server:** `http://localhost:8080`
- **Configuration:** `.env` file
- **Logs:** `marketplace_monitor.log`
- **Database:** `seen_listings.json`
