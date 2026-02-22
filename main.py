import os, requests, asyncio, threading, http.server, socketserver
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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

# --- 3. TRADING ENGINE (MORE SENSITIVE) ---
async def get_signals(app):
    while True:
        try:
            # Bitcoin & Gold Technical Check
            for sym in ["BTC", "GLD"]:
                url = f"https://www.alphavantage.co/query?function=RSI&symbol={sym}&interval=60min&time_period=14&series_type=close&apikey={AV_KEY}"
                data = requests.get(url, timeout=10).json()
                
                if "Technical Analysis: RSI" in data:
                    latest = list(data["Technical Analysis: RSI"].values())[0]
                    rsi = float(latest["RSI"])
                    
                    # More sensitive levels: 65 and 35
                    if rsi > 65:
                        await app.bot.send_message(CHAT_ID, f"📉 **SENTINEL SELL ALERT**\nAsset: {sym}\nReason: RSI Overbought ({rsi})\nStrategy: Price Action")
                    elif rsi < 35:
                        await app.bot.send_message(CHAT_ID, f"🚀 **SENTINEL BUY ALERT**\nAsset: {sym}\nReason: RSI Oversold ({rsi})\nStrategy: Price Action")
            
            # 15 minute ka wait taaki API limit na khatam ho
            await asyncio.sleep(900) 
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(60)

async def start(update, context):
    await update.message.reply_text("🛡️ Sentinel Active! Monitoring BTC & Gold every 15 mins.")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    async with app:
        await app.initialize()
        await app.start()
        asyncio.create_task(get_signals(app))
        await app.updater.start_polling()
        while True: await asyncio.sleep(100)

if __name__ == "__main__":
    asyncio.run(main())
