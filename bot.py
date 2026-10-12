"""
🚀 OSINT Hunter Hub - @osint_hunter_hub_bot
Advanced High-Level OSINT Tools Hub - 11 Tools

Owner: 8607774564 @Supermannn_x
Force Channel: -1004393596502 @osint_xpert
Repo: savecontentrestricted-pixel/osint

This is ADVANCED version - no one's bot has this level code:
- Max data extraction
- Beautiful formatting with spaces, emojis, styles
- Force join channel
- FloodWait protection
- Export JSON/CSV/PDF
- 11 Tools in one bot

Tools:
1. Telegram Channel Scraper (Advanced)
2. Instagram OSINT
3. Email OSINT
4. IP & Domain Recon
5. Image EXIF Forensics
6. Social Media Security Checker
7. Number Info (Same as utility-duniya-bot)
8. TG Tools (Telegram + Pak Number)
9. OCR Extractor (Image to Text)
10. Website Extractor (Email/Phone/Links/Meta)
11. Excel to PDF + File Converter Hub
"""

import os
import asyncio
import logging
import json
import tempfile
import time
from datetime import datetime
from pathlib import Path

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
            self.wfile.write(b'Webhook endpoint - POST only')
        else:
            html = b"<html><body><h1>OSINT Hunter Hub FULL 11 TOOLS WEBHOOK LIVE - GRID 2-col</h1><p>All 11 tools working</p><p>Webhook: /webhook</p></body></html>"
            self.wfile.write(html)
    
    def do_POST(self):
        try:
            if self.path == '/webhook':
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body)
                print(f"WEBHOOK POST update_id {data.get('update_id')}")
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
        global loop
        if loop:
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
            await app.process_update(update)
    except Exception as e:
        print(f"handle_update error: {e}")
        traceback.print_exc()

def keepalive():
    try:
        print(f"WEBHOOK server on 0.0.0.0:{PORT} -> {WEBHOOK_URL}")
        HTTPServer(('0.0.0.0', PORT), WebhookHandler).serve_forever()
    except Exception as e:
        print(f"Keepalive error: {e}")
        traceback.print_exc()

threading.Thread(target=keepalive, daemon=False).start()

try:
    import requests
    token = os.getenv('BOT_TOKEN','')
    if token:
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': '8607774564', 'text': '🚀 FULL 11 TOOLS WEBHOOK GRID starting...'}, timeout=5)
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': '6919943679', 'text': '🚀 FULL 11 TOOLS WEBHOOK GRID starting...'}, timeout=5)
except Exception as e:
    print(f"Notify failed: {e}")

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from telegram.constants import ParseMode
from telegram.error import BadRequest

# ========== GRID MENU - Like utility-duniya-bot (2 columns grid) ==========
# This is the grid that appears when user clicks the 4-dots menu button at bottom
KB_BTNS = [
    ["📡 TELEGRAM SCRAPER", "📸 INSTAGRAM OSINT"],
    ["📧 EMAIL OSINT", "🌐 IP/DOMAIN RECON"],
    ["🖼️ EXIF FORENSICS", "🔒 SECURITY CHECK"],
    ["📱 NUMBER INFO", "🆔 TG NUMBER TOOLS"],
    ["📝 OCR EXTRACTOR", "🌐 WEBSITE EXTRACTOR"],
    ["📊 FILE CONVERTER", "📜 ALL COMMANDS"],
    ["👑 OWNER", "📢 CHANNEL"],
]

def main_keyboard(admin: bool = False):
    """Grid keyboard like utility-duniya-bot - 2 columns"""
    rows = [row[:] for row in KB_BTNS]
    # Admin gets extra row if needed
    try:
        return ReplyKeyboardMarkup(
            [[KeyboardButton(t) for t in row] for row in rows],
            resize_keyboard=True,
        )
    except Exception as e:
        print(f"Keyboard create failed: {e}")
        # Fallback simple keyboard
        return ReplyKeyboardMarkup(
            [[KeyboardButton(t) for t in row] for row in rows[:4]],
            resize_keyboard=True,
        )

def kb_for(uid: int):
    is_admin_user = False
    try:
        is_admin_user = config.is_admin(uid)
    except:
        is_admin_user = (uid == config.ADMIN_ID)
    return main_keyboard(admin=is_admin_user)

# Button text -> internal mode mapping
BTN_MODE_MAP = {
    "TELEGRAM SCRAPER": "scraper",
    "CHANNEL SCRAPER": "scraper",
    "TELEGRAM CHANNEL": "scraper",
    "INSTAGRAM OSINT": "insta",
    "INSTA OSINT": "insta",
    "INSTAGRAM": "insta",
    "EMAIL OSINT": "email",
    "EMAIL": "email",
    "IP/DOMAIN RECON": "ip",
    "IP DOMAIN": "ip",
    "IP RECON": "ip",
    "DOMAIN RECON": "domain",
    "EXIF FORENSICS": "exif",
    "EXIF": "exif",
    "IMAGE EXIF": "exif",
    "SECURITY CHECK": "security",
    "SECURITY CHECKER": "security",
    "SECURITY": "security",
    "NUMBER INFO": "numinfo",
    "NUMBER": "numinfo",
    "NUM INFO": "numinfo",
    "TG NUMBER TOOLS": "tgtools",
    "TG TOOLS": "tgtools",
    "TELEGRAM TOOLS": "tgtools",
    "OCR EXTRACTOR": "ocr",
    "OCR": "ocr",
    "WEBSITE EXTRACTOR": "wextract",
    "WEBSITE": "wextract",
    "FILE CONVERTER": "converter",
    "EXCEL TO PDF": "converter",
    "FILE": "converter",
    "ALL COMMANDS": "help",
    "HELP": "help",
    "COMMANDS": "help",
    "OWNER": "owner",
    "CHANNEL": "channel",
}

# Prompt texts for grid tools (like utility bot)
GRID_PROMPTS = {
    "scraper": {
        "head": "📡 TELEGRAM CHANNEL SCRAPER",
        "ask": "Channel username bhejo with limit:",
        "ex": "/scrape @durov 50",
        "tip": "5 channels ek saath: /batch @ch1 @ch2 30",
        "cmds": "/channel_info @channel → Full info\n/scrape @channel 100 → Messages\n/scrape_search @channel keyword 50 → Search\n/scrape_media @channel 30 → Only media\n/stats @channel → Top 10 most viewed\n/batch @ch1 @ch2 30 → Multiple"
    },
    "insta": {
        "head": "📸 INSTAGRAM OSINT",
        "ask": "Instagram username bhejo:",
        "ex": "/insta @instagram",
        "tip": "Public profile ka full data milega",
        "cmds": "/insta @username → Followers, bio, posts, full name"
    },
    "email": {
        "head": "📧 EMAIL OSINT",
        "ask": "Email bhejo:",
        "ex": "/email test@gmail.com",
        "tip": "Validation + Disposable + Gravatar + Breach + MX",
        "cmds": "/email test@gmail.com"
    },
    "ip": {
        "head": "🌐 IP & DOMAIN RECON",
        "ask": "IP ya Domain bhejo:",
        "ex": "/ip 8.8.8.8 ya /domain google.com",
        "tip": "Location + ISP + VPN/Proxy + DNS + WHOIS + SSL",
        "cmds": "/ip 8.8.8.8 → IP info\n/domain google.com → Full recon\n/dns google.com → DNS\n/whois google.com → WHOIS\n/ssl google.com → SSL cert"
    },
    "exif": {
        "head": "🖼️ EXIF FORENSICS",
        "ask": "Photo ko File/Document ke roop me bhejo:",
        "ex": "Photo → GPS + Camera + Date + Photoshop check",
        "tip": "File ke roop me bhejo, gallery se nahi",
        "cmds": "Photo bhejo as Document → EXIF analysis"
    },
    "security": {
        "head": "🔒 SECURITY CHECKER",
        "ask": "Username bhejo:",
        "ex": "/igsecure @username",
        "tip": "Security Score 0-100 + leak check",
        "cmds": "/igsecure @username → Security report"
    },
    "numinfo": {
        "head": "📱 NUMBER INFO (Utility Wala)",
        "ask": "10 Digit Number bhejo:",
        "ex": "/numinfo 9204507743",
        "tip": "+91 ya 0 lagane ki zarurat nahi",
        "cmds": "/numinfo 9876543210 → Name, Father, Address, Circle, Aadhaar masked\nSame as @utility_duniya_bot"
    },
    "tgtools": {
        "head": "🆔 TG NUMBER TOOLS",
        "ask": "Telegram username ya Pak number bhejo:",
        "ex": "/tginfo @durov ya /paknum 03001234567",
        "tip": "Telegram + Pak number info",
        "cmds": "/tginfo @username → TG info\n/paknum 0300... → Pak number / CNIC"
    },
    "ocr": {
        "head": "📝 OCR EXTRACTOR",
        "ask": "Photo bhejo with caption 'ocr':",
        "ex": "Photo + caption me ocr likho",
        "tip": "Hindi + English text extraction",
        "cmds": "Photo bhejo + caption 'ocr' → Text niklega"
    },
    "wextract": {
        "head": "🌐 WEBSITE EXTRACTOR",
        "ask": "Website URL bhejo:",
        "ex": "/wextract https://example.com",
        "tip": "Emails + Phones + Links + Meta tags",
        "cmds": "/wextract https://site.com"
    },
    "converter": {
        "head": "📊 FILE CONVERTER HUB",
        "ask": "File bhejo as Document:",
        "ex": "Excel/CSV/Image/PDF",
        "tip": "Caption me conversion type likho",
        "cmds": "Excel file + caption 'excel2pdf' → PDF\n'csv2excel' → CSV to Excel\n'excel2csv' → Excel to CSV\n'img2pdf' → Image to PDF\n'pdf2text' → PDF to Text"
    },
}

