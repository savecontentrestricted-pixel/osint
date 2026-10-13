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

import threading
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler

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

# ========== GRID MENU - SLIM 5 TOOLS ONLY (User requested delete rest) ==========
# Kept: NUMBER INFO, TG INFO, IP/DOMAIN, WEBSITE EXTRACTOR, PDF RENAMER (Private Owner)
KB_BTNS = [
    ["📱 NUMBER INFO", "🆔 TELEGRAM NUMBER"],
    ["🌐 IP/DOMAIN RECON", "🌐 WEBSITE EXTRACTOR"],
]

def main_keyboard(admin: bool = False):
    """Grid keyboard - 5 tools only as per user request"""
    rows = [row[:] for row in KB_BTNS]
    # PDF Renamer is private but user wants to keep it - show only for admin/owner
    if admin:
        rows.append(["📚 PDF RENAMER (Private)"])
    # For non-admin, show 4 tools only
    try:
        return ReplyKeyboardMarkup(
            [[KeyboardButton(t) for t in row] for row in rows],
            resize_keyboard=True,
        )
    except Exception as e:
        print(f"Keyboard create failed: {e}")
        return ReplyKeyboardMarkup(
            [[KeyboardButton(t) for t in row] for row in rows],
            resize_keyboard=True,
        )

def kb_for(uid: int):
    is_admin_user = False
    try:
        is_admin_user = config.is_admin(uid)
    except:
        is_admin_user = (uid == config.ADMIN_ID)
    return main_keyboard(admin=is_admin_user)

# Button text -> internal mode mapping - SLIM 5 TOOLS ONLY
BTN_MODE_MAP = {
    "IP/DOMAIN RECON": "ip",
    "IP DOMAIN": "ip",
    "IP RECON": "ip",
    "DOMAIN RECON": "domain",
    "DOMAIN": "domain",
    "IP INFO": "ip",
    "IP": "ip",
    "NUMBER INFO": "numinfo",
    "NUMBER INFO V2 ENGINE": "numinfo",
    "NUMBER": "numinfo",
    "NUM INFO": "numinfo",
    "NUMINFO": "numinfo",
    "TELEGRAM NUMBER": "tgtools",
    "TG NUMBER": "tgtools",
    "TG INFO": "tgtools",
    "TELEGRAM": "tgtools",
    "WEBSITE EXTRACTOR": "wextract",
    "WEBSITE": "wextract",
    "WEXTRACT": "wextract",
    "PDF RENAMER": "pdf_rename",
    "PDF RENAMER (PRIVATE)": "pdf_rename",
    "PDF RENAMER (PRIVATE) ": "pdf_rename",
    "HACKER PDF": "pdf_rename",
    "HACKER": "pdf_rename",
}

# Prompt texts for grid tools - SLIM 5 TOOLS ONLY
GRID_PROMPTS = {
    "ip": {
        "head": "🌐 IP/DOMAIN RECON",
        "ask": "IP ya Domain bhejein:",
        "ex": "8.8.8.8",
    },
    "numinfo": {
        "head": "📱 NUMBER INFO V2 ENGINE",
        "ask": "10 Digit Number bhejein:",
        "ex": "7857843092",
    },
    "tgtools": {
        "head": "🆔 TELEGRAM NUMBER",
        "ask": "Telegram username ya user ID bhejein:",
        "ex": "@Perfectamit65",
    },
    "wextract": {
        "head": "🌐 WEBSITE EXTRACTOR",
        "ask": "Website URL bhejein:",
        "ex": "https://example.com",
    },
    "pdf_rename": {
        "head": "📚 PDF RENAMER (Private - Owner Only)",
        "ask": "PDF bhejo, naam auto change hoga:",
        "ex": "Vivid.pdf -> 卄卂匚K乇尺.pdf",
    },
}

