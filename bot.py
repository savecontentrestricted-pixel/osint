import os, threading, traceback, asyncio, json
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
PORT = int(os.getenv('PORT','10000'))
WEBHOOK_URL = f"https://osint-hunter-hub-bot.onrender.com/webhook"

# Global app for webhook handling
app = None

class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        if self.path == '/webhook':
            self.wfile.write(b'Webhook endpoint - POST only')
        else:
            html = b"<html><body><h1>OSINT Hunter Hub WEBHOOK MODE LIVE</h1><p>Grid ready</p><p>Webhook: /webhook</p></body></html>"
            self.wfile.write(html)
    
    def do_POST(self):
        try:
            if self.path == '/webhook':
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body)
                # Process update in background
                threading.Thread(target=process_update, args=(data,), daemon=True).start()
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

def process_update(data):
    try:
        # Use asyncio to handle update
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(handle_update(data))
    except Exception as e:
        print(f"process_update error: {e}")
        traceback.print_exc()

async def handle_update(data):
    try:
        from telegram import Update
        global app
        if app:
            update = Update.de_json(data, app.bot)
            await app.process_update(update)
    except Exception as e:
        print(f"handle_update error: {e}")
        traceback.print_exc()

def keepalive():
    try:
        print(f"🌐 Webhook server on 0.0.0.0:{PORT}, webhook URL {WEBHOOK_URL}")
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
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': '8607774564', 'text': '🧪 WEBHOOK MODE starting...'}, timeout=5)
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': '6919943679', 'text': '🧪 WEBHOOK MODE starting...'}, timeout=5)
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
        print(f"START from {user.id}")
        kb = main_keyboard()
        txt = f"""
🚀 <b>OSINT Hunter Hub - WEBHOOK MODE</b>

👋 Hello {user.first_name}!

🔥 11 Tools Grid (Webhook working!):

📡 TELEGRAM SCRAPER | 📸 INSTAGRAM OSINT
📧 EMAIL OSINT | 🌐 IP/DOMAIN RECON
🖼️ EXIF | 🔒 SECURITY CHECK
📱 NUMBER INFO | 🆔 TG TOOLS
📝 OCR | 🌐 WEBSITE EXTRACTOR
📊 FILE CONVERTER | 📜 ALL COMMANDS

👇 Grid button dabao (4 dots icon)

✅ Webhook mode - Instant reply!
👑 Owner: @Supermannn_x
"""
        await update.message.reply_text(txt, parse_mode='HTML', reply_markup=kb)
        print("Replied")
    except Exception as e:
        print(f"start error {e}")
        traceback.print_exc()

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Help: /start etc. Webhook mode live!")

async def grid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔘 You clicked: {update.message.text}\nGrid working!")

def main():
    global app
    print("Building app...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, grid_handler))
    
    # Set webhook
    async def set_webhook():
        try:
            await app.bot.delete_webhook(drop_pending_updates=True)
            await app.bot.set_webhook(url=WEBHOOK_URL, allowed_updates=["message","callback_query"])
            print(f"Webhook set to {WEBHOOK_URL}")
            import requests
            token = os.getenv('BOT_TOKEN','')
            requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': '8607774564', 'text': f'✅ Webhook set to {WEBHOOK_URL}'}, timeout=5)
            requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': '6919943679', 'text': f'✅ Webhook set - Try /start now!'}, timeout=5)
        except Exception as e:
            print(f"Webhook set error: {e}")
            traceback.print_exc()
    
    # Run set_webhook
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_webhook())
    
    print("Webhook mode ready - HTTP server handling updates")
    # Keep main thread alive
    while True:
        time.sleep(60)
        print("Webhook mode alive...")

if __name__ == "__main__":
    import time
    main()