import config
from modules.telegram_scraper import TelegramScraper
from modules.ip_domain_recon import ip_lookup, dns_lookup, whois_lookup, ssl_check, full_recon
from modules.image_exif import analyze_exif, exif_to_text
from modules.instagram_osint import instagram_osint
from modules.email_osint import email_osint
from modules.social_security_checker import social_security_check, security_report_text
from modules.number_info import lookup_number, format_card as numinfo_format
from modules.telegram_tools import lookup_tg, lookup_pak, format_tg_card, format_pak_card
from modules.ocr_extractor import ocr_image
from modules.website_extractor import website_extractor
from modules.file_converter import excel_to_pdf, csv_to_excel, excel_to_csv, images_to_pdf, pdf_to_text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global scraper instance
scraper: TelegramScraper = None

def get_scraper() -> TelegramScraper:
    global scraper
    if scraper is None:
        if not config.API_ID or not config.API_HASH or not config.SESSION_STRING:
            raise Exception("API_ID/API_HASH/SESSION_STRING missing - Telegram scraper ke liye my.telegram.org se lo aur generate_session.py chalao")
        scraper = TelegramScraper(config.API_ID, config.API_HASH, config.SESSION_STRING)
    return scraper

# ========== FORCE JOIN CHECK ==========
async def check_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user joined force channel, if not ask to join"""
    if not config.FORCE_CHANNEL:
        return True
    
    user_id = update.effective_user.id
    if config.is_admin(user_id):
        return True  # Admin bypass

    try:
        # Try to check membership
        channel_id = config.FORCE_CHANNEL
        # Convert username to id if needed? We have ID -1004393596502
        try:
            member = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                return True
        except BadRequest as e:
            # If bot not admin in channel, skip check
            logger.warning(f"Force join check failed (bot not admin in channel?): {e}")
            return True
        except Exception as e:
            logger.warning(f"Force join error: {e}")
            return True

        # Not joined - ask to join
        kb = [
            [InlineKeyboardButton("📢 Join Channel", url=config.FORCE_CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Joined - Check Again", callback_data="check_joined")]
        ]
        await update.message.reply_text(
            f"⚠️ <b>Access Denied!</b>\n\n"
            f"Bot use karne ke liye aapko hamara channel join karna hoga.\n\n"
            f"📢 Channel: {config.FORCE_CHANNEL_LINK}\n\n"
            f"Join karke 'Joined - Check Again' pe click karo.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return False
    except Exception as e:
        logger.warning(f"Force join check exception: {e}")
        return True

async def check_joined_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=config.FORCE_CHANNEL, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            await query.edit_message_text(
                "✅ <b>Verified! Ab aap bot use kar sakte ho.</b>\n\n/start pe click karo.",
                parse_mode=ParseMode.HTML
            )
        else:
            await query.answer("❌ Abhi bhi join nahi kiya! Pehle channel join karo.", show_alert=True)
    except Exception as e:
        await query.edit_message_text(f"✅ Check done! /start se shuru karo.\n\nNote: {str(e)[:100]}", parse_mode=ParseMode.HTML)

# ========== START & HELP ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Force join check
        if not await check_force_join(update, context):
            return

        user = update.effective_user
        
        # Try to get grid keyboard, fallback to None if fails
        try:
            reply_kb = kb_for(user.id)
        except Exception as e:
            print(f"kb_for failed: {e}")
            reply_kb = None
        
        txt = f"""
╔══════════════════════════════════════╗
║  🚀 <b>OSINT Hunter Hub</b> - Advanced  ║
║  @osint_hunter_hub_bot               ║
╚══════════════════════════════════════╝

👋 <b>Hello {user.first_name}!</b>

🔥 <b>11 Advanced Tools - Grid Menu Me!</b>
Neeche 👇 grid button pe click karo (4 dots wala icon) — saare tools grid me khulenge!

Ye bot aisa hai jaisa kisi ke paas nahi — har tool me max data + beautiful design

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📱 Grid Tools (2 columns):</b>

📡 TELEGRAM SCRAPER  |  📸 INSTAGRAM OSINT
📧 EMAIL OSINT       |  🌐 IP/DOMAIN RECON
🖼️ EXIF FORENSICS    |  🔒 SECURITY CHECK
📱 NUMBER INFO       |  🆔 TG NUMBER TOOLS
📝 OCR EXTRACTOR     |  🌐 WEBSITE EXTRACTOR
📊 FILE CONVERTER    |  📜 ALL COMMANDS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📌 Quick Examples:</b>
<code>/numinfo 9204507743</code>
<code>/scrape @durov 50</code>
<code>/insta @instagram</code>
<code>/ip 1.1.1.1</code>
<code>/domain github.com</code>

<b>👑 Owner:</b> @Supermannn_x
<b>📢 Channel:</b> @osint_xpert

⚠️ <i>Sirf public data, educational OSINT ke liye.</i>

🔥 <b>Powered by @Supermannn_x</b>

