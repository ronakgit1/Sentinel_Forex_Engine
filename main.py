import os, requests, asyncio, threading, http.server, socketserver
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime

# --- 1. RENDER SERVER ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 2. CONFIG ---
TOKEN = '8429123743:AAEzB9HSZZIigYyK1uHxHrJ34e5oG_0tp4Y'
# API Limit se bachne ke liye 2-3 keys yahan comma laga kar zaroor daalein
API_KEYS = ['66Z6WZUNM075IKOR'] 
CHAT_ID = -1003835397825 
CH_LINK = "https://t.me/+u-4ClI7OsUszMDZl"
ADMIN_LINK = "https://t.me/Ronak_Admin"

# --- 3. EXPERT ENGINE & ACCURACY TRACKER ---

async def get_price(sym, key):
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={sym}&apikey={key}"
        data = requests.get(url, timeout=10).json()
        return float(data["Global Quote"]["05. price"])
    except: return None

async def track_accuracy(app, sym, entry_price, direction):
    """Trade ke 1 ghante baad result check karega"""
    await asyncio.sleep(3600) 
    exit_price = await get_price(sym, API_KEYS[0])
    if exit_price and entry_price:
        change = ((exit_price - entry_price) / entry_price) * 100
        result = "✅ PROFIT" if (direction == "BUY" and change > 0) or (direction == "SELL" and change < 0) else "❌ LOSS/SIDEWAYS"
        accuracy_msg = (
            f"📊 **TRADE RESULT UPDATE**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🎯 **Asset:** {sym}\n"
            f"💰 **Entry:** {entry_price}\n"
            f"📉 **Exit (1h):** {exit_price}\n"
            f"✨ **Result:** {result} ({abs(change):.2f}%)\n"
            f"━━━━━━━━━━━━━━━"
        )
        await app.bot.send_message(CHAT_ID, accuracy_msg, parse_mode='Markdown')

async def trading_engine(app):
    """Background mein trades scan karta rahega (Silent)"""
    while True:
        key = API_KEYS[0]
        for sym in ["BTC", "GLD"]:
            url = f"https://www.alphavantage.co/query?function=RSI&symbol={sym}&interval=60min&time_period=14&series_type=close&apikey={key}"
            data = requests.get(url).json()
            
            if "Technical Analysis: RSI" in data:
                rsi = float(list(data["Technical Analysis: RSI"].values())[0]["RSI"])
                entry_price = await get_price(sym, key)
                
                signal = ""
                direction = ""
                # High Accuracy Thresholds
                if rsi < 38: 
                    signal = "🚀 **EXPERT BUY SIGNAL**"
                    direction = "BUY"
                elif rsi > 62: 
                    signal = "📉 **EXPERT SELL SIGNAL**"
                    direction = "SELL"

                if signal and entry_price:
                    msg = (
                        f"🛡️ {signal}\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"🎯 **Asset:** {sym}\n"
                        f"💵 **Entry Price:** {entry_price}\n"
                        f"📊 **RSI Level:** {rsi:.2f}\n"
                        f"🚦 **Status:** Signal Confirmed\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"💬 [Admin]({ADMIN_LINK})"
                    )
                    await app.bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                    asyncio.create_task(track_accuracy(app, sym, entry_price, direction))
        
        # Har 15-20 min mein market check karega (API limit ke liye safe)
        await asyncio.sleep(1200)

async def heartbeat_6h(app):
    """Har 6 ghante mein status message (As requested)"""
    while True:
        try:
            status = (
                f"🛰️ **SYSTEM STATUS UPDATE**\n"
                f"━━━━━━━━━━━━━━━\n"
                f"✅ **Bot:** Online & Active\n"
                f"📊 **Scanning:** XAUUSD & BTCUSD\n"
                f"🛡️ **Heartbeat:** 6-Hour Cycle\n"
                f"━━━━━━━━━━━━━━━"
            )
            await app.bot.send_message(CHAT_ID, status, parse_mode='Markdown')
        except: pass
        # 21600 seconds = 6 hours
        await asyncio.sleep(21600)

# --- 4. START & MAIN ---
async def start(update, context):
    kb = [[InlineKeyboardButton("📥 JOIN VIP CHANNEL", url=CH_LINK)]]
    await update.message.reply_text("👋 Sentinel V13 Active.\nScanning messages set to 6-hour intervals!", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    async with app:
        await app.initialize()
        await app.start()
        # Tasks start karein
        asyncio.create_task(heartbeat_6h(app))
        asyncio.create_task(trading_engine(app))
        await app.updater.start_polling()
        while True: await asyncio.sleep(100)

if __name__ == "__main__":
    asyncio.run(main())