import config
from modules.ip_domain_recon import ip_lookup, dns_lookup, whois_lookup, ssl_check, full_recon
from modules.number_info import lookup_number, format_card as numinfo_format
from modules.telegram_tools import lookup_tg, lookup_pak, format_tg_card, format_pak_card
from modules.website_extractor import website_extractor
from modules.pdf_renamer import rename_pdf_filename, batch_rename, HACKER_NAME, OWNER_ID as PDF_OWNER_ID

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        
        pc_mid = "━━━━━━━━━━━━━━━━━━━━━━"
        txt = f"""
🚀 <b>OSINT Hunter Hub - SLIM 5 TOOLS</b>
{pc_mid}

👋 <b>Hello {user.first_name}!</b>

🔥 <b>5 Powerful Tools - Grid Menu Me!</b>
Neeche 👇 grid button pe click karo

{pc_mid}

<b>📱 Grid Tools (Slim):</b>

📱 NUMBER INFO       |  🆔 TG NUMBER
🌐 IP/DOMAIN RECON  |  🌐 WEBSITE EXTRACTOR
📚 PDF RENAMER (Private - Owner Only)

{pc_mid}

<b>📌 Quick Examples:</b>
<code>/numinfo 9204507743</code>
<code>/tginfo @username</code>
<code>/ip 8.8.8.8</code>
<code>/domain google.com</code>
<code>/wextract https://site.com</code>
<code>/pdfrename (owner only)</code>

{pc_mid}

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
    """Handle grid button presses like utility-duniya-bot + auto-process inputs"""
    try:
        if not await check_force_join(update, context):
            return
        
        text = update.message.text.strip()
        # Clean emoji and get mode - robust for all emojis including 📚
        clean_text = text
        # Remove emoji prefix - list includes all grid emojis
        for emoji in ["📡 ", "📸 ", "📧 ", "🌐 ", "🖼️ ", "🔒 ", "📱 ", "🆔 ", "📝 ", "📊 ", "📜 ", "👑 ", "📢 ", "📚 ", "🔧 "]:
            if clean_text.startswith(emoji):
                clean_text = clean_text[len(emoji):].strip()
                break
        # Fallback: strip any leading non-alphanumeric (emoji) characters
        if clean_text == text:
            # Try to remove first char if it's emoji/non-ascii
            import re
            # Remove leading emoji/non-letter chars
            m = re.match(r'^[^A-Za-z0-9]+(.*)', text)
            if m:
                possible = m.group(1).strip()
                if possible:
                    clean_text = possible
        
        mode = BTN_MODE_MAP.get(clean_text.upper())
        if not mode:
            mode = BTN_MODE_MAP.get(text.upper())
        # Also try without (Private) suffix
        if not mode:
            # Remove (Private) etc
            import re
            no_bracket = re.sub(r'\s*\(.*?\)\s*', '', clean_text).strip()
            mode = BTN_MODE_MAP.get(no_bracket.upper())
        if not mode:
            no_bracket2 = re.sub(r'\s*\(.*?\)\s*', '', text).strip()
            mode = BTN_MODE_MAP.get(no_bracket2.upper())
        
        # If it's a grid button, show prompt and set mode
        if mode:
            # Handle special modes
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

            if mode == "admin":
                # Admin panel placeholder
                if not config.is_admin(update.effective_user.id):
                    await update.message.reply_text("❌ Owner only", parse_mode=ParseMode.HTML)
                    return
                await update.message.reply_text("🔧 <b>ADMIN PANEL</b>\n\nOwner: 8607774564\nTools: 12 (11 public + 1 private)", parse_mode=ParseMode.HTML)
                return

            if mode == "pdf_rename":
                # Owner only private tool
                if not config.is_admin(update.effective_user.id) and update.effective_user.id != 8607774564:
                    await update.message.reply_text("❌ <b>This tool is Private - Owner Only</b>\n\nSirf owner use kar sakta hai.", parse_mode=ParseMode.HTML)
                    return
                # Set mode and show detailed prompt
                try:
                    context.user_data["mode"] = mode
                    context.user_data["pdf_batch"] = []  # reset batch
                except:
                    pass
                prompt = GRID_PROMPTS.get(mode)
                pc_mid = "━━━━━━━━━━━━━━━━━━━━━━"
                txt = f"""
📚 <b>PDF RENAMER (Private - Owner Only)</b>
{pc_mid}

🔗 <b>PDF bhejo, naam auto change hoga:</b>

     <code>Vivid.pdf -> 卄卂匚K乇尺.pdf</code>

{pc_mid}

📌 <b>Kaise kaam karta hai:</b>
• Aap apne chat se PDF forward karo
• Bot auto .pdf se pehle wala naam hatayega
• Vivid / koi bhi extractor naam -> 卄卂匚K乇尺
• Example:
  <code>LECTURE-6 POLITY Vivid.pdf</code>
  →
  <code>LECTURE-6 POLITY 卄卂匚K乇尺.pdf</code>

• Ek saath 10 PDFs bhej sakte ho
• Same content, sirf naam change