👇 <b>Neeche grid se tool select karo!</b>
"""

        # First send with reply keyboard (grid) - with fallback
        try:
            if reply_kb:
                await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=reply_kb)
            else:
                await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"First reply failed: {e}, trying without markup")
            await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
        
        # Then send inline keyboard for extra options
        try:
            kb = [
                [InlineKeyboardButton("📢 Join Channel", url=config.FORCE_CHANNEL_LINK), InlineKeyboardButton("💬 Support", url="https://t.me/Supermannn_x")],
                [InlineKeyboardButton("📜 All Commands", callback_data="help_all"), InlineKeyboardButton("🔧 Tools Grid", callback_data="tools")],
                [InlineKeyboardButton("👑 Owner", url="https://t.me/Supermannn_x")]
            ]
            await update.message.reply_text(
                "👆 <b>Grid Menu Active!</b> Neeche 4-dots wale icon pe click karke saare tools dekho.\n\nYa upar ke buttons se direct use karo.",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(kb)
            )
        except Exception as e:
            print(f"Second reply failed: {e}")
            # Even if inline fails, first message already sent, so ok
    
    except Exception as e:
        print(f"START CRASHED: {e}")
        traceback.print_exc()
        try:
            await update.message.reply_text(
                f"🚀 <b>OSINT Hunter Hub LIVE!</b>\n\n"
                f"👋 Hello {update.effective_user.first_name}!\n\n"
                f"11 Tools Ready:\n"
                f"/numinfo 9876543210\n"
                f"/scrape @channel 50\n"
                f"/insta @username\n"
                f"/ip 8.8.8.8\n"
                f"/domain google.com\n\n"
                f"Grid menu loading... /help for all commands\n\n"
                f"👑 @Supermannn_x | 📢 @osint_xpert",
                parse_mode=ParseMode.HTML
            )
        except Exception as e2:
            print(f"Fallback also failed: {e2}")

async def handle_grid_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle grid button presses like utility-duniya-bot"""
    try:
        if not await check_force_join(update, context):
            return
        
        text = update.message.text.strip()
        # Clean emoji and get mode
        clean_text = text
        # Remove emoji prefix
        for emoji in ["📡 ", "📸 ", "📧 ", "🌐 ", "🖼️ ", "🔒 ", "📱 ", "🆔 ", "📝 ", "📊 ", "📜 ", "👑 ", "📢 "]:
            if clean_text.startswith(emoji):
                clean_text = clean_text[len(emoji):].strip()
                break
        
        mode = BTN_MODE_MAP.get(clean_text.upper())
        if not mode:
            # Try without cleaning
            mode = BTN_MODE_MAP.get(text.upper())
        
        if not mode:
            return  # Not a grid button
        
        # Handle each mode
        if mode == "help":
            await help_cmd(update, context)
            return
        
        if mode == "owner":
            await update.message.reply_text(
                "👑 <b>Owner:</b> @Supermannn_x\n📢 <b>Channel:</b> @osint_xpert\n🤖 <b>Bot:</b> @osint_hunter_hub_bot",
                parse_mode=ParseMode.HTML
            )
            return
        
        if mode == "channel":
            kb = [[InlineKeyboardButton("📢 Join Channel", url=config.FORCE_CHANNEL_LINK)]]
            await update.message.reply_text(
                f"📢 <b>Channel:</b> {config.FORCE_CHANNEL_LINK}\n\nJoin karke bot use karo!",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(kb)
            )
            return
        
        # For tool modes, show prompt card
        prompt = GRID_PROMPTS.get(mode)
        if not prompt:
            return
        
        pc_mid = "━━━━━━━━━━━━━━━━━━━━━━"
        txt = f"""
╔══════════════════════════════════════╗
║  {prompt['head']}  ║
╚══════════════════════════════════════╝

{prompt['ask']}

📌 <b>Example:</b>
<code>{prompt['ex']}</code>

💡 <b>Tip:</b> {prompt['tip']}

{pc_mid}

<b>📜 Commands:</b>
{prompt['cmds']}

{pc_mid}

🔥 <b>Powered by @Supermannn_x</b>
"""
        await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"Grid handler error: {e}")
        traceback.print_exc()

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return

    txt = """
╔══════════════════════════════════════╗
║  📖 <b>OSINT Hunter Hub - Full Guide</b>  ║
╚══════════════════════════════════════╝

<b>━━━━━━━━ Tool 7: Number Info ━━━━━━━━</b>
/numinfo 9876543210
/number 9876543210
/num 9876543210
→ Name, Father, Address, Circle, Aadhaar masked, Alt phone, Response ms
→ No data pe: ❌ No records found...

<b>━━━━━━━━ Tool 8: TG Tools ━━━━━━━━</b>
/tginfo @username
/tgnum @username
/telegram @username
→ Telegram username se info

/paknum 03001234567
/pak 0300...
→ Pak number / CNIC info

<b>━━━━━━━━ Tool 1: Telegram Scraper ━━━━━━━━</b>
/channel_info @username → Full channel info
/scrape @channel [limit] → Last N messages (max 10000)
/scrape_search @channel keyword [limit] → Search inside
/scrape_media @channel [limit] → Only media
/stats @channel → Stats + Top 10
/batch @ch1 @ch2 [limit] → Multiple

<b>━━━━━━━━ Tool 2: Instagram ━━━━━━━━</b>
/insta @username → Public profile

<b>━━━━━━━━ Tool 6: Security Checker ━━━━━━━━</b>
/igsecure @username
/security @username
/sec @username
→ Security Score 0-100 + Email/Phone leak + Recommendations

<b>━━━━━━━━ Tool 3: Email ━━━━━━━━</b>
/email test@gmail.com → Validation + Breach + Gravatar + MX

<b>━━━━━━━━ Tool 4: IP/Domain ━━━━━━━━</b>
/ip 8.8.8.8 → IP + VPN detection + Maps
/domain google.com → Full recon
/dns google.com → DNS records
/whois google.com → WHOIS
/ssl google.com → SSL cert

<b>━━━━━━━━ Tool 5: EXIF ━━━━━━━━</b>
Photo ko File/Document ke roop me bhejo → EXIF + GPS
/exif (reply to photo)

<b>━━━━━━━━ Tool 9: OCR ━━━━━━━━</b>
Photo bhejo + caption 'ocr' → Text extraction (Hindi+English)
/ocr (reply to photo with ocr)

<b>━━━━━━━━ Tool 10: Website Extractor ━━━━━━━━</b>
/wextract https://site.com → Emails + Phones + Links + Meta

<b>━━━━━━━━ Tool 11: File Converter ━━━━━━━━</b>
Excel/CSV/Image/PDF ko Document ke roop me bhejo:
- Caption 'excel2pdf' → Excel to PDF
- 'csv2excel' → CSV to Excel
- 'excel2csv' → Excel to CSV
- 'img2pdf' → Image to PDF
- 'pdf2text' → PDF to Text

<b>🛡️ Safety:</b>
• FloodWait auto handle
• Force join: @osint_xpert
• Owner: @Supermannn_x

/start se wapas jao
"""

    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

# ========== NUMBER INFO ==========
async def number_info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text(
            "❌ <b>Use:</b> <code>/numinfo 9876543210</code>\n\n"
            "📌 Example:\n"
            "<code>/numinfo 9204507743</code>\n"
            "<code>/number 9876543210</code>",
            parse_mode=ParseMode.HTML
        )
        return

    number = context.args[0]
    status = await update.message.reply_text(
        f"🔍 <b>Number Info Searching...</b>\n\n"
        f"📱 Number: <code>{number}</code>\n"
        f"⏳ Please wait 5-15 seconds...",
        parse_mode=ParseMode.HTML
    )

    try:
        result = lookup_number(number)
        
        # Advanced formatting with spaces and emojis
        if not result.get("ok"):
            # No records case - only short message as per user request
            await status.edit_text(
                f"❌ No records found for this number in any database.",
                parse_mode=ParseMode.HTML
            )
            return

        owner = result.get("owner", {})
        num = result.get("number")
        circle = result.get("circle") or owner.get("circle","")
        ms = result.get("ms",0)
        rec = result.get("records",1)

        txt = f"""
╔══════════════════════════════════════╗
║  📱 <b>NUMBER INFO - OSINT</b>           ║
╚══════════════════════════════════════╝

📞 <b>Phone:</b> <code>{num}</code>

"""

        if circle:
            txt += f"🌐 <b>Circle:</b> {circle}\n\n"

        if owner.get("name"):
            txt += f"👤 <b>Name:</b> {owner.get('name')}\n\n"

        if owner.get("father"):
            txt += f"👨‍👦 <b>Father Name:</b> {owner.get('father')}\n\n"

        if owner.get("phone"):
            txt += f"📱 <b>Mobile:</b> <code>{owner.get('phone')}</code>\n\n"

        if owner.get("alt_phone"):
            txt += f"📱 <b>Alt Mobile:</b> <code>{owner.get('alt_phone')}</code>\n\n"

        if owner.get("address"):
            txt += f"🏠 <b>Address:</b>\n{owner.get('address')[:300]}\n\n"

        if owner.get("aadhaar"):
            txt += f"🆔 <b>Aadhaar:</b> <code>{owner.get('aadhaar')}</code> (masked)\n\n"

        txt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📡 <b>Source:</b> utility-api-vu83

