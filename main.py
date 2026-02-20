import os
import requests
import asyncio
import threading
import http.server
import socketserver

# --- 1. RENDER PORT FIX ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"📡 Light Service Active on Port {port}")
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 2. CONFIGURATION ---
TOKEN = '8429123743:AAEzB9HSZZIigYyK1uHxHrJ34e5oG_0tp4Y'
AV_KEY = '66Z6WZUNM075IKOR'
CHAT_ID = 1726287018
ADMIN_LINK = "https://t.me/Ronak_Admin" 

GOLD_KEYS = ['FED', 'CPI', 'INFLATION', 'NFP', 'GOLD', 'XAU', 'POWELL']
BTC_KEYS = ['BITCOIN', 'BTC', 'SEC', 'CRYPTO', 'ETF', 'HALVING', 'BINANCE']

last_h = ""

async def send_v11_signal(headline, pair, score, sentiment):
    # Sentiment text fix
    emoji = "🚀 BULLISH" if "BULLISH" in sentiment.upper() else "📉 BEARISH"
    msg = (
        f"🛡️ **SENTINEL SNIPER V11 (Cloud Mode)**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎯 **Asset:** {pair}\n"
        f"📰 **News:** {headline[:110]}...\n\n"
        f"⚡ **Signal:** {emoji}\n"
        f"🧠 **AI Score:** {score}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💬 **Admin:** {ADMIN_LINK}"
    )
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown"
    requests.get(url)

async def main_engine():
    global last_h
    print("🚀 Sentinel V11: Cloud Engine Online...")
    while True:
        try:
            url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=FOREX:USD,CRYPTO:BTC&apikey={AV_KEY}'
            data = requests.get(url, timeout=15).json()
            if "feed" in data and len(data["feed"]) > 0:
                top_news = data["feed"][0]
                h = top_news['title']
                if h != last_h:
                    last_h = h
                    is_gold = any(word in h.upper() for word in GOLD_KEYS)
                    is_btc = any(word in h.upper() for word in BTC_KEYS)
                    if is_gold or is_btc:
                        pair = "GOLD" if is_gold else "BITCOIN"
                        score = top_news.get('overall_sentiment_score', '0.0')
                        label = top_news.get('overall_sentiment_label', 'Neutral')
                        await send_v11_signal(h, pair, score, label)
            await asyncio.sleep(60) 
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(20)

if __name__ == "__main__":
    asyncio.run(main_engine())
# Bot commands handler (Add this inside main_engine)
from telegram.ext import Application, CommandHandler

async def start(update, context):
    await update.message.reply_text("🛡️ Sentinel V11 Active! I am monitoring Gold & BTC news for you.")

# Use this to handle commands
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