{pc_mid}

📤 <b>Ab PDF bhejo (Document ke roop me)</b>
"""
                await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
                return
            
            # For tool modes, show prompt card - CLEAN LIKE IMAGE
            prompt = GRID_PROMPTS.get(mode)
            if not prompt:
                return
            
            try:
                context.user_data["mode"] = mode
            except:
                pass
            
            pc_mid = "━━━━━━━━━━━━━━━━━━━━━━"
            head = prompt['head']
            if " " in head:
                icon, rest = head.split(" ", 1)
                header_line = f"{icon} <b>{rest}</b>"
            else:
                header_line = f"<b>{head}</b>"
            
            txt = f"""
{header_line}
{pc_mid}

🔗 <b>{prompt['ask']}</b>

     <code>{prompt['ex']}</code>
"""
            await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
            return
        
        # If not a grid button, check if user has a mode set (from previous grid click)
        # Then treat this text as input for that mode - AUTO DETECT like utility bot
        current_mode = None
        try:
            current_mode = context.user_data.get("mode")
        except:
            pass
        
        # Auto-detect mode from input if no mode set (like utility bot does)
        if not current_mode:
            import re
            raw = text
            d = re.sub(r"\D", "", raw)
            # Auto detect
            if len(d) == 10 and d[0] in "6789":
                current_mode = "numinfo"
            elif "@" in raw and "." in raw and " " not in raw:
                # email
                if re.match(r"^[^@]+@[^@]+\.[^@]+$", raw):
                    current_mode = "email"
            elif raw.startswith("@") or raw.replace("@","").replace("_","").isalnum() and len(raw) >= 4 and len(raw) <= 32 and " " not in raw:
                # Could be telegram username or insta, but if mode was tgtools or insta, use that
                # For now, if it starts with @, treat as tgtools
                if raw.startswith("@"):
                    current_mode = "tgtools"
            elif "." in raw and ("http" in raw or "/" not in raw):
                # domain or website
                if raw.startswith("http"):
                    current_mode = "wextract"
                elif "." in raw and " " not in raw and len(raw) > 3:
                    current_mode = "ip"
        
        if not current_mode:
            # No mode and can't auto-detect, ignore (or show menu)
            return
        
        # Process input based on mode - call appropriate lookup
        # Clear mode after processing? Keep it for multiple lookups, but we can clear after one
        # For now, keep mode so user can send multiple numbers without re-clicking
        
        print(f"Processing input '{text}' as mode {current_mode}")
        
        # Route to appropriate handler based on mode
        if current_mode == "numinfo":
            # Simulate /numinfo command
            context.args = [text]
            await number_info_cmd(update, context)
        elif current_mode == "tgtools":
            context.args = [text]
            await tg_number_cmd(update, context)
        elif current_mode == "email":
            context.args = [text]
            await email_cmd(update, context)
        elif current_mode == "ip" or current_mode == "domain":
            # Check if IP or domain
            if "." in text and text.replace(".","").replace(":","").replace("/","").isdigit() or text.count(".")==3:
                context.args = [text]
                await ip_cmd(update, context)
            else:
                context.args = [text]
                await domain_cmd(update, context)
        elif current_mode == "insta":
            context.args = [text]
            await insta_cmd(update, context)
        elif current_mode == "security":
            context.args = [text]
            await igsecure_cmd(update, context)
        elif current_mode == "wextract":
            context.args = [text]
            await website_extract_cmd(update, context)
        elif current_mode == "scraper":
            # For scraper, need channel + limit
            parts = text.split()
            if len(parts) >= 1:
                context.args = parts
                await scrape_cmd(update, context)
            else:
                await update.message.reply_text("Channel bhejo: @username", parse_mode=ParseMode.HTML)
        elif current_mode == "pdf_rename":
            await update.message.reply_text(
                f"📚 <b>PDF RENAMER Mode ON</b>\n\n"
                f"Ab PDF bhejo Document ke roop me.\n"
                f"Naam auto: <code>Vivid.pdf -> 卄卂匚K乇尺.pdf</code>\n\n"
                f"Ek saath 10 bhej sakte ho.",
                parse_mode=ParseMode.HTML
            )
        elif current_mode == "converter" or current_mode == "ocr" or current_mode == "exif":
            await update.message.reply_text(
                f"📎 <b>{current_mode.upper()}</b> ke liye file bhejo as Document.\n\n"
                f"Prompt: {GRID_PROMPTS.get(current_mode, {}).get('ask','')}\n"
                f"Example: {GRID_PROMPTS.get(current_mode, {}).get('ex','')}",
                parse_mode=ParseMode.HTML
            )
        else:
            # Generic
            await update.message.reply_text(f"Processing {current_mode}: {text}", parse_mode=ParseMode.HTML)
            
    except Exception as e:
        print(f"Grid handler error: {e}")
        traceback.print_exc()
        try:
            await update.message.reply_text(f"❌ Error: {str(e)[:200]}", parse_mode=ParseMode.HTML)
        except:
            pass

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return

    txt = """