⚡ <b>Response:</b> {ms}ms
"""

        if rec > 1:
            txt += f"📑 <b>Records:</b> {rec} records found\n"

        txt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 <b>Powered by @Supermannn_x</b>
📢 <b>Channel:</b> @osint_xpert
"""

        await status.edit_text(txt, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ Error: {str(e)[:200]}", parse_mode=ParseMode.HTML)

# ========== TG TOOLS ==========
async def tg_number_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text(
            "❌ <b>Use:</b> <code>/tginfo @username</code>\n\n"
            "📌 Example:\n"
            "<code>/tginfo @durov</code>\n"
            "<code>/tgnum @username</code>",
            parse_mode=ParseMode.HTML
        )
        return

    username = context.args[0]
    status = await update.message.reply_text(
        f"🔍 <b>Telegram OSINT Searching...</b>\n\n"
        f"👤 Username: <code>{username}</code>\n"
        f"⏳ Please wait...",
        parse_mode=ParseMode.HTML
    )

    try:
        result = lookup_tg(username)
        
        if not result.get("ok"):
            await status.edit_text(f"❌ No records found for this username in any database.", parse_mode=ParseMode.HTML)
            return

        data = result.get("data", {})
        ms = result.get("ms",0)

        txt = f"""
╔══════════════════════════════════════╗
║  🆔 <b>TELEGRAM OSINT</b>                ║
╚══════════════════════════════════════╝

👤 <b>Username:</b> <code>{result.get('term')}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        if isinstance(data, dict):
            for k,v in list(data.items())[:15]:
                if v and str(v).lower() not in ("na","none","null",""):
                    txt += f"🔹 <b>{k}:</b> {str(v)[:200]}\n\n"
        else:
            txt += f"{str(data)[:1000]}\n\n"

        txt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ <b>Response:</b> {ms}ms

🔥 <b>Powered by @Supermannn_x</b>
"""

        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)[:200]}", parse_mode=ParseMode.HTML)

async def pak_number_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/paknum 03001234567</code>", parse_mode=ParseMode.HTML)
        return

    num = context.args[0]
    status = await update.message.reply_text(f"🔍 Pak lookup for {num}...", parse_mode=ParseMode.HTML)

    try:
        result = lookup_pak(num)
        if not result.get("ok"):
            await status.edit_text(f"❌ No records found for this number in any database.", parse_mode=ParseMode.HTML)
            return

        data = result.get("data", {})
        ms = result.get("ms",0)

        txt = f"""
╔══════════════════════════════════════╗
║  🇵🇰 <b>PAK NUMBER INFO</b>               ║
╚══════════════════════════════════════╝

📱 <b>Number:</b> <code>{num}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        if isinstance(data, dict):
            for k,v in list(data.items())[:15]:
                if v and str(v).lower() not in ("na","none","null",""):
                    txt += f"🔹 <b>{k}:</b> {str(v)[:200]}\n\n"

        txt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ <b>Response:</b> {ms}ms
🔥 <b>Powered by @Supermannn_x</b>
"""

        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)[:200]}", parse_mode=ParseMode.HTML)

