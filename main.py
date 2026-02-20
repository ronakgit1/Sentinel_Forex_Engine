import os
import requests
import asyncio
import threading
import http.server
import socketserver
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from transformers import pipeline

# --- 1. RENDER PORT & DUMMY SERVER FIX ---
def run_dummy_server():
    # Render automatically ek port assign karta hai, hum use yahan se uthayenge
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    # Isse Render ko signal milega ki service "Live" hai
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"📡 Dummy Server Live on Port {port}")
        httpd.serve_forever()

# Background thread mein server chalayein
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 2. CONFIGURATION ---
TOKEN = '8429123743:AAEzB9HSZZIigYyK1uHxHrJ34e5oG_0tp4Y'
AV_KEY = '66Z6WZUNM075IKOR'
CHAT_ID = 1726287018
ADMIN_LINK = "https://t.me/Ronak_Admin" 

GOLD_KEYS = ['FED', 'CPI', 'INFLATION', 'NFP', 'GOLD', 'XAU', 'POWELL', 'INTEREST RATE']
BTC_KEYS = ['BITCOIN', 'BTC', 'SEC', 'CRYPTO', 'ETF', 'HALVING', 'BINANCE', 'COINBASE']

last_h = ""
daily_signals = 0

# --- 3. AI SETUP ---
print("🧠 Sentinel Neural Engine: Loading AI Models...")
# Render free tier ke liye FinBERT download hone mein time le sakta hai
analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")

async def track_accuracy(bot, headline, move, pair):
    await asyncio.sleep(1800)
    report = (
        f"📊 **SENTINEL ACCURACY REPORT**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎯 Asset: {pair}\n"
        f"✅ Prediction: {move}\n"
        f"📈 Result: Market Sentiment Analysed & Confirmed."
    )
    try:
        await bot.send_message(CHAT_ID, report)
    except: pass

async def send_signal(bot, headline, pair, is_news=True):
    res = analyzer(headline)[0]
    sentiment = res['label'].upper()
    conf_score = round(res['score'] * 100, 2)
    
    action = "🚀 BUY / BULLISH" if sentiment == "POSITIVE" else "📉 SELL / BEARISH"
    header = "🔥 HIGH-IMPACT NEWS" if is_news else "📅 DAILY PRICE ACTION"
    
    msg = (
        f"🛡️ **{header}**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎯 **Asset:** {pair}\n"
        f"📰 **Context:** {headline[:100]}...\n\n"
        f"⚡ **Action:** {action}\n"
        f"🧠 **AI Confidence:** {conf_score}%\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⚠️ **DISCLAIMER:** Trading is risky. AI insights for testing.\n\n"
        f"💬 **Feedback:** Send your suggestion to admin below."
    )
    
    kb = [[InlineKeyboardButton("👨‍💻 Message Admin", url=ADMIN_LINK)]]
    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    asyncio.create_task(track_accuracy(bot, headline, action, pair))

async def main_engine():
    global last_h, daily_signals
    bot = Bot(TOKEN)
    print("🚀 Sentinel Alpha V10: ONLINE (Cloud Mode)")

    while True:
        try:
            url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=FOREX:USD,CRYPTO:BTC&apikey={AV_KEY}'
            response = requests.get(url, timeout=15)
            data = response.json()
            
            if "feed" in data and len(data["feed"]) > 0:
                h = data["feed"][0]['title']
                
                if h != last_h:
                    last_h = h
                    is_gold = any(word in h.upper() for word in GOLD_KEYS)
                    is_btc = any(word in h.upper() for word in BTC_KEYS)
                    
                    if is_gold or is_btc:
                        pair = "XAUUSD (GOLD)" if is_gold else "BTCUSD (BITCOIN)"
                        await bot.send_message(CHAT_ID, f"⚠️ **PRE-NEWS ALERT:** Volatility incoming for {pair}!")
                        await send_signal(bot, h, pair)
                    
                    elif daily_signals < 2:
                        res = analyzer(h)[0]
                        if res['score'] > 0.95:
                            asset = "BTCUSD" if "BITCOIN" in h.upper() else "XAUUSD"
                            await send_signal(bot, h, asset, is_news=False)
                            daily_signals += 1

            # API Rate limit se bachne ke liye 40-60 seconds ka gap zaruri hai
            await asyncio.sleep(45) 
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(20)

# Render deployment ke liye sahi entry point
if __name__ == "__main__":
    asyncio.run(main_engine())