╔══════════════════════════════════════╗
║  📖 <b>OSINT Hunter Hub - SLIM 5 TOOLS</b>  ║
╚══════════════════════════════════════╝

<b>━━━━━━━━ Tool 1: Number Info ━━━━━━━━</b>
/numinfo 9876543210
/number 9876543210
/num 9876543210
→ Name, Father, Address, Circle, Aadhaar masked, Alt phone, Response ms
→ No data pe: ❌ No records found...

<b>━━━━━━━━ Tool 2: TG Tools ━━━━━━━━</b>
/tginfo @username
/tgnum @username
/telegram @username
→ Telegram username se info

<b>━━━━━━━━ Tool 3: IP/Domain ━━━━━━━━</b>
/ip 8.8.8.8 → IP + VPN detection + Maps
/domain google.com → Full recon
/dns google.com → DNS records
/whois google.com → WHOIS
/ssl google.com → SSL cert

<b>━━━━━━━━ Tool 4: Website Extractor ━━━━━━━━</b>
/wextract https://site.com → Emails + Phones + Links + Meta

<b>━━━━━━━━ Tool 5: PDF Renamer (Private) ━━━━━━━━</b>
/pdfrename
/hacker
→ PDF filename me Vivid -> 卄卂匚K乇尺
→ Batch 10 PDFs
→ Owner only 8607774564

<b>🛡️ Safety:</b>
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

# ========== PDF RENAMER (Private Owner Only) ==========
async def pdf_rename_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    if not config.is_admin(uid) and uid != 8607774564:
        await update.message.reply_text("❌ <b>This tool is Private - Owner Only</b>\n\nSirf owner 8607774564 use kar sakta hai.", parse_mode=ParseMode.HTML)
        return
    try:
        context.user_data["mode"] = "pdf_rename"
        context.user_data["pdf_batch"] = []
    except:
        pass
    pc_mid = "━━━━━━━━━━━━━━━━━━━━━━"
    txt = f"""
📚 <b>PDF RENAMER (Private - Owner Only)</b>
{pc_mid}

🔗 <b>PDF bhejo, naam auto change hoga:</b>

     <code>Vivid.pdf -> 卄卂匚K乇尺.pdf</code>

{pc_mid}

📌 <b>Kaise kaam karta hai:</b>
• Aap apne chat se PDF forward karo
• Bot auto .pdf se pehle wala naam hatayega
• Vivid / koi bhi extractor naam -> 卄卂匚K乇尺
• Example:
  <code>LECTURE-6 POLITY Vivid.pdf</code>
  →
  <code>LECTURE-6 POLITY 卄卂匚K乇尺.pdf</code>

• Ek saath 10 PDFs bhej sakte ho
• Same content, sirf naam change

{pc_mid}

📤 <b>Ab PDF bhejo (Document ke roop me)</b>
"""
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

