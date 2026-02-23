import os, requests, asyncio, threading, http.server, socketserver
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler
from datetime import datetime

# --- 1. RENDER SERVER ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 2. CONFIG ---
TOKEN = '8429123743:AAEzB9HSZZIigYyK1uHxHrJ34e5oG_0tp4Y'
AV_KEY = '66Z6WZUNM075IKOR'
CHAT_ID = -1003835397825 
CH_LINK = "https://t.me/+u-4ClI7OsUszMDZl"
ADMIN_LINK = "https://t.me/Ronak_Admin"

# Keywords for News
GOLD_KEYS = ['GOLD', 'XAU', 'FED', 'INFLATION', 'USD']
BTC_KEYS = ['BTC', 'CRYPTO', 'BITCOIN', 'BINANCE']
last_news_title = ""

# --- 3. FUNCTIONS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📥 JOIN TELEGRAM CHANNEL", url=CH_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user_name = update.effective_user.first_name
    msg = f"👋 **Welcome {user_name}!**\n\n🛡️ **Sentinel Sniper V11** is Online.\nMonitoring Gold, Crypto & Forex 24/7.\n\nClick below to join VIP Channel 👇"
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')

async def welcome_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.chat_member.new_chat_member.status == "member":
        user = update.chat_member.new_chat_member.user
        welcome_text = f"🎊 **Welcome {user.first_name} to Sentinel FX Engine!**\nReal-time signals are being scanned. Stay tuned! 🚀"
        await context.bot.send_message(CHAT_ID, welcome_text, parse_mode='Markdown')

async def heartbeat(app):
    while True:
        now = datetime.now().strftime("%H:%M")
        status_msg = f"🛰️ **SENTINEL SYSTEM UPDATE**\n━━━━━━━━━━━━━━\n⏰ **Time:** {now} IST\n📡 **Status:** Scanning Active\n📊 **Assets:** XAU, BTC, EURUSD, USDJPY\n━━━━━━━━━━━━━━"
        try: await app.bot.send_message(CHAT_ID, status_msg, parse_mode='Markdown')
        except: pass
        await asyncio.sleep(3600)

async def trading_engine(app):
    global last_news_title
    while True:
        try:
            # A. TECHNICAL RSI SIGNALS (Every 5 Mins)
            for sym in ["BTC", "GLD", "EURUSD", "USDJPY"]:
                url = f"https://www.alphavantage.co/query?function=RSI&symbol={sym}&interval=60min&time_period=14&series_type=close&apikey={AV_KEY}"
                r = requests.get(url, timeout=10).json()
                if "Technical Analysis: RSI" in r:
                    rsi = float(list(r["Technical Analysis: RSI"].values())[0]["RSI"])
                    if rsi > 60 or rsi < 40:
                        signal = "📉 SELL" if rsi > 60 else "🚀 BUY"
                        msg = f"🔔 **TECHNICAL SIGNAL**\n━━━━━━━━━━━━━━\n🎯 **Asset:** {sym}\n⚡ **Action:** {signal}\n📊 **RSI:** {rsi}\n━━━━━━━━━━━━━━\n💬 [Admin]({ADMIN_LINK})"
                        await app.bot.send_message(CHAT_ID, msg, parse_mode='Markdown', disable_web_page_preview=True)

            # B. NEWS SENTIMENT SIGNALS
            news_url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=FOREX:USD,CRYPTO:BTC&apikey={AV_KEY}'
            n_data = requests.get(news_url, timeout=10).json()
            if "feed" in n_data and len(n_data["feed"]) > 0:
                top_news = n_data["feed"][0]
                if top_news['title'] != last_news_title:
                    last_news_title = top_news['title']
                    label = top_news.get('overall_sentiment_label', 'Neutral')
                    if "BULLISH" in label.upper() or "BEARISH" in label.upper():
                        emoji = "🚀 BULLISH" if "BULLISH" in label.upper() else "📉 BEARISH"
                        msg = f"🛡️ **NEWS SIGNAL**\n━━━━━━━━━━━━━━\n📰 {last_news_title[:100]}...\n⚡ **Sentiment:** {emoji}\n━━━━━━━━━━━━━━\n💬 [Admin]({ADMIN_LINK})"
                        await app.bot.send_message(CHAT_ID, msg, parse_mode='Markdown', disable_web_page_preview=True)
            
            await asyncio.sleep(300) # Scan every 5 minutes
        except: await asyncio.sleep(60)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatMemberHandler(welcome_member, ChatMemberHandler.CHAT_MEMBER))
    async with app:
        await app.initialize()
        await app.start()
        asyncio.create_task(heartbeat(app))
        asyncio.create_task(trading_engine(app))
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        while True: await asyncio.sleep(100)

if __name__ == "__main__":
    asyncio.run(main())