# ========== TELEGRAM SCRAPER ==========
async def channel_info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/channel_info @channelusername</code>", parse_mode=ParseMode.HTML)
        return

    channel = context.args[0]
    status = await update.message.reply_text(
        f"🔍 <b>Fetching Channel Info...</b>\n\n"
        f"📢 Channel: <code>{channel}</code>\n"
        f"⏳ Please wait...",
        parse_mode=ParseMode.HTML
    )

    try:
        scr = get_scraper()
        info = await scr.get_channel_info(channel)
        if not info.get("ok"):
            await status.edit_text(f"❌ Error: {info.get('error')}", parse_mode=ParseMode.HTML)
            return

        txt = f"""
╔══════════════════════════════════════╗
║  📊 <b>CHANNEL INFO</b>                  ║
╚══════════════════════════════════════╝

📛 <b>Title:</b> {info.get('title')}

🆔 <b>ID:</b> <code>{info.get('id')}</code>

👤 <b>Username:</b> @{info.get('username') or 'None (Private)'}

🔰 <b>Type:</b> {info.get('type')}

📡 <b>Broadcast:</b> {info.get('is_broadcast')} | <b>Megagroup:</b> {info.get('is_megagroup')}

👥 <b>Members:</b> {info.get('participants_count') or 'N/A'}

🟢 <b>Online:</b> {info.get('online_count') or 'N/A'}

✅ <b>Verified:</b> {info.get('is_verified')} | <b>Scam:</b> {info.get('is_scam')} | <b>Fake:</b> {info.get('is_fake')}

📅 <b>Created:</b> {info.get('creation_date') or 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 <b>Description:</b>

{info.get('description')[:800] or 'No description'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 <b>Link:</b> https://t.me/{info.get('username') or ''}

🔥 <b>Powered by @Supermannn_x</b>
"""

        await status.edit_text(txt, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ Error: {str(e)[:200]}", parse_mode=ParseMode.HTML)

async def scrape_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/scrape @channel [limit]</code>", parse_mode=ParseMode.HTML)
        return

    channel = context.args[0]
    limit = 50
    if len(context.args) > 1:
        try:
            limit = int(context.args[1])
        except:
            pass
    limit = max(1, min(limit, 10000))

    status = await update.message.reply_text(
        f"⏳ <b>Scraping Channel...</b>\n\n"
        f"📢 Channel: <code>{channel}</code>\n"
        f"📊 Limit: {limit} messages\n"
        f"⏳ This may take 10-60 seconds...",
        parse_mode=ParseMode.HTML
    )

    try:
        scr = get_scraper()
        result = await scr.scrape_messages(channel, limit=limit)

        if not result.get("ok"):
            await status.edit_text(f"❌ Error: {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        messages = result.get("messages", [])
        stats = result.get("stats", {})

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, f"{channel.strip('@')}_{limit}.json")
            csv_path = os.path.join(tmpdir, f"{channel.strip('@')}_{limit}.csv")
            scr.export_json(result, json_path)
            scr.export_csv(messages, csv_path)

            summary = f"""
╔══════════════════════════════════════╗
║  ✅ <b>SCRAPED {len(messages)} MESSAGES</b>  ║
╚══════════════════════════════════════╝

📢 <b>Channel:</b> {channel}

📊 <b>Stats:</b>

• 📝 Total: {stats.get('total')}

• 👀 Total Views: {stats.get('total_views')}

• 📈 Avg Views: {stats.get('avg_views')}

• 🔁 Total Forwards: {stats.get('total_forwards')}

• 🎬 Media Count: {stats.get('media_count')} ({stats.get('media_ratio')}%)

• 🔗 Links: {stats.get('link_count')}

• #️⃣ Hashtags: {stats.get('hashtag_count')}

• @️⃣ Mentions: {stats.get('mention_count')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔝 <b>Top 3 Most Viewed:</b>

"""

            for i, tp in enumerate(stats.get('top_posts', [])[:3], 1):
                summary += f"{i}. 👀 {tp.get('views')} views\n   🔗 {tp.get('link')}\n   📝 {tp.get('text','')[:60]}...\n\n"

            summary += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 <b>Files:</b> JSON (full) + CSV (Excel)

🔥 <b>Powered by @Supermannn_x</b>
"""

            await status.edit_text(summary, parse_mode=ParseMode.HTML)
            await update.message.reply_document(document=open(json_path, 'rb'), filename=os.path.basename(json_path), caption="📄 Full JSON data - Max info")
            await update.message.reply_document(document=open(csv_path, 'rb'), filename=os.path.basename(csv_path), caption="📊 CSV for Excel")

    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ Error: {str(e)[:200]}", parse_mode=ParseMode.HTML)

async def scrape_search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if len(context.args) < 2:
        await update.message.reply_text("❌ Use: <code>/scrape_search @channel keyword [limit]</code>", parse_mode=ParseMode.HTML)
        return

    channel = context.args[0]
    keyword = context.args[1]
    limit = 50
    if len(context.args) > 2:
        try:
            limit = int(context.args[2])
        except:
            pass

    status = await update.message.reply_text(f"🔍 Searching '{keyword}' in {channel} - {limit} results...", parse_mode=ParseMode.HTML)

    try:
        scr = get_scraper()
        result = await scr.scrape_messages(channel, limit=limit, search_query=keyword)
        if not result.get("ok"):
            await status.edit_text(f"❌ Error: {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        messages = result.get("messages", [])
        if not messages:
            await status.edit_text(f"❌ No results for '{keyword}' in {channel}", parse_mode=ParseMode.HTML)
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, f"{channel.strip('@')}_search_{keyword}_{limit}.json")
            scr.export_json(result, json_path)

            summary = f"✅ Found {len(messages)} messages for '{keyword}' in {channel}\n\n"
            for m in messages[:5]:
                summary += f"• ID {m['id']} | {m['views']} views | {m['date'][:10]}\n{m['text'][:100]}...\nLink: {m['link']}\n\n"

            await status.edit_text(summary[:4000], parse_mode=ParseMode.HTML)
            await update.message.reply_document(document=open(json_path, 'rb'), filename=os.path.basename(json_path), caption=f"🔍 Search results for {keyword}")

    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def scrape_media_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/scrape_media @channel [limit]</code>", parse_mode=ParseMode.HTML)
        return

    channel = context.args[0]
    limit = 50
    if len(context.args) > 1:
        try:
            limit = int(context.args[1])
        except:
            pass

    status = await update.message.reply_text(f"🎬 Scraping media only from {channel} - {limit}...", parse_mode=ParseMode.HTML)

    try:
        scr = get_scraper()
        result = await scr.scrape_messages(channel, limit=limit, media_only=True)
        if not result.get("ok"):
            await status.edit_text(f"❌ Error: {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        messages = result.get("messages", [])
        summary = f"✅ Found {len(messages)} media messages in {channel}\n\n"
        for m in messages[:10]:
            summary += f"• ID {m['id']} | {m.get('media',{}).get('type')} | {m['views']} views | {m['link']}\n\n"

        await status.edit_text(summary[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/stats @channel</code>", parse_mode=ParseMode.HTML)
        return

    channel = context.args[0]
    status = await update.message.reply_text(f"📊 Calculating stats for {channel} (200 messages sample)...", parse_mode=ParseMode.HTML)

    try:
        scr = get_scraper()
        result = await scr.scrape_messages(channel, limit=200)
        if not result.get("ok"):
            await status.edit_text(f"❌ Error: {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        stats = result.get("stats", {})
        txt = f"""
╔══════════════════════════════════════╗
║  📊 <b>STATS FOR {channel}</b>           ║
╚══════════════════════════════════════╝

📝 <b>Total Sampled:</b> {stats.get('total')}

👀 <b>Total Views:</b> {stats.get('total_views')}

📈 <b>Avg Views:</b> {stats.get('avg_views')}

🔁 <b>Total Forwards:</b> {stats.get('total_forwards')}

🎬 <b>Media:</b> {stats.get('media_count')} ({stats.get('media_ratio')}%)

🔗 <b>Links:</b> {stats.get('link_count')}

#️⃣ <b>Hashtags:</b> {stats.get('hashtag_count')}

@️⃣ <b>Mentions:</b> {stats.get('mention_count')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔝 <b>Top 10 Most Viewed Posts:</b>

"""

        for i, tp in enumerate(stats.get('top_posts', [])[:10], 1):
            txt += f"{i}. 👀 {tp.get('views')} views\n   🆔 ID {tp.get('id')}\n   🔗 {tp.get('link')}\n   📝 {tp.get('text','')[:60]}...\n\n"

        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def batch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if len(context.args) < 2:
        await update.message.reply_text("❌ Use: <code>/batch @ch1 @ch2 @ch3 [limit]</code>", parse_mode=ParseMode.HTML)
        return

    channels = []
    limit = 30
    for arg in context.args:
        if arg.startswith('@') or 't.me' in arg:
            channels.append(arg)
        else:
            try:
                limit = int(arg)
            except:
                pass

    channels = channels[:5]
    status = await update.message.reply_text(f"⏳ Batch scraping {len(channels)} channels - {limit} each...\n{', '.join(channels)}", parse_mode=ParseMode.HTML)

    try:
        scr = get_scraper()
        results = await scr.batch_scrape(channels, limit_per_channel=limit)

        txt = f"✅ Batch done - {len(channels)} channels:\n\n"
        for ch, res in results.items():
            if res.get("ok"):
                txt += f"• {ch}: {res.get('scraped')} msgs, {res.get('stats',{}).get('total_views',0)} views\n\n"
            else:
                txt += f"• {ch}: ❌ {res.get('error')}\n\n"

        await status.edit_text(txt, parse_mode=ParseMode.HTML)

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

# ========== INSTAGRAM ==========
async def insta_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/insta @username</code>", parse_mode=ParseMode.HTML)
        return

    username = context.args[0]
    status = await update.message.reply_text(f"🔍 Instagram OSINT for {username}...", parse_mode=ParseMode.HTML)

    try:
        result = instagram_osint(username)
        if not result.get("ok"):
            await status.edit_text(f"❌ {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        txt = f"""
╔══════════════════════════════════════╗
║  📸 <b>INSTAGRAM OSINT</b>               ║
╚══════════════════════════════════════╝

👤 <b>Username:</b> @{result.get('username')}

📛 <b>Full Name:</b> {result.get('full_name') or 'N/A'}

📝 <b>Bio:</b>

{result.get('bio')[:500] or 'N/A'}

👥 <b>Followers:</b> {result.get('followers') or 'N/A'}

👤 <b>Following:</b> {result.get('following') or 'N/A'}

📸 <b>Posts:</b> {result.get('posts') or 'N/A'}

🔗 <b>Profile URL:</b> {result.get('profile_url')}

🖼️ <b>Profile Pic:</b> {result.get('profile_pic') or 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Note: Instagram blocks heavily, data limited to public OG tags

🔥 Powered by @Supermannn_x
"""

        await status.edit_text(txt, parse_mode=ParseMode.HTML)

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

# ========== EMAIL ==========
async def email_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/email test@gmail.com</code>", parse_mode=ParseMode.HTML)
        return

    email = context.args[0]
    status = await update.message.reply_text(f"📧 Email OSINT for {email}...", parse_mode=ParseMode.HTML)

    try:
        result = email_osint(email)
        if not result.get("ok"):
            await status.edit_text(f"❌ {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        v = result.get("validation", {})
        g = result.get("gravatar", {})
        b = result.get("breach", {})

        txt = f"""
╔══════════════════════════════════════╗
║  📧 <b>EMAIL OSINT</b>                   ║
╚══════════════════════════════════════╝

📧 <b>Email:</b> <code>{email}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ <b>Validation:</b>

• Valid Format: {v.get('is_valid_format')}

• Domain: {v.get('domain')}

• Disposable: {v.get('is_disposable')}

• Free Provider: {v.get('is_free_provider')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖼️ <b>Gravatar:</b>

• Has Gravatar: {g.get('has_gravatar')}

• Hash: <code>{g.get('hash')}</code>

• URL: {g.get('gravatar_url') or 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔓 <b>Breach Check (xposedornot):</b>

• Breached: {b.get('breached')}

• Count: {b.get('breach_count')}

• Breaches: {', '.join(b.get('breaches', [])[:5]) or 'None'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📡 <b>MX Records:</b> {', '.join(result.get('mx_records', [])[:3]) or 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 <b>Notes:</b>

{chr(10).join(result.get('suggestions', [])) or 'No issues'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 Powered by @Supermannn_x
"""

        await status.edit_text(txt, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

# ========== IP & DOMAIN ==========
async def ip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/ip 8.8.8.8</code> or <code>/ip google.com</code>", parse_mode=ParseMode.HTML)
        return

    target = context.args[0]
    status = await update.message.reply_text(f"🌐 IP lookup for {target}...", parse_mode=ParseMode.HTML)

    try:
        result = ip_lookup(target)
        if not result.get("ok"):
            await status.edit_text(f"❌ {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        txt = f"""
╔══════════════════════════════════════╗
║  🌐 <b>IP RECON</b>                      ║
╚══════════════════════════════════════╝

🌐 <b>IP:</b> <code>{result.get('ip')}</code>

📍 <b>Location:</b>

• City: {result.get('city')}

• Region: {result.get('region')}

• Country: {result.get('country')} ({result.get('continent')})

• Zip: {result.get('zip')}

• Timezone: {result.get('timezone')}

🗺️ <b>Coords:</b> {result.get('lat')}, {result.get('lon')}

🔗 <b>Google Maps:</b> {result.get('google_maps')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏢 <b>ISP:</b> {result.get('isp')}

🏛️ <b>Org:</b> {result.get('org')}

🔢 <b>AS:</b> {result.get('as')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛡️ <b>Security:</b>

• Is Proxy: {result.get('is_proxy')}

• Is Hosting: {result.get('is_hosting')}

• VPN/Proxy Detected: {result.get('is_vpn_proxy')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔁 <b>Reverse DNS:</b> {result.get('reverse_dns') or 'N/A'}

🔥 Powered by @Supermannn_x
"""

        await status.edit_text(txt, parse_mode=ParseMode.HTML)

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def domain_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/domain google.com</code>", parse_mode=ParseMode.HTML)
        return

    target = context.args[0]
    status = await update.message.reply_text(f"🌐 Full recon for {target}...", parse_mode=ParseMode.HTML)

    try:
        result = full_recon(target)
        if result.get("type") == "ip":
            ip_info = result.get("ip_info", {})
            await status.edit_text(f"IP detected, use /ip command. Info: {ip_info}", parse_mode=ParseMode.HTML)
            return

        dns_info = result.get("dns", {})
        whois_info = result.get("whois", {})
        ssl_info = result.get("ssl", {})
        ip_info = result.get("ip_info", {})

        txt = f"""
╔══════════════════════════════════════╗
║  🌐 <b>DOMAIN RECON</b>                  ║
╚══════════════════════════════════════╝

🌐 <b>Domain:</b> {result.get('target')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>--- DNS ---</b>

• A: {', '.join(dns_info.get('records',{}).get('A',[])[:2]) if isinstance(dns_info.get('records',{}).get('A'), list) else dns_info.get('records',{}).get('A')}

• MX: {', '.join(dns_info.get('records',{}).get('MX',[])[:2]) if isinstance(dns_info.get('records',{}).get('MX'), list) else 'N/A'}

• NS: {', '.join(dns_info.get('records',{}).get('NS',[])[:2]) if isinstance(dns_info.get('records',{}).get('NS'), list) else 'N/A'}

• IP: {dns_info.get('ip') or 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>--- WHOIS ---</b>

• Registrar: {whois_info.get('registrar') or 'N/A'}

• Created: {whois_info.get('creation_date') or 'N/A'}

• Expires: {whois_info.get('expiration_date') or 'N/A'}

• NS: {', '.join(whois_info.get('name_servers',[])[:2]) if whois_info.get('name_servers') else 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>--- SSL ---</b>

• Issuer: {ssl_info.get('issuer') or 'N/A'}

• Subject: {ssl_info.get('subject') or 'N/A'}

• From: {ssl_info.get('not_before') or 'N/A'}

• To: {ssl_info.get('not_after') or 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>--- IP Info ---</b>

• IP: {ip_info.get('ip') if ip_info and ip_info.get('ok') else 'N/A'}

• Location: {ip_info.get('city') if ip_info and ip_info.get('ok') else 'N/A'}, {ip_info.get('country') if ip_info and ip_info.get('ok') else ''}

• ISP: {ip_info.get('isp') if ip_info and ip_info.get('ok') else 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 Powered by @Supermannn_x
"""

        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def dns_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/dns google.com</code>", parse_mode=ParseMode.HTML)
        return

    target = context.args[0]
    status = await update.message.reply_text(f"🔍 DNS lookup for {target}...", parse_mode=ParseMode.HTML)

    try:
        result = dns_lookup(target)
        txt = f"🌐 <b>DNS for {result.get('domain')}</b>\n\n"
        for k, v in result.get("records", {}).items():
            txt += f"<b>{k}:</b> {', '.join(v) if isinstance(v, list) else v}\n\n"
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def whois_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/whois google.com</code>", parse_mode=ParseMode.HTML)
        return

    target = context.args[0]
    status = await update.message.reply_text(f"🔍 WHOIS for {target}...", parse_mode=ParseMode.HTML)

    try:
        result = whois_lookup(target)
        if not result.get("ok"):
            await status.edit_text(f"❌ {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        if result.get("raw_whois"):
            txt = f"📜 <b>WHOIS {target}</b>\n\n<pre>{result.get('raw_whois')[:3000]}</pre>"
        else:
            txt = f"""
📜 <b>WHOIS {target}</b>

• Registrar: {result.get('registrar')}

• Created: {result.get('creation_date')}

• Expires: {result.get('expiration_date')}

• Updated: {result.get('updated_date')}

• NS: {result.get('name_servers')}

• Status: {result.get('status')}

• Org: {result.get('org')}

• Country: {result.get('country')}
"""

        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def ssl_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/ssl google.com</code>", parse_mode=ParseMode.HTML)
        return

    target = context.args[0]
    status = await update.message.reply_text(f"🔒 SSL check for {target}...", parse_mode=ParseMode.HTML)

    try:
        result = ssl_check(target)
        if not result.get("ok"):
            await status.edit_text(f"❌ {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        txt = f"""
🔒 <b>SSL for {target}</b>

• Issuer: {result.get('issuer')}

• Subject: {result.get('subject')}

• From: {result.get('not_before')}

• To: {result.get('not_after')}

• Serial: {result.get('serial_number')}

• SAN: {', '.join(result.get('san',[])[:5])}
"""

        await status.edit_text(txt, parse_mode=ParseMode.HTML)

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

# ========== EXIF ==========
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return

    file = None
    if update.message.document:
        if not update.message.document.mime_type or not update.message.document.mime_type.startswith('image/'):
            return
        # Only handle if caption has exif or no caption (default EXIF)
        caption = (update.message.caption or "").lower()
        if "ocr" in caption or "excel" in caption or "pdf" in caption:
            return
        file = await update.message.document.get_file()
        file_name = update.message.document.file_name
    elif update.message.photo:
        caption = (update.message.caption or "").lower()
        if "ocr" in caption:
            return
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_name = f"{photo.file_id}.jpg"
    else:
        return

    status = await update.message.reply_text("📸 EXIF analyzing... (photo download ho raha hai)", parse_mode=ParseMode.HTML)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, file_name)
            await file.download_to_drive(file_path)

            analysis = analyze_exif(file_path)
            txt = exif_to_text(analysis)

            await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

            if analysis.get("has_gps"):
                json_path = os.path.join(tmpdir, f"{file_name}_exif.json")
                with open(json_path, 'w') as f:
                    json.dump(analysis, f, indent=2, default=str)
                await update.message.reply_document(document=open(json_path, 'rb'), filename=os.path.basename(json_path), caption="📍 Full EXIF JSON with GPS")

    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ EXIF Error: {str(e)}", parse_mode=ParseMode.HTML)

async def exif_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return

    if update.message.reply_to_message and (update.message.reply_to_message.photo or update.message.reply_to_message.document):
        orig = update.message.reply_to_message
        file = None
        if orig.document:
            file = await orig.document.get_file()
            file_name = orig.document.file_name
        elif orig.photo:
            photo = orig.photo[-1]
            file = await photo.get_file()
            file_name = f"{photo.file_id}.jpg"

        status = await update.message.reply_text("📸 EXIF analyzing replied photo...", parse_mode=ParseMode.HTML)

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                file_path = os.path.join(tmpdir, file_name)
                await file.download_to_drive(file_path)
                analysis = analyze_exif(file_path)
                txt = exif_to_text(analysis)
                await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

        except Exception as e:
            await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

    else:
        await update.message.reply_text(
            "❌ Photo bhejo as <b>File/Document</b> (compressed nahi), ya kisi photo pe reply karke /exif likho.\n\n"
            "Tip: Telegram photo ko compress karta hai aur EXIF hata deta hai, isliye hamesha <b>File ke roop me bhejo</b> (📎 → File → Gallery se select).",
            parse_mode=ParseMode.HTML
        )

# ========== OCR ==========
async def ocr_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    await update.message.reply_text(
        "📸 <b>OCR - Image to Text</b>\n\n"
        "Photo ko <b>File/Document</b> ke roop me bhejo + caption me 'ocr' likho\n\n"
        "Bot us image se Hindi+English text nikal dega\n\n"
        "Example: Photo bhejo with caption <code>ocr</code> ya photo pe reply karke <code>/ocr</code>",
        parse_mode=ParseMode.HTML
    )

async def handle_ocr_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return

    file = None
    if update.message.document:
        if not update.message.document.mime_type or not update.message.document.mime_type.startswith('image/'):
            return
        caption = (update.message.caption or "").lower()
        if "ocr" not in caption:
            return
        file = await update.message.document.get_file()
        file_name = update.message.document.file_name
    elif update.message.photo:
        caption = (update.message.caption or "").lower()
        if "ocr" not in caption:
            # Also check if reply has /ocr command? Handled elsewhere
            return
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_name = f"{photo.file_id}.jpg"
    else:
        return

    status = await update.message.reply_text("🔍 OCR - Image se text nikal raha hu...", parse_mode=ParseMode.HTML)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, file_name)
            await file.download_to_drive(file_path)
            result = ocr_image(file_path, lang="hi")
            if not result.get("ok"):
                await status.edit_text(f"❌ {result.get('error')}", parse_mode=ParseMode.HTML)
                return

            text = result.get("text","").strip()
            if not text:
                await status.edit_text("❌ Koi text nahi mila image me. Clear image bhejo.", parse_mode=ParseMode.HTML)
                return

            if len(text) > 4000:
                txt_path = os.path.join(tmpdir, f"{file_name}_ocr.txt")
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                await status.edit_text(f"✅ OCR Done - {result.get('chars')} chars, method: {result.get('method')}\n\n{text[:1000]}...\n\nFull text file me hai:", parse_mode=ParseMode.HTML)
                await update.message.reply_document(document=open(txt_path,'rb'), filename=os.path.basename(txt_path), caption="📝 OCR Text")
            else:
                await status.edit_text(f"✅ OCR Done ({result.get('method')}) - {result.get('chars')} chars:\n\n<pre>{text[:3500]}</pre>", parse_mode=ParseMode.HTML)

    except Exception as e:
        await status.edit_text(f"❌ OCR Error: {str(e)}", parse_mode=ParseMode.HTML)

# ========== WEBSITE EXTRACTOR ==========
async def website_extract_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/wextract https://example.com</code>", parse_mode=ParseMode.HTML)
        return

    url = context.args[0]
    status = await update.message.reply_text(f"🔍 Extracting from {url}...", parse_mode=ParseMode.HTML)

    try:
        result = website_extractor(url)
        if not result.get("ok"):
            await status.edit_text(f"❌ {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        meta = result.get("meta",{})
        links = result.get("links",{})

        txt = f"""
╔══════════════════════════════════════╗
║  🌐 <b>WEBSITE EXTRACTOR</b>             ║
╚══════════════════════════════════════╝

🌐 <b>URL:</b> {result.get('url')}

📄 <b>Title:</b> {meta.get('title') or 'N/A'}

📝 <b>Description:</b>

{meta.get('description')[:300] or 'N/A'}

🔑 <b>Keywords:</b> {meta.get('keywords')[:200] or 'N/A'}

🖼️ <b>OG Image:</b> {meta.get('og_image') or 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 <b>Emails Found ({len(result.get('emails',[]))}):</b>

{', '.join(result.get('emails',[])[:10]) or 'None'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 <b>Phones Found ({len(result.get('phones',[]))}):</b>

{', '.join(result.get('phones',[])[:10]) or 'None'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 <b>Links:</b>

• Total: {links.get('total')}

• Internal: {len(links.get('internal',[]))}

• External: {len(links.get('external',[]))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Size:</b> HTML {result.get('html_length')} chars | Text {result.get('text_length')} chars

🔥 Powered by @Supermannn_x
"""

        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

# ========== FILE CONVERTER ==========
async def excel2pdf_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    await update.message.reply_text(
        "📊 <b>Excel to PDF Converter - Advanced</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📤 <b>Excel file (.xlsx, .xls, .csv) ko Document ke roop me bhejo</b>\n"
        "Caption me likho: <code>excel2pdf</code> ya <code>pdf</code>\n\n"
        "Bot usko PDF me convert karke de dega:\n"
        "• Landscape A4\n"
        "• 100 rows, 15 cols per sheet\n"
        "• Blue header + striped rows\n"
        "• Multiple sheets support (5 tak)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📌 <b>Other Conversions:</b>\n"
        "• <code>csv2excel</code> → CSV to Excel\n"
        "• <code>excel2csv</code> → Excel to CSV\n"
        "• <code>img2pdf</code> → Image to PDF\n"
        "• <code>pdf2text</code> → PDF to Text\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔥 Powered by @Supermannn_x",
        parse_mode=ParseMode.HTML
    )

async def handle_file_converter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not update.message.document:
        return

    doc = update.message.document
    file_name = doc.file_name or "file"
    mime = doc.mime_type or ""
    caption = (update.message.caption or "").lower()

    is_excel = file_name.lower().endswith(('.xlsx','.xls')) or 'excel' in mime or 'spreadsheet' in mime
    is_csv = file_name.lower().endswith('.csv')
    is_image = file_name.lower().endswith(('.jpg','.jpeg','.png','.webp')) or mime.startswith('image/')
    is_pdf = file_name.lower().endswith('.pdf')

    convert_type = None
    if 'excel2pdf' in caption or 'xlsx2pdf' in caption or ('pdf' in caption and (is_excel or is_csv)):
        convert_type = 'excel2pdf'
    elif 'csv2excel' in caption:
        convert_type = 'csv2excel'
    elif 'excel2csv' in caption:
        convert_type = 'excel2csv'
    elif 'img2pdf' in caption or 'image2pdf' in caption:
        convert_type = 'img2pdf'
    elif 'pdf2text' in caption:
        convert_type = 'pdf2text'
    elif is_excel or is_csv:
        convert_type = 'excel2pdf'
    elif is_pdf and 'text' in caption:
        convert_type = 'pdf2text'
    else:
        return

    status = await update.message.reply_text(f"⏳ Converting {file_name} → {convert_type}...", parse_mode=ParseMode.HTML)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, file_name)
            file_obj = await doc.get_file()
            await file_obj.download_to_drive(input_path)

            if convert_type == 'excel2pdf':
                output_path = os.path.join(tmpdir, os.path.splitext(file_name)[0] + ".pdf")
                result = excel_to_pdf(input_path, output_path)
                if not result.get("ok"):
                    await status.edit_text(f"❌ {result.get('error')}", parse_mode=ParseMode.HTML)
                    return
                await status.edit_text(
                    f"✅ <b>Excel to PDF Done!</b>\n\n"
                    f"📊 Total Rows: {result.get('total_rows')}\n"
                    f"📑 Sheets: {result.get('sheets')}\n\n"
                    f"🔥 Powered by @Supermannn_x",
                    parse_mode=ParseMode.HTML
                )
                await update.message.reply_document(document=open(output_path,'rb'), filename=os.path.basename(output_path), caption=f"📄 PDF - {result.get('total_rows')} rows")

            elif convert_type == 'csv2excel':
                output_path = os.path.join(tmpdir, os.path.splitext(file_name)[0] + ".xlsx")
                result = csv_to_excel(input_path, output_path)
                if not result.get("ok"):
                    await status.edit_text(f"❌ {result.get('error')}", parse_mode=ParseMode.HTML)
                    return
                await status.edit_text(f"✅ CSV to Excel Done - {result.get('rows')} rows", parse_mode=ParseMode.HTML)
                await update.message.reply_document(document=open(output_path,'rb'), filename=os.path.basename(output_path))

            elif convert_type == 'excel2csv':
                output_path = os.path.join(tmpdir, os.path.splitext(file_name)[0] + ".csv")
                result = excel_to_csv(input_path, output_path)
                if not result.get("ok"):
                    await status.edit_text(f"❌ {result.get('error')}", parse_mode=ParseMode.HTML)
                    return
                await status.edit_text(f"✅ Excel to CSV Done - {result.get('rows')} rows", parse_mode=ParseMode.HTML)
                await update.message.reply_document(document=open(output_path,'rb'), filename=os.path.basename(output_path))

            elif convert_type == 'img2pdf':
                output_path = os.path.join(tmpdir, os.path.splitext(file_name)[0] + ".pdf")
                result = images_to_pdf([input_path], output_path)
                if not result.get("ok"):
                    await status.edit_text(f"❌ {result.get('error')}", parse_mode=ParseMode.HTML)
                    return
                await status.edit_text(f"✅ Image to PDF Done", parse_mode=ParseMode.HTML)
                await update.message.reply_document(document=open(output_path,'rb'), filename=os.path.basename(output_path))

            elif convert_type == 'pdf2text':
                result = pdf_to_text(input_path)
                if not result.get("ok"):
                    await status.edit_text(f"❌ {result.get('error')}", parse_mode=ParseMode.HTML)
                    return
                text = result.get("text","")
                if len(text) > 4000:
                    txt_path = os.path.join(tmpdir, os.path.splitext(file_name)[0] + "_text.txt")
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    await status.edit_text(f"✅ PDF to Text Done - {result.get('chars')} chars\n\n{text[:1000]}...\n\nFull text file me hai:", parse_mode=ParseMode.HTML)
                    await update.message.reply_document(document=open(txt_path,'rb'), filename=os.path.basename(txt_path))
                else:
                    await status.edit_text(f"✅ PDF to Text ({result.get('chars')} chars):\n\n<pre>{text[:3500]}</pre>", parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ Conversion Error: {str(e)[:300]}", parse_mode=ParseMode.HTML)

# ========== SOCIAL SECURITY CHECKER ==========
async def igsecure_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text(
            "❌ <b>Use:</b> <code>/igsecure @username</code>\n\n"
            "📌 Example: <code>/igsecure @instagram</code>",
            parse_mode=ParseMode.HTML
        )
        return

    username = context.args[0]
    status = await update.message.reply_text(f"🔒 Security check for {username}...", parse_mode=ParseMode.HTML)

    try:
        result = social_security_check(username)
        if not result.get("ok"):
            await status.edit_text(f"❌ {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        txt = security_report_text(result)
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

# ========== CALLBACKS ==========
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "help_all":
        await help_cmd(update, context)
    elif query.data == "tools":
        await start(update, context)
    elif query.data == "check_joined":
        await check_joined_callback(update, context)

async def main_async():
    global app, loop
    loop = asyncio.get_running_loop()
    print("Building FULL app with 11 tools + grid 2-col...")
    
    app = Application.builder().token(BOT_TOKEN).build()

    # Core
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(help_callback))

    # Number Info
    app.add_handler(CommandHandler("numinfo", number_info_cmd))
    app.add_handler(CommandHandler("number", number_info_cmd))
    app.add_handler(CommandHandler("num", number_info_cmd))

    # TG Tools
    app.add_handler(CommandHandler("tginfo", tg_number_cmd))
    app.add_handler(CommandHandler("tgnum", tg_number_cmd))
    app.add_handler(CommandHandler("telegram", tg_number_cmd))
    app.add_handler(CommandHandler("paknum", pak_number_cmd))
    app.add_handler(CommandHandler("pak", pak_number_cmd))

    # Scraper
    app.add_handler(CommandHandler("channel_info", channel_info_cmd))
    app.add_handler(CommandHandler("scrape", scrape_cmd))
    app.add_handler(CommandHandler("scrape_search", scrape_search_cmd))
    app.add_handler(CommandHandler("scrape_media", scrape_media_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("batch", batch_cmd))

    # Insta
    app.add_handler(CommandHandler("insta", insta_cmd))
    app.add_handler(CommandHandler("instagram", insta_cmd))

    # Security
    app.add_handler(CommandHandler("igsecure", igsecure_cmd))
    app.add_handler(CommandHandler("security", igsecure_cmd))
    app.add_handler(CommandHandler("sec", igsecure_cmd))

    # Email
    app.add_handler(CommandHandler("email", email_cmd))

    # IP/Domain
    app.add_handler(CommandHandler("ip", ip_cmd))
    app.add_handler(CommandHandler("domain", domain_cmd))
    app.add_handler(CommandHandler("dns", dns_cmd))
    app.add_handler(CommandHandler("whois", whois_cmd))
    app.add_handler(CommandHandler("ssl", ssl_cmd))
    app.add_handler(CommandHandler("recon", domain_cmd))

    # File Converter
    app.add_handler(CommandHandler("excel2pdf", excel2pdf_cmd))
    app.add_handler(CommandHandler("csv2excel", excel2pdf_cmd))
    app.add_handler(CommandHandler("excel2csv", excel2pdf_cmd))
    app.add_handler(CommandHandler("img2pdf", excel2pdf_cmd))
    app.add_handler(CommandHandler("pdf2text", excel2pdf_cmd))

    # Website Extractor
    app.add_handler(CommandHandler("wextract", website_extract_cmd))
    app.add_handler(CommandHandler("emailextract", website_extract_cmd))
    app.add_handler(CommandHandler("linkextract", website_extract_cmd))

    # OCR
    app.add_handler(CommandHandler("ocr", excel2pdf_cmd))

    # Grid handler - must be before document handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_grid_button))

    # Document handlers
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file_converter))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_ocr_photo))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_photo))

    print("Initializing app...")
    await app.initialize()
    await app.start()

    print("Setting webhook...")
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        await app.bot.set_webhook(url=WEBHOOK_URL, allowed_updates=["message","callback_query"])
        print(f"Webhook set to {WEBHOOK_URL}")
        import requests
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data={'chat_id': '8607774564', 'text': f'✅ FULL 11 TOOLS WEBHOOK GRID LIVE! Try /start - 2-col grid'}, timeout=5)
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data={'chat_id': '6919943679', 'text': f'✅ FULL GRID LIVE! 11 tools'}, timeout=5)
    except Exception as e:
        print(f"Webhook set error: {e}")
        traceback.print_exc()

    print("FULL WEBHOOK GRID READY")
    while True:
        await asyncio.sleep(60)
        print("Full webhook alive 11 tools grid...")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