async def handle_pdf_renamer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    if not config.is_admin(uid) and uid != 8607774564:
        return  # silently ignore for non-owner, private tool

    # Only if mode is pdf_rename or user is owner sending PDF (auto)
    try:
        cur_mode = context.user_data.get("mode")
    except:
        cur_mode = None

    # Allow owner to send PDFs even without mode, but prefer mode
    # If not in pdf_rename mode and owner, check caption/file - if it's pdf, still process if owner explicitly wants?
    # For safety, only process when mode == pdf_rename OR command was used recently (within session)
    # We'll also allow if no mode but file is pdf and owner id matches - to be user-friendly
    if cur_mode != "pdf_rename":
        # If owner sends PDF without setting mode, auto-set mode for convenience
        # But only for PDFs
        if update.message.document and update.message.document.file_name and update.message.document.file_name.lower().endswith('.pdf'):
            # Auto enable for owner
            try:
                context.user_data["mode"] = "pdf_rename"
                cur_mode = "pdf_rename"
            except:
                pass
        else:
            return

    if not update.message.document:
        return

    doc = update.message.document
    file_name = doc.file_name or "document.pdf"
    if not file_name.lower().endswith('.pdf'):
        # Only PDFs
        await update.message.reply_text(f"❌ Sirf PDF bhejo, ye hai: {file_name}", parse_mode=ParseMode.HTML)
        return

    # Rename logic
    new_name = rename_pdf_filename(file_name)

    status = await update.message.reply_text(
        f"📚 <b>PDF Renaming...</b>\n\n"
        f"📄 Old: <code>{file_name}</code>\n"
        f"📝 New: <code>{new_name}</code>\n"
        f"⏳ Downloading...",
        parse_mode=ParseMode.HTML
    )

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, file_name)
            output_path = os.path.join(tmpdir, new_name)

            # Robust download with longer timeout and retry
            # Try PTB get_file with extended timeouts
            file_obj = None
            for attempt in range(3):
                try:
                    file_obj = await context.bot.get_file(
                        doc.file_id,
                        read_timeout=120,
                        write_timeout=120,
                        connect_timeout=60,
                        pool_timeout=60
                    )
                    break
                except Exception as e:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(1 + attempt)

            # Download with retry, try both PTB method and direct requests fallback
            downloaded = False
            last_err = None
            for attempt in range(3):
                try:
                    # Try PTB download
                    await file_obj.download_to_drive(custom_path=input_path)
                    if os.path.exists(input_path) and os.path.getsize(input_path) > 0:
                        downloaded = True
                        break
                except Exception as e:
                    last_err = e
                    logger.warning(f"Download attempt {attempt+1} failed: {e}")
                    # Fallback: direct download via file_path URL
                    try:
                        import requests
                        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_obj.file_path}"
                        # Use streaming download with long timeout
                        with requests.get(file_url, stream=True, timeout=120) as r:
                            r.raise_for_status()
                            with open(input_path, 'wb') as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                        if os.path.exists(input_path) and os.path.getsize(input_path) > 0:
                            downloaded = True
                            break
                    except Exception as e2:
                        last_err = e2
                        logger.warning(f"Direct download attempt {attempt+1} failed: {e2}")
                        await asyncio.sleep(2)

            if not downloaded:
                raise Exception(f"Failed to download after 3 attempts: {last_err}")

            # Optional: Replace VIVID inside PDF content if requested
            # Try to replace text inside PDF using PyMuPDF if available, else keep original
            try:
                # Check if user wants content replacement too (jaha jaha vivid likha hai)
                # We'll attempt to replace VIVID text inside PDF if possible
                # This is best-effort, won't fail if library missing
                replaced_content = False
                try:
                    # Try PyMuPDF (fitz) if available
                    import fitz  # PyMuPDF
                    doc_pdf = fitz.open(input_path)
                    for page in doc_pdf:
                        # Search for VIVID (case-insensitive) and replace
                        # Note: This is simple text replacement, may not work for all PDFs
                        text_instances = page.search_for("VIVID")
                        for inst in text_instances:
                            # Add redaction and new text
                            page.add_redact_annot(inst, text=HACKER_NAME, fill=(1,1,1))
                        # Also search lowercase
                        text_instances2 = page.search_for("Vivid")
                        for inst in text_instances2:
                            page.add_redact_annot(inst, text=HACKER_NAME, fill=(1,1,1))
                        if text_instances or text_instances2:
                            page.apply_redactions()
                            replaced_content = True
                    if replaced_content:
                        doc_pdf.save(output_path)
                        doc_pdf.close()
                    else:
                        doc_pdf.close()
                        # No VIVID found inside, just copy file
                        import shutil
                        shutil.copy2(input_path, output_path)
                except ImportError:
                    # PyMuPDF not available, try PyPDF2 + reportlab fallback or just copy
                    import shutil
                    shutil.copy2(input_path, output_path)
                except Exception as e:
                    logger.warning(f"PDF content replace failed (non-critical): {e}")
                    import shutil
                    shutil.copy2(input_path, output_path)
            except Exception:
                import shutil
                shutil.copy2(input_path, output_path)

            # Ensure output exists, if not copy input
            if not os.path.exists(output_path):
                import shutil
                shutil.copy2(input_path, output_path)

            await status.edit_text(
                f"✅ <b>Renamed!</b>\n\n"
                f"📄 Old: <code>{file_name}</code>\n"
                f"📝 New: <code>{new_name}</code>\n"
                f"📦 Size: {os.path.getsize(output_path)//1024} KB\n\n"
                f"📤 Sending...",
                parse_mode=ParseMode.HTML
            )

            # Send back with new name - with increased timeout for upload
            await update.message.reply_document(
                document=open(output_path, 'rb'),
                filename=new_name,
                caption=f"✅ Renamed: <code>{file_name}</code> → <code>{new_name}</code>\n\n"
                        f"🔥 卄卂匚K乇尺\n"
                        f"📦 Batch supported (10 at once)",
                parse_mode=ParseMode.HTML,
                read_timeout=120,
                write_timeout=120,
                connect_timeout=60,
                pool_timeout=60
            )

            try:
                await status.delete()
            except:
                pass

            # Track batch count
            try:
                batch = context.user_data.get("pdf_batch", [])
                batch.append(new_name)
                if len(batch) > 10:
                    batch = batch[-10:]
                context.user_data["pdf_batch"] = batch
                if len(batch) >= 2:
                    await update.message.reply_text(
                        f"📦 Batch: {len(batch)} PDFs renamed in this session\n"
                        f"Last: {', '.join(batch[-3:])}",
                        parse_mode=ParseMode.HTML
                    )
            except:
                pass

    except Exception as e:
        logger.exception(e)
        try:
            await status.edit_text(f"❌ Rename Error: {str(e)[:500]}\n\nTip: File size {doc.file_size//1024}KB, try smaller file or /pdfrename again", parse_mode=ParseMode.HTML)
        except:
            try:
                await update.message.reply_text(f"❌ Rename Error: {str(e)[:500]}", parse_mode=ParseMode.HTML)
            except:
                pass

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
    print("Building SLIM 5 TOOLS app...")
    
    app = Application.builder().token(BOT_TOKEN).build()

    # Core
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(help_callback))

    # Number Info - KEEP
    app.add_handler(CommandHandler("numinfo", number_info_cmd))
    app.add_handler(CommandHandler("number", number_info_cmd))
    app.add_handler(CommandHandler("num", number_info_cmd))

    # TG Tools - KEEP
    app.add_handler(CommandHandler("tginfo", tg_number_cmd))
    app.add_handler(CommandHandler("tgnum", tg_number_cmd))
    app.add_handler(CommandHandler("telegram", tg_number_cmd))
    app.add_handler(CommandHandler("paknum", pak_number_cmd))
    app.add_handler(CommandHandler("pak", pak_number_cmd))

    # IP/Domain - KEEP
    app.add_handler(CommandHandler("ip", ip_cmd))
    app.add_handler(CommandHandler("domain", domain_cmd))
    app.add_handler(CommandHandler("dns", dns_cmd))
    app.add_handler(CommandHandler("whois", whois_cmd))
    app.add_handler(CommandHandler("ssl", ssl_cmd))
    app.add_handler(CommandHandler("recon", domain_cmd))

    # Website Extractor - KEEP
    app.add_handler(CommandHandler("wextract", website_extract_cmd))
    app.add_handler(CommandHandler("emailextract", website_extract_cmd))
    app.add_handler(CommandHandler("linkextract", website_extract_cmd))

    # PDF Renamer - Private Owner Only - KEEP
    app.add_handler(CommandHandler("pdfrename", pdf_rename_cmd))
    app.add_handler(CommandHandler("pdf_rename", pdf_rename_cmd))
    app.add_handler(CommandHandler("hacker", pdf_rename_cmd))
    app.add_handler(CommandHandler("hackerpdf", pdf_rename_cmd))

    # Grid handler - must be before document handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_grid_button))

    # Document handlers - PDF Renamer first (owner only, priority)
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf_renamer))

    print("Initializing app...")
    await app.initialize()
    await app.start()

    print("Setting webhook...")
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        await app.bot.set_webhook(url=WEBHOOK_URL, allowed_updates=["message","callback_query"])
        print(f"Webhook set to {WEBHOOK_URL}")
        import requests
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data={'chat_id': '8607774564', 'text': f'✅ SLIM 5 TOOLS LIVE! Number+TG+IP+Website+PDF Renamer'}, timeout=5)
    except Exception as e:
        print(f"Webhook set error: {e}")
        traceback.print_exc()

    print("SLIM 5 TOOLS WEBHOOK READY")
    while True:
        await asyncio.sleep(60)
        print("Slim 5 tools alive...")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
