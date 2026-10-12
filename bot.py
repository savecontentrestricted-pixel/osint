import os, threading, traceback, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
load_dotenv()

# Keep-alive for Render
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        html = b"<html><body><h1>OSINT Hunter Hub MINIMAL TEST LIVE</h1><p>Testing polling</p></body></html>"
        self.wfile.write(html)
    def log_message(self, *args): pass

def keepalive():
    try:
        port = int(os.getenv('PORT','10000'))
        print(f"🌐 Keepalive listening on 0.0.0.0:{port}")
        HTTPServer(('0.0.0.0', port), Handler).serve_forever()
    except Exception as e:
        print(f"Keepalive error: {e}")
        traceback.print_exc()

threading.Thread(target=keepalive, daemon=False).start()

# Direct startup notify
try:
    import requests
    token = os.getenv('BOT_TOKEN','')
    admin = os.getenv('ADMIN_ID','8607774564')
    if token:
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': admin, 'text': '🧪 MINIMAL TEST BOT starting...'}, timeout=5)
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': '6919943679', 'text': '🧪 MINIMAL TEST BOT starting for test account...'}, timeout=5)
        print("Startup notify sent")
except Exception as e:
    print(f"Notify failed: {e}")

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv('BOT_TOKEN')

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
🚀 <b>OSINT Hunter Hub - MINIMAL TEST</b>

👋 Hello {user.first_name}!

🔥 11 Tools Grid:

📡 TELEGRAM SCRAPER | 📸 INSTAGRAM OSINT
📧 EMAIL OSINT | 🌐 IP/DOMAIN RECON
🖼️ EXIF | 🔒 SECURITY CHECK
📱 NUMBER INFO | 🆔 TG TOOLS
📝 OCR | 🌐 WEBSITE EXTRACTOR
📊 FILE CONVERTER | 📜 ALL COMMANDS

👇 Grid button dabao (4 dots icon)

👑 Owner: @Supermannn_x
📢 Channel: @osint_xpert

Try /help or click grid!
"""
        await update.message.reply_text(txt, parse_mode='HTML', reply_markup=kb)
        print("Replied to /start")
    except Exception as e:
        print(f"start error: {e}")
        traceback.print_exc()
        try:
            await update.message.reply_text("✅ Bot alive! Minimal test")
        except:
            pass

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Help: /start, /numinfo 9876543210, /ip 8.8.8.8, /domain google.com etc.")

async def grid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"🔘 You clicked: {text}\n\nThis is grid button! Use /start to see all tools.")

def main():
    print("Building app...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, grid_handler))
    print("Starting polling...")
    # Notify that polling starting
    try:
        import requests
        token = os.getenv('BOT_TOKEN','')
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': '8607774564', 'text': '🔄 Polling starting now...'}, timeout=5)
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': '6919943679', 'text': '🔄 Polling starting now for test...'}, timeout=5)
    except:
        pass
    
    app.run_polling(drop_pending_updates=False, stop_signals=None)

if __name__ == "__main__":
    main()
