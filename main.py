import os, requests, asyncio, threading, http.server, socketserver
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler
from datetime import datetime

# --- 1. RENDER PORT FIX ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 2. CONFIG ---
TOKEN = '8429123743:AAEzB9HSZZIigYyK1uHxHrJ34e5oG_0tp4Y'
AV_KEY = '66Z6WZUNM075IKOR'
CHAT_ID = -1003835397825 
ADMIN_LINK = "https://t.me/Ronak_Admin"
# AAPKI NAYI LINK YAHAN UPDATE KAR DI HAI
CH_LINK = "https://t.me/+u-4ClI7OsUszMDZl"

last_h = ""

# --- 3. FUNCTIONS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab koi bot ko /start karega"""
    user_name = update.effective_user.first_name
    msg = (
        f"👋 Hello **{user_name}**!\n\n"
        f"🛡️ **Sentinel Sniper V11** setup complete.\n"
        f"Main Gold aur Crypto market ko monitor kar raha hoon.\n\n"
        f"📢 **Join our Private Channel for Signals:**\n"
        f"{CH_LINK}\n\n"
        f"_(Agar link kaam na kare toh Admin ko message karein)_"
    )
    await update.message.reply_text(msg, parse_mode='Markdown', disable_web_page_preview=False)

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab koi naya member channel join karega"""
    if update.chat_member.new_chat_member.status == "member":
        user = update.chat_member.new_chat_member.user
        await context.bot.send_message(CHAT_ID, f"🎊 Welcome **{user.first_name}** to Sentinel FX Engine! Market signals ke liye taiyar rahein. 📈", parse_mode='Markdown')

async def heartbeat(app):
    """Uptime check every 1 hour"""
    while True:
        try: await app.bot.send_message(CHAT_ID, "✅ **Sentinel System Update:** Monitoring News & Technicals...")
        except: pass
        await asyncio.sleep(3600)

async def engine(app):
    """Main Trading Engine"""
    global last_h
    while True:
        try:
            # 1. News Analysis
            url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=FOREX:USD,CRYPTO:BTC&apikey={AV_KEY}'
            data = requests.get(url, timeout=10).json()
            if "feed" in data and len(data["feed"]) > 0:
                top = data["feed"][0]
                if top['title'] != last_h:
                    last_h = top['title']
                    label = top.get('overall_sentiment_label', 'Neutral')
                    emoji = "🚀 BULLISH" if "BULLISH" in label.upper() else "📉 BEARISH"
                    msg = f"🛡️ **SENTINEL NEWS SIGNAL**\n━━━━━━━━━━━━━━━\n🎯 **Asset:** Gold/BTC\n⚡ **Action:** {emoji}\n📰 {last_h[:110]}...\n━━━━━━━━━━━━━━━\n💬 [Admin]({ADMIN_LINK})"
                    await app.bot.send_message(CHAT_ID, msg, parse_mode='Markdown', disable_web_page_preview=True)
            
            # 2. Technical Analysis (RSI)
            for sym in ["BTC", "GLD"]:
                r = requests.get(f"https://www.alphavantage.co/query?function=RSI&symbol={sym}&interval=daily&time_period=14&series_type=close&apikey={AV_KEY}").json()
                if "Technical Analysis: RSI" in r:
                    val = float(list(r["Technical Analysis: RSI"].values())[0]["RSI"])
                    if val > 70 or val < 30:
                        act = "📉 SELL (Overbought)" if val > 70 else "🚀 BUY (Oversold)"
                        await app.bot.send_message(CHAT_ID, f"📊 **TECHNICAL SIGNAL**\n━━━━━━━━━━━━━━━\n🎯 **Asset:** {sym}\n⚡ **Action:** {act}\n📉 **RSI Level:** {val}\n━━━━━━━━━━━━━━━", parse_mode='Markdown')
            
            await asyncio.sleep(600) 
        except: await asyncio.sleep(60)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatMemberHandler(welcome, ChatMemberHandler.CHAT_MEMBER))
    
    async with app:
        await app.initialize()
        await app.start()
        asyncio.create_task(heartbeat(app))
        asyncio.create_task(engine(app))
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        while True: await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
