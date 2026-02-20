import os
import requests
import asyncio
import threading
import http.server
import socketserver
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from transformers import pipeline

# --- RENDER PORT FIX ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"📡 Web Server Active on Port {port}")
        httpd.serve_forever()

# Start dummy server in background
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- CONFIGURATION ---
TOKEN = '8429123743:AAEzB9HSZZIigYyK1uHxHrJ34e5oG_0tp4Y'
AV_KEY = '66Z6WZUNM075IKOR'
CHAT_ID = 1726287018
ADMIN_LINK = "https://t.me/Ronak_Admin" 

GOLD_KEYS = ['FED', 'CPI', 'INFLATION', 'NFP', 'GOLD', 'XAU', 'POWELL']
BTC_KEYS = ['BITCOIN', 'BTC', 'SEC', 'CRYPTO', 'ETF', 'HALVING', 'BINANCE']

# --- AI SETUP ---
print("🧠 Loading Sentiment Engine...")
analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

last_h = ""

async def send_signal(bot, headline, pair):
    res = analyzer(headline)[0]
    sentiment = res['label'].upper()
    action = "🚀 BUY / BULLISH" if "POSITIVE" in sentiment else "📉 SELL / BEARISH"
    
    msg = (
        f"🛡️ **SENTINEL SNIPER V10**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎯 **Asset:** {pair}\n"
        f"📰 **News:** {headline[:100]}...\n\n"
        f"⚡ **Action:** {action}\n"
        f"🧠 **AI Sentiment:** {sentiment}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💬 **Feedback:** @Ronak_Admin"
    )
    kb = [[InlineKeyboardButton("👨‍💻 Message Admin", url=ADMIN_LINK)]]
    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def main_engine():
    global last_h
    bot = Bot(TOKEN)
    print("🚀 Sentinel V10: Sniper Online...")

    while True:
        try:
            url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=FOREX:USD,CRYPTO:BTC&apikey={AV_KEY}'
            r = requests.get(url, timeout=15)
            data = r.json()
            
            if "feed" in data and len(data["feed"]) > 0:
                h = data["feed"][0]['title']
                if h != last_h:
                    last_h = h
                    is_gold = any(word in h.upper() for word in GOLD_KEYS)
                    is_btc = any(word in h.upper() for word in BTC_KEYS)
                    
                    if is_gold or is_btc:
                        pair = "XAUUSD" if is_gold else "BTCUSD"
                        await send_signal(bot, h, pair)
            
            await asyncio.sleep(60) 
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(20)

# --- CORRECT SYNTAX FOR RENDER ---
if __name__ == "__main__":
    asyncio.run(main_engine())
