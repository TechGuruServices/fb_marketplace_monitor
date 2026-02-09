"""
Verify Telegram Chat ID - Gets user info
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_chat():
    try:
        from telegram import Bot
        
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        print(f"🔍 Verifying Chat ID: {chat_id}")
        
        bot = Bot(token=bot_token)
        
        # Get chat info
        chat = await bot.get_chat(chat_id)
        
        print(f"\n✅ Chat Found!")
        print(f"   Type: {chat.type}")
        print(f"   First Name: {chat.first_name or 'N/A'}")
        print(f"   Last Name: {chat.last_name or 'N/A'}")
        print(f"   Username: @{chat.username}" if chat.username else "   Username: N/A")
        print(f"   ID: {chat.id}")
        
        # Check for Zempel
        if chat.last_name and "Zempel" in chat.last_name:
            print(f"\n🎉 Confirmed: User is {chat.first_name} {chat.last_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(verify_chat())
