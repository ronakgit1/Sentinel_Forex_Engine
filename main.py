import os
import requests
import asyncio
import threading
import http.server
import socketserver
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler
from datetime import datetime

# --- 1. RENDER PORT FIX ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"📡 Web Service Active on Port {port}")
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 2. CONFIGURATION ---
TOKEN = '8429123743:AAEzB9HSZZIigYyK1uHxHrJ34e5oG_0tp4Y'
AV_KEY = '66Z6WZUNM075IKOR'
CHAT_ID = -1003835397825 
ADMIN_LINK = "https://t.me/Ronak_Admin"
CHANNEL_LINK = "https://t.me/+7fN4vWk-S1Y5MWRl" # Aapki Invite Link

GOLD_KEYS = ['FED', 'CPI', 'INFLATION', 'NFP', 'GOLD', 'XAU', 'POWELL', 'USD', 'RATE']
BTC_KEYS = ['BITCOIN', 'BTC', 'SEC', 'CRYPTO', 'ETF', 'HALVING', 'BINANCE']

last_h = ""

# --- 3. INTERACTIVE RESPONSES (Start & Welcome) ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab koi bot ko /start karega"""
    user_name = update.effective_user.first_name
    welcome_text = (
        f"👋 Hello {user_name}!\n\n"
        f"🛡️ **Sentinel Sniper V11** mein aapka swagat hai.\n"
        f"Main 24/7 Gold aur Crypto markets ko scan karta hoon.\n\n"
        f"📢 **Imp Step:** Saare live signals ke liye hamara Private Channel join karein:\n"
        f"👉 [JOIN CHANNEL HERE]({CHANNEL_LINK})"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown', disable_web_page_preview=True)

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab koi channel join karega"""
    result = update.chat_member
    if result.new_chat_member.status == "member":
        user = result.new_chat_member.user
        welcome_msg = f"🎊 Welcome {user.first_name} to **Sentinel FX Engine**! Market signals ke liye taiyar rahein. 📈"
        await context.bot.send_message(chat_id=CHAT_ID, text=welcome_msg, parse_mode='Markdown')

# --- 4. PRICE ACTION & NEWS LOGIC ---

async def get_price_action_signal(symbol):
    try:
        url = f"https://www.alphavantage.co/query?function=RSI&symbol={symbol}&interval=daily&time_period=14&series_type=close&apikey={AV_KEY}"
        data = requests.get(url, timeout=10).json()
        if "Technical Analysis: RSI" in data:
            latest_date = list(data["Technical Analysis: RSI"].keys())[0]
            rsi = float(data["Technical Analysis: RSI"][latest_date]["RSI"])
            if rsi > 70: return "📉 SELL (Overbought)", rsi
            if rsi < 30: return "🚀 BUY (Oversold)", rsi
        return None, None
    except: return None, None

async def heartbeat(application: Application):
    """System Uptime Status"""
    while True:
        try:
            now = datetime.now().strftime("%H:%M")
            await application.bot.send_message(chat_id=CHAT_ID, text=f"✅ **Sentinel System Update**\nTime: {now}\nStatus: Online & Scanning...", parse_mode='Markdown')
        except: pass
        await asyncio.sleep(3600)

async def main_engine(application: Application):
    global last_h
    while True:
        try:
            # 1. News Signals
            url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=FOREX:USD,CRYPTO:BTC&apikey={AV_KEY}'
            data = requests.get(url, timeout=15).json()
            if "feed" in data and len(data["feed"]) > 0:
                top = data["feed"][0]
                if top['title'] != last_h:
                    last_h = top['title']
                    is_gold = any(w in last_h.upper() for w in GOLD_KEYS)
                    is_btc = any(w in last_h.upper() for w in BTC_KEYS)
                    if is_gold or is_btc:
                        pair = "GOLD (XAUUSD)" if is_gold else "BITCOIN (BTCUSD)"
                        label = top.get('overall_sentiment_label', 'Neutral')
                        score = top.get('overall_sentiment_score', '0.0')
                        emoji = "🚀 BULLISH" if "BULLISH" in label.upper() else "📉 BEARISH"
                        msg = f"🛡️ **NEWS SIGNAL**\n━━━━━━━━━━━━━━━\n🎯 **Asset:** {pair}\n⚡ **Action:** {emoji}\n📰 {last_h[:100]}...\n━━━━━━━━━━━━━━━\n💬 [Admin]({ADMIN_LINK})"
                        await application.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown', disable_web_page_preview=True)
            
            # 2. Daily Price Action Check
            for asset in ["BTC", "GLD"]: # GLD is Gold ETF for RSI
                signal, rsi = await get_price_action_signal(asset)
                if signal:
                    msg = f"📊 **PRICE ACTION**\n━━━━━━━━━━━━━━━\n🎯 **Asset:** {asset}\n⚡ **Action:** {signal}\n📉 **RSI:** {rsi}\n━━━━━━━━━━━━━━━\n💬 [Admin]({ADMIN_LINK})"
                    await application.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
            
            await asyncio.sleep(300) # Check every 5 mins to save API limits
        except: await asyncio.sleep(30)

# --- 5. MAIN ENTRY ---
async def main():
    application = Application.builder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))
    
    async with application:
        await application.initialize()
        await application.start()
        
        # Start Background Tasks
        asyncio.create_task(main_engine(application))
        asyncio.create_task(heartbeat(application))
        
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        while True: await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
