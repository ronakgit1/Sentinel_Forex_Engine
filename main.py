import os, requests, asyncio, threading, http.server, socketserver
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler
from datetime import datetime

# --- 1. RENDER SERVER (UptimeRobot ke liye) ---
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

# --- 3. PROFESSIONAL FUNCTIONS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start karne par Stylish Button ke sath link"""
    keyboard = [[InlineKeyboardButton("📥 JOIN TELEGRAM CHANNEL", url=CH_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    user_name = update.effective_user.first_name
    msg = (
        f"👋 **Welcome {user_name}!**\n\n"
        f"🛡️ **Sentinel Sniper V11** is now Online.\n"
        f"Main Gold (XAUUSD) aur Crypto markets ko 24/7 monitor karta hoon.\n\n"
        f"Niche diye gaye button par click karke VIP channel join karein 👇"
    )
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')

async def welcome_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Channel join karne par Welcome message (Bot & Channel dono mein)"""
    if update.chat_member.new_chat_member.status == "member":
        user = update.chat_member.new_chat_member.user
        welcome_text = f"🎊 **Welcome {user.first_name} to Sentinel FX Engine!**\nSahi jagah aaye ho, ab signals ka intezar karo. 🚀"
        
        # 1. Channel mein message
        await context.bot.send_message(CHAT_ID, welcome_text, parse_mode='Markdown')
        # 2. User ko personal message (agar usne bot start kiya hai)
        try:
            await context.bot.send_message(user.id, f"Dhanyawad {user.first_name} channel join karne ke liye! Main active hoon. ✅")
        except: pass

async def heartbeat(app):
    """Har 1 ghante mein Professional Update"""
    while True:
        now = datetime.now().strftime("%H:%M")
        status_msg = (
            f"🛰️ **SENTINEL SYSTEM UPDATE**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏰ **Time:** {now} IST\n"
            f"📡 **Status:** All Systems Nominal\n"
            f"📊 **Scanning:** XAUUSD & BTCUSD\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✅ *Bot is Active and Monitoring...*"
        )
        try:
            await app.bot.send_message(CHAT_ID, status_msg, parse_mode='Markdown')
        except: pass
        await asyncio.sleep(3600)

async def trading_engine(app):
    """Technical Trading Logic"""
    while True:
        try:
            for sym in ["BTC", "GLD"]:
                url = f"https://www.alphavantage.co/query?function=RSI&symbol={sym}&interval=60min&time_period=14&series_type=close&apikey={AV_KEY}"
                r = requests.get(url, timeout=10).json()
                if "Technical Analysis: RSI" in r:
                    rsi = float(list(r["Technical Analysis: RSI"].values())[0]["RSI"])
                    if rsi > 65 or rsi < 35:
                        signal = "📉 SELL" if rsi > 65 else "🚀 BUY"
                        msg = f"🔔 **NEW SIGNAL**\nAsset: {sym}\nAction: {signal}\nRSI: {rsi}\n[Contact Admin]({ADMIN_LINK})"
                        await app.bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
            await asyncio.sleep(900) 
        except: await asyncio.sleep(60)

# --- 4. MAIN EXECUTION ---
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
