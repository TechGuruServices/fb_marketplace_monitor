"""
Quick Telegram Test Script
Run: python test_telegram.py
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_telegram():
    try:
        from telegram import Bot
        
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            print("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env")
            return False
        
        print(f"📱 Bot Token: {bot_token[:20]}...")
        print(f"💬 Chat ID: {chat_id}")
        
        bot = Bot(token=bot_token)
        
        # Send test message
        message = (
            "🎉 *Facebook Marketplace Monitor Test*\n\n"
            "✅ Telegram notifications are working!\n\n"
            "📦 *Sample Listing:*\n"
            "💰 $150\n"
            "📍 Montana, USA\n"
            "🔗 Ready to monitor!"
        )
        
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="Markdown"
        )
        
        print("✅ Test message sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_telegram())
