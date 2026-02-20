import os
import requests
import asyncio
import threading
import http.server
import socketserver
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- 1. RENDER PORT FIX (Dummy Server) ---
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
# Aapki updated Channel ID
CHAT_ID = -1003835397825 
ADMIN_LINK = "https://t.me/Ronak_Admin" 

GOLD_KEYS = ['FED', 'CPI', 'INFLATION', 'NFP', 'GOLD', 'XAU', 'POWELL']
BTC_KEYS = ['BITCOIN', 'BTC', 'SEC', 'CRYPTO', 'ETF', 'HALVING', 'BINANCE']

last_h = ""

# --- 3. COMMAND HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Logon ko /start par reply karega"""
    await update.message.reply_text(
        "🛡️ **Sentinel Alpha V11 Active!**\n\n"
        "Main 24/7 Gold aur Bitcoin ki news scan kar raha hoon.\n"
        "Signals hamare private channel mein aayenge.",
        parse_mode='Markdown'
    )

# --- 4. CORE ENGINE (News Scanning) ---
async def fetch_news_and_signal(application: Application):
    global last_h
    print("🚀 Sentinel News Engine: Online...")
    
    while True:
        try:
            url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=FOREX:USD,CRYPTO:BTC&apikey={AV_KEY}'
            r = requests.get(url, timeout=15)
            data = r.json()
            
            if "feed" in data and len(data["feed"]) > 0:
                top_news = data["feed"][0]
                h = top_news['title']
                
                if h != last_h:
                    last_h = h
                    is_gold = any(word in h.upper() for word in GOLD_KEYS)
                    is_btc = any(word in h.upper() for word in BTC_KEYS)
                    
                    if is_gold or is_btc:
                        pair = "GOLD (XAUUSD)" if is_gold else "BITCOIN (BTCUSD)"
                        score = top_news.get('overall_sentiment_score', '0.0')
                        sentiment = top_news.get('overall_sentiment_label', 'Neutral')
                        
                        emoji = "🚀 BULLISH" if "BULLISH" in sentiment.upper() else "📉 BEARISH"
                        
                        msg = (
                            f"🛡️ **SENTINEL SNIPER V11**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"🎯 **Asset:** {pair}\n"
                            f"📰 **News:** {h[:110]}...\n\n"
                            f"⚡ **Signal:** {emoji}\n"
                            f"🧠 **AI Score:** {score}\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"💬 **Admin:** [Contact Here]({ADMIN_LINK})"
                        )
                        
                        # Channel mein signal bhejna
                        await application.bot.send_message(
                            chat_id=CHAT_ID, 
                            text=msg, 
                            parse_mode='Markdown',
                            disable_web_page_preview=True
                        )
            
            await asyncio.sleep(60) # 1 minute check
        except Exception as e:
            print(f"Error in Engine: {e}")
            await asyncio.sleep(20)

# --- 5. MAIN ENTRY POINT ---
async def main():
    # Application setup
    application = Application.builder().token(TOKEN).build()
    
    # Commands add karein
    application.add_handler(CommandHandler("start", start))
    
    # Dono kaam ek saath (Commands check karna + News scan karna)
    async with application:
        await application.initialize()
        await application.start()
        print("✅ Bot and Commands initialized.")
        
        # News engine ko background task ki tarah chalana
        asyncio.create_task(fetch_news_and_signal(application))
        
        # Bot ko "Polling" mode mein rakhein taaki band na ho
        await application.updater.start_polling()
        
        # Service ko hamesha ke liye chalu rakhne ke liye
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
