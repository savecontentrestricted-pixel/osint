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

# ========== GRID MENU - 8 TOOLS (7 + TeraBox) ==========
KB_BTNS = [
    ["📱 NUMBER INFO", "🆔 TELEGRAM NUMBER"],
    ["🌐 IP/DOMAIN RECON", "🌐 WEBSITE EXTRACTOR"],
    ["💎 JS SECRET FINDER", "🐙 GITHUB LEAK HUNTER"],
    ["☁️ TERABOX EXTRACTOR", "📚 PDF RENAMER (Private)"],
]

def main_keyboard(admin: bool = False):
    """Grid keyboard - 8 tools clean, no commands - PDF Renamer still owner only but in grid for all? Keep owner check in handler"""
    rows = [row[:] for row in KB_BTNS]
    # If not admin, hide PDF Renamer row? Actually keep it but handler will block
    # For clean: if not admin, remove PDF Renamer from last row
    if not admin:
        # Remove PDF Renamer from grid for non-admin, keep only TeraBox
        new_rows = []
        for row in rows:
            new_row = [b for b in row if "PDF RENAMER" not in b]
            if new_row:
                new_rows.append(new_row)
        rows = new_rows
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

# Button text -> internal mode mapping - 8 TOOLS
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
    "JS SECRET FINDER": "jsfinder",
    "JS SECRETS": "jsfinder",
    "JS SECRET": "jsfinder",
    "JS FINDER": "jsfinder",
    "SECRET FINDER": "jsfinder",
    "GITHUB LEAK HUNTER": "ghleak",
    "GITHUB LEAKS": "ghleak",
    "GITHUB LEAK": "ghleak",
    "GITHUB": "ghleak",
    "LEAK HUNTER": "ghleak",
    "TERABOX EXTRACTOR": "terabox",
    "TERABOX": "terabox",
    "TERABOX STREAM": "terabox",
    "TERABOX FILE": "terabox",
}

# Prompt texts for grid tools - 8 TOOLS CLEAN, NO COMMANDS
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
    "jsfinder": {
        "head": "💎 JS SECRET FINDER - PRO",
        "ask": "Website URL bhejein:",
        "ex": "https://example.com",
    },
    "ghleak": {
        "head": "🐙 GITHUB LEAK HUNTER - PRO",
        "ask": "Keyword bhejein (domain/email):",
        "ex": "example.com",
    },
    "terabox": {
        "head": "☁️ TERABOX EXTRACTOR - PRO",
        "ask": "TeraBox URL bhejein:",
        "ex": "https://1024terabox.com/s/1AbCd...",
    },
}

import config
from modules.ip_domain_recon import ip_lookup, dns_lookup, whois_lookup, ssl_check, full_recon
from modules.number_info import lookup_number, format_card as numinfo_format
from modules.telegram_tools import lookup_tg, lookup_pak, format_tg_card, format_pak_card
from modules.website_extractor import website_extractor
from modules.pdf_renamer import rename_pdf_filename, batch_rename, HACKER_NAME, OWNER_ID as PDF_OWNER_ID
from modules.js_secret_finder import js_secret_finder, format_js_report
from modules.github_leak_hunter import github_leak_hunter, format_github_report
from modules.terabox_extractor import extract_terabox, format_terabox_report

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
🚀 <b>OSINT Hunter Hub - 7 PRO TOOLS</b>
{pc_mid}

👋 <b>Hello {user.first_name}!</b>

🔥 <b>7 Powerful Tools - Clean Grid, No Commands!</b>
Neeche 👇 grid button pe click karo

{pc_mid}

<b>📱 Grid Tools (Pro - Clean):</b>

📱 NUMBER INFO       |  🆔 TG NUMBER
🌐 IP/DOMAIN RECON  |  🌐 WEBSITE EXTRACTOR
💎 JS SECRET FINDER |  🐙 GITHUB LEAKS
📚 PDF RENAMER (Private - Owner Only)

{pc_mid}

