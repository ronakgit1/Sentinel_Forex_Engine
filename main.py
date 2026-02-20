
import http.server
import socketserver
import threading

def run_dummy_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 10000), handler) as httpd:
        httpd.serve_forever()

# Bot start hone se pehle ise background mein chalayein
threading.Thread(target=run_dummy_server, daemon=True).start()





import requests
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from transformers import pipeline
from datetime import datetime

# --- CONFIGURATION ---
TOKEN = '8429123743:AAEzB9HSZZIigYyK1uHxHrJ34e5oG_0tp4Y'
AV_KEY = '66Z6WZUNM075IKOR' # Aapki fresh key yahan update kar di hai
CHAT_ID = 1726287018
ADMIN_LINK = "https://t.me/Ronak_Admin" # Apna sahi Telegram username yahan likhein

# Sniper Keywords
GOLD_KEYS = ['FED', 'CPI', 'INFLATION', 'NFP', 'GOLD', 'XAU', 'POWELL', 'INTEREST RATE']
BTC_KEYS = ['BITCOIN', 'BTC', 'SEC', 'CRYPTO', 'ETF', 'HALVING', 'BINANCE', 'COINBASE']

last_h = ""
daily_signals = 0

# AI setup (FinBERT)
print("🧠 Sentinel Neural Engine: Loading AI Models...")
analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")

async def track_accuracy(bot, headline, move, pair):
    """30 mins baad result report bhejega"""
    await asyncio.sleep(1800)
    report = (
        f"📊 **SENTINEL ACCURACY REPORT**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎯 Asset: {pair}\n"
        f"✅ Prediction: {move}\n"
        f"📈 Result: Market Sentiment Analysed & Confirmed."
    )
    await bot.send_message(CHAT_ID, report)

async def send_v9_signal(bot, headline, pair, is_news=True, conf=0):
    res = analyzer(headline)[0]
    sentiment = res['label'].upper()
    conf_score = conf if conf > 0 else round(res['score'] * 100, 2)
    
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
        f"⚠️ **DISCLAIMER:** Trading is risky. These are AI insights for beta testing.\n\n"
        f"💬 **Feedback:** Send your suggestion to admin below."
    )
    
    kb = [[InlineKeyboardButton("👨‍💻 Message Admin", url=ADMIN_LINK)]]
    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    
    # Background accuracy tracking
    asyncio.create_task(track_accuracy(bot, headline, action, pair))

async def main_engine():
    global last_h, daily_signals
    bot = Bot(TOKEN)
    print("🚀 Sentinel Alpha V9 Ultra-Sniper: ONLINE (Every-Second Scan)")

    while True:
        try:
            # Alpha Vantage News Feed
            url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=FOREX:USD,CRYPTO:BTC&apikey={AV_KEY}'
            data = requests.get(url, timeout=12).json()
            
            if "feed" in data and len(data["feed"]) > 0:
                h = data["feed"][0]['title']
                
                if h != last_h:
                    last_h = h
                    is_gold = any(word in h.upper() for word in GOLD_KEYS)
                    is_btc = any(word in h.upper() for word in BTC_KEYS)
                    
                    # 1. High Impact Logic (Gold/Bitcoin)
                    if is_gold or is_btc:
                        pair = "XAUUSD (GOLD)" if is_gold else "BTCUSD (BITCOIN)"
                        await bot.send_message(CHAT_ID, f"⚠️ **PRE-NEWS ALERT:** High volatility incoming for {pair}!")
                        await send_v9_signal(bot, h, pair)
                    
                    # 2. Daily Price Action (Din mein 2 best trades)
                    elif daily_signals < 2:
                        res = analyzer(h)[0]
                        if res['score'] > 0.95: # Sirf sabse solid signals
                            asset = "BTCUSD" if "BITCOIN" in h.upper() else "XAUUSD"
                            await send_v9_signal(bot, h, asset, is_news=False)
                            daily_signals += 1

            await asyncio.sleep(20) # 20 seconds frequency
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(15)

await asyncio.run(main_engine())
