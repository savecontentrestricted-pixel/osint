import os, threading, traceback, asyncio, json, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
PORT = int(os.getenv('PORT','10000'))
WEBHOOK_URL = f"https://osint-hunter-hub-bot.onrender.com/webhook"

app = None
loop = None

class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        if self.path == '/webhook':
            self.wfile.write(b'Webhook endpoint - POST only, GET works')
        else:
            html = b"<html><body><h1>OSINT Hunter Hub WEBHOOK MODE LIVE - FIXED</h1><p>Grid ready</p><p>Webhook: /webhook POST</p><p>Try /start in Telegram</p></body></html>"
            self.wfile.write(html)
    
    def do_POST(self):
        try:
            if self.path == '/webhook':
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body)
                print(f"📥 Webhook POST received: update_id {data.get('update_id')}")
                # Process synchronously in thread pool
                threading.Thread(target=process_update_sync, args=(data,), daemon=True).start()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"Webhook POST error: {e}")
            traceback.print_exc()
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, *args): pass

def process_update_sync(data):
    try:
        global loop, app
        if loop is None:
            print("No loop!")
            return
        # Schedule coroutine in the main loop
        asyncio.run_coroutine_threadsafe(handle_update(data), loop)
    except Exception as e:
        print(f"process_update_sync error: {e}")
        traceback.print_exc()

async def handle_update(data):
    try:
        from telegram import Update
        global app
        if app:
            update = Update.de_json(data, app.bot)
            print(f"Processing update {update.update_id} type {update.message.text if update.message else 'no text'}")
            await app.process_update(update)
            print(f"Processed update {update.update_id}")
    except Exception as e:
        print(f"handle_update error: {e}")
        traceback.print_exc()
        # Try to notify owner
        try:
            import requests
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data={'chat_id': '8607774564', 'text': f'❌ Webhook handle error: {e}'}, timeout=5)
        except:
            pass

def keepalive():
    try:
        print(f"🌐 Webhook server on 0.0.0.0:{PORT}, webhook {WEBHOOK_URL}")
        HTTPServer(('0.0.0.0', PORT), WebhookHandler).serve_forever()
    except Exception as e:
        print(f"Keepalive error: {e}")
        traceback.print_exc()

threading.Thread(target=keepalive, daemon=False).start()

# Startup notify
try:
    import requests
    token = os.getenv('BOT_TOKEN','')
    if token:
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': '8607774564', 'text': '🧪 WEBHOOK FIXED MODE starting...'}, timeout=5)
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': '6919943679', 'text': '🧪 WEBHOOK FIXED MODE starting...'}, timeout=5)
        print("Startup notify sent")
except Exception as e:
    print(f"Notify failed: {e}")

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

KB_BTNS = [
    ["📡 TELEGRAM SCRAPER", "📸 INSTAGRAM OSINT"],
    ["📧 EMAIL OSINT", "🌐 IP/DOMAIN RECON"],
    ["🖼️ EXIF FORENSICS", "🔒 SECURITY CHECK"],
    ["📱 NUMBER INFO", "🆔 TG NUMBER TOOLS"],
    ["📝 OCR EXTRACTOR", "🌐 WEBSITE EXTRACTOR"],
    ["📊 FILE CONVERTER", "📜 ALL COMMANDS"],
]

def main_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(t) for t in row] for row in KB_BTNS],
        resize_keyboard=True,
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        print(f"START from {user.id} {user.first_name}")
        kb = main_keyboard()
        txt = f"""
🚀 <b>OSINT Hunter Hub - WEBHOOK FIXED</b>

👋 Hello {user.first_name}!

🔥 11 Tools Grid (Webhook Fixed!):

📡 TELEGRAM SCRAPER | 📸 INSTAGRAM OSINT
📧 EMAIL OSINT | 🌐 IP/DOMAIN RECON
🖼️ EXIF | 🔒 SECURITY CHECK
📱 NUMBER INFO | 🆔 TG TOOLS
📝 OCR | 🌐 WEBSITE EXTRACTOR
📊 FILE CONVERTER | 📜 ALL COMMANDS

👇 Grid button dabao (4 dots icon - screenshot wala)

✅ Webhook mode - Instant reply!
👑 Owner: @Supermannn_x
📢 Channel: @osint_xpert

Grid me saare tools hai!
"""
        await update.message.reply_text(txt, parse_mode='HTML', reply_markup=kb)
        print("Replied to /start")
    except Exception as e:
        print(f"start error: {e}")
        traceback.print_exc()

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Help: /start, /numinfo 9876543210, /ip 8.8.8.8, /domain google.com etc. Grid me sab hai!")

async def grid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        print(f"Grid click: {text}")
        await update.message.reply_text(f"🔘 You clicked: {text}\n\n✅ Grid working! All 11 tools in grid like utility bot.\n\nUse /start to see full menu.")
    except Exception as e:
        print(f"grid error {e}")

async def main_async():
    global app, loop
    loop = asyncio.get_running_loop()
    print("Building app...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, grid_handler))
    
    print("Initializing app...")
    await app.initialize()
    await app.start()
    
    print("Setting webhook...")
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        await app.bot.set_webhook(url=WEBHOOK_URL, allowed_updates=["message","callback_query"])
        print(f"Webhook set to {WEBHOOK_URL}")
        import requests
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data={'chat_id': '8607774564', 'text': f'✅ Webhook FIXED set to {WEBHOOK_URL} - Try /start now!'}, timeout=5)
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data={'chat_id': '6919943679', 'text': f'✅ Webhook FIXED - Try /start now!'}, timeout=5)
    except Exception as e:
        print(f"Webhook set error: {e}")
        traceback.print_exc()
    
    print("Webhook mode ready - waiting forever")
    # Keep alive
    while True:
        await asyncio.sleep(60)
        print("Webhook alive...")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