<b>📌 How to Use:</b>
Grid se tool select karo, phir data bhejo
Example: 7857843092, @username, example.com

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
            if "terabox.com" in raw or "1024terabox.com" in raw or "terabox" in raw.lower():
                current_mode = "terabox"
            elif len(d) == 10 and d[0] in "6789":
                current_mode = "numinfo"
            elif raw.startswith("@") or raw.replace("@","").replace("_","").isalnum() and len(raw) >= 4 and len(raw) <= 32 and " " not in raw:
                # Could be telegram username
                if raw.startswith("@"):
                    current_mode = "tgtools"
            elif "." in raw and ("http" in raw or "/" not in raw):
                # domain or website
                if raw.startswith("http"):
                    # Check if it's terabox url already handled above, else wextract
                    if "terabox" in raw.lower():
                        current_mode = "terabox"
                    else:
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
        elif current_mode == "ip" or current_mode == "domain":
            # Check if IP or domain
            if "." in text and text.replace(".","").replace(":","").replace("/","").isdigit() or text.count(".")==3:
                context.args = [text]
                await ip_cmd(update, context)
            else:
                context.args = [text]
                await domain_cmd(update, context)
        elif current_mode == "wextract":
            context.args = [text]
            await website_extract_cmd(update, context)
        elif current_mode == "jsfinder":
            context.args = [text]
            await js_secret_cmd(update, context)
        elif current_mode == "ghleak":
            context.args = [text]
            await github_leak_cmd(update, context)
        elif current_mode == "terabox":
            context.args = [text]
            await terabox_cmd(update, context)
        elif current_mode == "pdf_rename":
            await update.message.reply_text(
                f"📚 <b>PDF RENAMER Mode ON</b>\n\n"
                f"Ab PDF bhejo Document ke roop me.\n"
                f"Naam auto: <code>Vivid.pdf -> 卄卂匚K乇尺.pdf</code>\n\n"
                f"Ek saath 10 bhej sakte ho.",
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
║  📖 <b>OSINT Hunter Hub - 7 PRO TOOLS</b>  ║
╚══════════════════════════════════════╝

<b>━━━━━━━━ Tool 1: Number Info ━━━━━━━━</b>
10 Digit Number bhejein: 7857843092
→ Name, Father, Address, Circle, Aadhaar masked

<b>━━━━━━━━ Tool 2: TG Tools ━━━━━━━━</b>
Telegram username bhejein: @Perfectamit65
→ Telegram ID + Mobile info

<b>━━━━━━━━ Tool 3: IP/Domain ━━━━━━━━</b>
IP ya Domain bhejein: 8.8.8.8
→ IP + VPN + Maps + WHOIS + SSL

<b>━━━━━━━━ Tool 4: Website Extractor ━━━━━━━━</b>
Website URL bhejein: https://example.com
→ Emails + Phones + Links + Meta

<b>━━━━━━━━ Tool 5: JS Secret Finder (PRO) ━━━━━━━━</b>
Website URL bhejein: https://example.com
→ JS files se API keys, endpoints, secrets
→ Bug bounty ke liye best, kisi bot me nahi!

<b>━━━━━━━━ Tool 6: GitHub Leak Hunter (PRO) ━━━━━━━━</b>
Keyword bhejein: example.com
→ GitHub public repos me leak search
→ API keys, passwords leak check

<b>━━━━━━━━ Tool 7: PDF Renamer (Private) ━━━━━━━━</b>
PDF bhejo, Vivid -> 卄卂匚K乇尺
→ Batch 10 PDFs
→ Owner only

<b>🛡️ Safety:</b>
• Force join: @osint_xpert
• Owner: @Supermannn_x

/start se grid dekho - Clean, no commands!
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
# ========== INSTAGRAM ==========
# ========== EMAIL ==========
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
# ========== OCR ==========
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

# ========== JS SECRET FINDER - PRO ==========
async def js_secret_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text(
            "❌ <b>Use:</b> <code>/jsfind https://example.com</code>\n\n"
            "📌 Example: <code>/jsfind https://example.com</code>\n"
            "Bot us site ke JS files se API keys, endpoints nikalega",
            parse_mode=ParseMode.HTML
        )
        return

    url = context.args[0]
    status = await update.message.reply_text(
        f"💎 <b>JS Secret Finder Scanning...</b>\n\n"
        f"🌐 URL: <code>{url}</code>\n"
        f"⏳ JS files extract kar raha hu...",
        parse_mode=ParseMode.HTML
    )

    try:
        result = js_secret_finder(url)
        txt = format_js_report(result)
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ Error: {str(e)[:300]}", parse_mode=ParseMode.HTML)

# ========== GITHUB LEAK HUNTER - PRO ==========
async def github_leak_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text(
            "❌ <b>Use:</b> <code>/ghleak example.com</code>\n\n"
            "📌 Example: <code>/ghleak example.com</code> ya <code>/ghleak apikey</code>\n"
            "GitHub public repos me leak search",
            parse_mode=ParseMode.HTML
        )
        return

    query = " ".join(context.args)
    status = await update.message.reply_text(
        f"🐙 <b>GitHub Leak Hunter Searching...</b>\n\n"
        f"🔍 Query: <code>{query}</code>\n"
        f"⏳ GitHub API se search...",
        parse_mode=ParseMode.HTML
    )

    try:
        result = github_leak_hunter(query)
        txt = format_github_report(result)
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ Error: {str(e)[:300]}", parse_mode=ParseMode.HTML)

# ========== TERABOX EXTRACTOR - PRO ==========
async def terabox_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await update.message.reply_text(
            "❌ <b>Use:</b> <code>/terabox https://1024terabox.com/s/xxxxx</code>\n\n"
            "📌 Example: <code>/terabox https://1024terabox.com/s/1AbCdEfGh</code>\n"
            "TeraBox se direct download + stream link",
            parse_mode=ParseMode.HTML
        )
        return

    url = context.args[0]
    status = await update.message.reply_text(
        f"☁️ <b>TeraBox Extracting...</b>\n\n"
        f"🌐 URL: <code>{url[:80]}</code>\n"
        f"⏳ 4 APIs combination se try kar raha hu (2 LIVE)...\n"
        f"Note: Upstream Render service 50s me wake up hota hai, thoda wait karo",
        parse_mode=ParseMode.HTML
    )

    try:
        result = extract_terabox(url)
        txt = format_terabox_report(result)
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ Error: {str(e)[:500]}", parse_mode=ParseMode.HTML)

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
    print("Building 8 TOOLS app - 5 old + 2 pro + TeraBox...")
    
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

    # PRO TOOLS - JS Secret Finder + GitHub Leak Hunter
    app.add_handler(CommandHandler("jsfind", js_secret_cmd))
    app.add_handler(CommandHandler("jssecret", js_secret_cmd))
    app.add_handler(CommandHandler("secrets", js_secret_cmd))
    app.add_handler(CommandHandler("ghleak", github_leak_cmd))
    app.add_handler(CommandHandler("github", github_leak_cmd))
    app.add_handler(CommandHandler("leak", github_leak_cmd))

    # TeraBox Extractor - NEW
    app.add_handler(CommandHandler("terabox", terabox_cmd))
    app.add_handler(CommandHandler("tb", terabox_cmd))
    app.add_handler(CommandHandler("teraboxdl", terabox_cmd))

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
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data={'chat_id': '8607774564', 'text': f'✅ 7 TOOLS LIVE! 5 old + JS Secrets + GitHub Leaks - Clean no commands grid!'}, timeout=5)
    except Exception as e:
        print(f"Webhook set error: {e}")
        traceback.print_exc()

    print("7 TOOLS WEBHOOK READY - Clean grid, no commands, powerful!")
    while True:
        await asyncio.sleep(60)
        print("7 tools alive...")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
