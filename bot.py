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
import html
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
        # Fast health check for Render - must respond <100ms
        try:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.send_header('Cache-Control','no-cache')
            self.end_headers()
            if self.path in ['/health', '/ping', '/healthz']:
                self.wfile.write(b'OK - Bot Alive')
            elif self.path == '/webhook':
                self.wfile.write(b'Webhook endpoint - POST only')
            else:
                html = b"&lt;html&gt;&lt;body&gt;&lt;h1&gt;OSINT Hunter Hub 8 TOOLS FAST STABLE LIVE</h1>&lt;p&gt;All 8 tools working - No delay</p>&lt;p&gt;Webhook: /webhook</p>&lt;p&gt;Health: /health</p></body></html>"
                self.wfile.write(html)
        except:
            pass
    
    def do_POST(self):
        try:
            if self.path == '/webhook':
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                try:
                    data = json.loads(body)
                    # Fast ack first - critical for no delay
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'OK')
                    # Then process async
                    print(f"WEBHOOK POST update_id {data.get('update_id')} - Fast ACK sent")
                    threading.Thread(target=process_update_sync, args=(data,), daemon=True).start()
                    return
                except Exception as je:
                    print(f"JSON parse error: {je}")
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'OK')
                    return
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"Webhook POST error: {e}")
            try:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')
            except:
                pass
    
    def log_message(self, *args): pass

def process_update_sync(data):
    try:
        global loop
        # Wait for loop to be ready max 5 sec
        for _ in range(50):
            if loop and app:
                break
            time.sleep(0.1)
        if loop and app:
            asyncio.run_coroutine_threadsafe(handle_update(data), loop)
        else:
            print("Loop/App not ready, dropping update", data.get('update_id'))
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
        print(f"WEBHOOK server on 0.0.0.0:{PORT} -> {WEBHOOK_URL} - FAST STABLE MODE")
        HTTPServer(('0.0.0.0', PORT), WebhookHandler).serve_forever()
    except Exception as e:
        print(f"Keepalive error: {e}")
        traceback.print_exc()

threading.Thread(target=keepalive, daemon=False).start()

# Self-ping to prevent Render sleep (every 10 min)
def self_ping_loop():
    time.sleep(30)
    while True:
        try:
            import requests
            # Ping own health endpoint to keep alive
            requests.get(f"http://127.0.0.1:{PORT}/health", timeout=5)
            print("Self-ping OK - keeping alive")
        except Exception as e:
            print(f"Self-ping fail: {e}")
        time.sleep(600)  # 10 min

threading.Thread(target=self_ping_loop, daemon=True).start()

# Removed spam starting message - only notify after full init in main_async

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from telegram.constants import ParseMode
from telegram.error import BadRequest

# ========== GRID MENU - 8 TOOLS + PREMIUM + ADMIN ==========
KB_BTNS = [
    ["📱 NUMBER INFO", "🆔 TELEGRAM NUMBER"],
    ["🌐 IP/DOMAIN RECON", "🌐 WEBSITE EXTRACTOR"],
    ["💎 JS SECRET FINDER", "🐙 GITHUB LEAK HUNTER"],
    ["☁️ TERABOX EXTRACTOR", "👑 PREMIUM"],
]

def main_keyboard(admin: bool = False):
    """Grid keyboard - 8 tools + Premium + Admin controls"""
    rows = [row[:] for row in KB_BTNS]
    if admin:
        rows.append(["📚 PDF RENAMER (Private)", "🛠️ ADMIN PANEL"])
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

# Button text -> internal mode mapping - 9 TOOLS
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
    "HACKER PDF": "pdf_rename",
    "HACKER": "pdf_rename",
    "JS SECRET FINDER": "jsfinder",
    "JS SECRETS": "jsfinder",
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
    "PREMIUM": "premium",
    "VIP": "premium",
    "BUY PREMIUM": "premium",
    "MY PLAN": "myplan",
    "MYPLAN": "myplan",
    "ADMIN PANEL": "admin_panel",
    "ADMIN": "admin_panel",
}

# Prompt texts for grid tools - 9 TOOLS CLEAN, NO COMMANDS, ULTRA ADVANCED
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
# NEW: Payments + Credits + Database
from modules.database import (
    get_user, get_credits, add_credits, set_credits, spend_credits,
    is_premium_user, is_premium, premium_expiry, grant_premium, revoke_premium,
    create_payment, get_payment, set_payment_status, set_payment_admin_msg,
    utr_exists, pending_payments_count, pending_payments, recent_payments,
    user_payments, all_user_ids, premium_users, recent_users, credits_stats, payment_stats,
    is_banned, set_ban, FREE_CREDITS
)
from modules.payments import PLANS, UPI_ID, UPI_NAME, get_upi_link, format_plans, format_plan_detail, format_myplan, format_credits_over

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ========== CREDITS CHECK - FAST ==========
def can_use_tool(uid: int) -> tuple:
    """Check if user can use tool - returns (can_use:bool, credits:int, user:dict)"""
    try:
        if config.is_admin(uid):
            u = get_user(uid)
            return True, u.get("credits", FREE_CREDITS), u
        if is_banned(uid):
            return False, 0, {}
        u = get_user(uid)
        if is_premium(u):
            return True, u.get("credits", FREE_CREDITS), u
        credits = int(u.get("credits", 0))
        if credits > 0:
            return True, credits, u
        else:
            return False, 0, u
    except Exception as e:
        print(f"can_use_tool error: {e}")
        return True, FREE_CREDITS, {}

def credits_line(uid: int) -> str:
    """Get credits line for footer"""
    try:
        if config.is_admin(uid):
            return "👑 <i>Admin - Unlimited</i>\n"
        u = get_user(uid)
        if is_premium(u):
            exp = premium_expiry(u)
            return f"👑 <i>Premium - {exp}</i>\n"
        credits = get_credits(uid)
        if credits <= 3 and credits > 0:
            return f"⚠️ <i>Sirf {credits} credits bache - /premium</i>\n"
        elif credits <= 0:
            return f"🔒 <i>Credits khatam - /premium</i>\n"
        else:
            return f"🎁 <i>{credits} credits bache</i>\n"
    except:
        return ""

# ========== FORCE JOIN - STRONG PROTECTION (No join = No bot) ==========
async def is_user_joined_channel(user_id: int, bot) -> bool:
    """Internal check - returns True if joined"""
    if not config.FORCE_CHANNEL:
        return True
    if config.is_admin(user_id):
        return True
    try:
        member = await bot.get_chat_member(chat_id=config.FORCE_CHANNEL, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except BadRequest as e:
        # Bot not admin in channel - log but allow to avoid total block, owner must make bot admin
        logger.warning(f"FORCE JOIN: Bot not admin or channel error: {e} | Make bot admin in {config.FORCE_CHANNEL_LINK}")
        # For strong protection, still return True here to not block everyone if misconfig, but owner should fix
        # Change to False if you want hard block even when bot not admin
        return True
    except Exception as e:
        logger.warning(f"FORCE JOIN error user {user_id}: {e}")
        return False

async def check_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Strong protection - Check if user joined, else block with join buttons"""
    if not config.FORCE_CHANNEL:
        return True
    
    user_id = update.effective_user.id
    if config.is_admin(user_id):
        return True

    joined = await is_user_joined_channel(user_id, context.bot)
    if joined:
        return True

    # NOT JOINED - Strong block
    kb = [
        [InlineKeyboardButton("📢 Join Channel @osint_xpert", url=config.FORCE_CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Verify - Joined", callback_data="check_joined")]
    ]
    try:
        # If called from message
        if update.message:
            await update.message.reply_text(
                f"🚫 <b>ACCESS DENIED - FORCE JOIN REQUIRED!</b>\n\n"
                f"👋 Hello <b>{update.effective_user.first_name}</b>!\n\n"
                f"⚠️ <b>Bot use karne ke liye aapko hamara channel join karna hoga!</b>\n\n"
                f"📢 <b>Channel:</b> {config.FORCE_CHANNEL_LINK}\n"
                f"🔒 Bina join kiye koi bhi tool kaam nahi karega!\n\n"
                f"👇 <b>Step 1:</b> Join Channel pe click karo\n"
                f"👇 <b>Step 2:</b> Verify pe click karo\n"
                f"✅ Uske baad /start se bot use karo",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(kb)
            )
        elif update.callback_query:
            await update.callback_query.answer("❌ Pehle channel join karo!", show_alert=True)
            await update.callback_query.message.reply_text(
                f"🚫 <b>Channel Join Karo!</b>\n\n📢 {config.FORCE_CHANNEL_LINK}",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(kb)
            )
    except Exception as e:
        logger.warning(f"Force join send failed: {e}")
    
    return False

async def check_joined_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        joined = await is_user_joined_channel(user_id, context.bot)
        if joined:
            # Verified! Now send welcome with grid
            await query.edit_message_text(
                f"✅ <b>VERIFIED SUCCESSFULLY!</b>\n\n"
                f"🎉 Aapne channel join kar liya!\n"
                f"🚀 Ab aap bot ke saare tools use kar sakte ho!\n\n"
                f"👇 /start pe click karo tools dekhne ke liye",
                parse_mode=ParseMode.HTML
            )
            # Auto trigger start
            try:
                # Create fake update for start
                await start(update, context)
            except:
                pass
        else:
            await query.answer("❌ Abhi bhi join nahi kiya! Pehle channel join karo, phir Verify dabao.", show_alert=True)
            # Keep message with buttons
            kb = [
                [InlineKeyboardButton("📢 Join Channel @osint_xpert", url=config.FORCE_CHANNEL_LINK)],
                [InlineKeyboardButton("✅ Verify - Joined", callback_data="check_joined")]
            ]
            try:
                await query.edit_message_text(
                    f"❌ <b>Abhi bhi join nahi kiya!</b>\n\n"
                    f"📢 Channel: {config.FORCE_CHANNEL_LINK}\n\n"
                    f"1️⃣ Join pe click karo\n"
                    f"2️⃣ Wapas aake Verify dabao",
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(kb)
                )
            except:
                pass
    except Exception as e:
        logger.warning(f"check_joined_callback error: {e}")
        await query.answer(f"Error: {str(e)[:100]}", show_alert=True)

# ========== START & HELP ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # STRONG FORCE JOIN CHECK - No join = No access at all
        if not await check_force_join(update, context):
            return

        user = update.effective_user
        
        # Try to get grid keyboard, fallback to None if fails
        try:
            reply_kb = kb_for(user.id)
        except Exception as e:
            print(f"kb_for failed: {e}")
            reply_kb = None
        
        # Format current time like screenshot: 14 October 2026 01:47 AM
        now = datetime.now()
        current_time_str = now.strftime("%d %B %Y\n%I:%M %p")
        
        # User details like screenshot
        username = f"@{user.username}" if user.username else "N/A"
        user_id = user.id
        display_name = user.first_name or "User"
        if user_id == 8607774564:
            name_display = "** V ᴇ ɴ ᴏ ᴍ **"
        else:
            name_display = f"** {display_name} **"
        
        txt = f"""
👋 Welcome {name_display}, apka swagat hai is bot mein! 😊

👤 User Details:
   ├ Username: {username}
   ├ User ID: {user_id}
   └ Name: {name_display}

🕐 Current Time:
   {current_time_str}

✅ <b>Verified: Channel Joined!</b>
💡 Neeche menu se tool chuno, ya /help bhejo.

📢 Update ke liye: @osint_xpert
👑 Owner: @Supermannn_x
"""

        # Try to send photo banner + caption + grid
        banner_path = os.path.join(os.path.dirname(__file__), "welcome_banner.jpg")
        if not os.path.exists(banner_path):
            banner_path = "welcome_banner.jpg"
        
        try:
            if os.path.exists(banner_path):
                with open(banner_path, 'rb') as photo:
                    if reply_kb:
                        await update.message.reply_photo(
                            photo=photo,
                            caption=txt,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_kb
                        )
                    else:
                        await update.message.reply_photo(
                            photo=photo,
                            caption=txt,
                            parse_mode=ParseMode.HTML
                        )
                # Inline buttons below welcome - channel + owner
                try:
                    kb = [
                        [InlineKeyboardButton("📢 Official Channel @osint_xpert", url=config.FORCE_CHANNEL_LINK)],
                        [InlineKeyboardButton("👑 Owner @Supermannn_x", url="https://t.me/Supermannn_x"), InlineKeyboardButton("📖 Help", callback_data="help_all")]
                    ]
                    await update.message.reply_text(
                        "👇 <b>Neeche menu se tool chuno - 8 Tools Ready!</b>\n\n"
                        "🔒 <b>Protection:</b> Channel joined ✅ | Ab sab tools kaam karenge!",
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(kb)
                    )
                except:
                    pass
            else:
                if reply_kb:
                    await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=reply_kb)
                else:
                    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
                
                # Inline buttons - joined users
                try:
                    kb = [
                        [InlineKeyboardButton("📢 Official Channel @osint_xpert", url=config.FORCE_CHANNEL_LINK)],
                        [InlineKeyboardButton("👑 Owner @Supermannn_x", url="https://t.me/Supermannn_x"), InlineKeyboardButton("📖 Help", callback_data="help_all")]
                    ]
                    await update.message.reply_text(
                        "👇 <b>Neeche menu se tool chuno - 8 Tools Ready!</b>\n\n"
                        "🔒 <b>Protection:</b> Channel joined ✅",
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(kb)
                    )
                except:
                    pass
        except Exception as e:
            print(f"Photo send failed: {e}, trying text only")
            try:
                if reply_kb:
                    await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=reply_kb)
                else:
                    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
            except Exception as e2:
                print(f"Text fallback also failed: {e2}")
                await update.message.reply_text(txt[:4000])
    
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
        print(f"GRID BUTTON PRESSED: '{text}' from user {update.effective_user.id}")
        # Clean emoji and get mode - robust for ALL emojis
        clean_text = text
        # Remove emoji prefix - comprehensive list
        all_emojis = ["📡 ", "📸 ", "📧 ", "🌐 ", "🖼️ ", "🔒 ", "📱 ", "🆔 ", "📝 ", "📊 ", "📜 ", "👑 ", "📢 ", "📚 ", "🔧 ", "💎 ", "🐙 ", "☁️ ", "🛠️ ", "⚒️ ", "🔨 ", "💳 ", "🎁 ", "👥 ", "📊 ", "💎 ", "🔥 ", "⭐ ", "🚀 "]
        for emoji in all_emojis:
            if clean_text.startswith(emoji):
                clean_text = clean_text[len(emoji):].strip()
                break
        # Fallback: strip any leading non-alphanumeric (emoji) characters - handles ALL emojis
        if clean_text == text:
            import re
            # Remove leading emoji/non-letter chars - more aggressive
            m = re.match(r'^[^\w]+(.*)', text, re.UNICODE)
            if m:
                possible = m.group(1).strip()
                if possible:
                    clean_text = possible
            # Also try removing first 2 chars if still same (for compound emojis like 🛠️)
            if clean_text == text and len(text) > 2:
                # Try stripping first 2-4 chars
                for i in range(1, 5):
                    if len(text) > i:
                        test = text[i:].strip()
                        if test and test[0].isalnum():
                            clean_text = test
                            break
        
        print(f"CLEANED: '{clean_text}' from '{text}'")
        
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

            if mode == "admin" or mode == "admin_panel":
                if not config.is_admin(update.effective_user.id):
                    await update.message.reply_text("❌ Owner only", parse_mode=ParseMode.HTML)
                    return
                await admin_cmd(update, context)
                return

            if mode == "premium":
                await premium_cmd(update, context)
                return

            if mode == "myplan":
                await myplan_cmd(update, context)
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
    uid = update.effective_user.id
    # Credits check
    can_use, creds, user = can_use_tool(uid)
    if not can_use:
        await update.message.reply_text(format_credits_over("Number Info"), parse_mode=ParseMode.HTML)
        return
    if not context.args:
        await update.message.reply_text(
            f"❌ <b>Use:</b> <code>/numinfo 9876543210</code>\n\n"
            f"📌 Example:\n"
            f"<code>/numinfo 9204507743</code>\n"
            f"<code>/number 9876543210</code>\n\n"
            f"{credits_line(uid)}",
            parse_mode=ParseMode.HTML
        )
        return

    number = context.args[0]
    status = await update.message.reply_text(
        f"🔍 <b>Number Info Searching...</b>\n\n"
        f"📱 Number: <code>{number}</code>\n"
        f"⏳ Please wait 5-15 seconds...\n"
        f"{credits_line(uid)}",
        parse_mode=ParseMode.HTML
    )

    try:
        result = await asyncio.to_thread(lookup_number, number)
        
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
            txt += f"🌐 <b>Circle:</b> {html.escape(str(circle)[:50])}\n\n"

        if owner.get("name"):
            txt += f"👤 <b>Name:</b> {html.escape(str(owner.get('name',''))[:100])}\n\n"

        if owner.get("father"):
            txt += f"👨‍👦 <b>Father Name:</b> {html.escape(str(owner.get('father',''))[:100])}\n\n"

        if owner.get("phone"):
            txt += f"📱 <b>Mobile:</b> <code>{owner.get('phone')}</code>\n\n"

        if owner.get("alt_phone"):
            txt += f"📱 <b>Alt Mobile:</b> <code>{owner.get('alt_phone')}</code>\n\n"

        if owner.get("address"):
            txt += f"🏠 <b>Address:</b>\n{html.escape(str(owner.get('address',''))[:300])}\n\n"

        if owner.get("aadhaar"):
            txt += f"🆔 <b>Aadhaar:</b> <code>{owner.get('aadhaar')}</code> (masked)\n\n"

        txt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📡 <b>Source:</b> utility-api-vu83

⚡ <b>Response:</b> {ms}ms
"""

        if rec > 1:
            txt += f"📑 <b>Records:</b> {rec} records found\n"

        # Spend credit after success
        left = spend_credits(uid, 1)
        if left <= 3:
            txt += f"\n{credits_line(uid)}"
        else:
            txt += f"\n🎁 <i>{left} credits bache</i>\n"

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
    uid = update.effective_user.id
    can_use, creds, user = can_use_tool(uid)
    if not can_use:
        await update.message.reply_text(format_credits_over("tg_number_cmd"), parse_mode=ParseMode.HTML)
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
        result = await asyncio.to_thread(lookup_tg, username)
        
        if not result.get("ok"):
            try:
                left = spend_credits(uid, 1)
                txt += f"\n{credits_line(uid)}"
            except:
                pass
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

        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(f"❌ Error: {str(e)[:200]}", parse_mode=ParseMode.HTML)

async def pak_number_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    can_use, creds, user = can_use_tool(uid)
    if not can_use:
        await update.message.reply_text(format_credits_over("pak_number_cmd"), parse_mode=ParseMode.HTML)
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/paknum 03001234567</code>", parse_mode=ParseMode.HTML)
        return

    num = context.args[0]
    status = await update.message.reply_text(f"🔍 Pak lookup for {num}...", parse_mode=ParseMode.HTML)

    try:
        result = await asyncio.to_thread(lookup_pak, num)
        if not result.get("ok"):
            try:
                left = spend_credits(uid, 1)
                txt += f"\n{credits_line(uid)}"
            except:
                pass
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

        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(f"❌ Error: {str(e)[:200]}", parse_mode=ParseMode.HTML)

# ========== TELEGRAM SCRAPER ==========
# ========== INSTAGRAM ==========
# ========== EMAIL ==========
# ========== IP & DOMAIN ==========
async def ip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    can_use, creds, user = can_use_tool(uid)
    if not can_use:
        await update.message.reply_text(format_credits_over("ip_cmd"), parse_mode=ParseMode.HTML)
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/ip 8.8.8.8</code> or <code>/ip google.com</code>", parse_mode=ParseMode.HTML)
        return

    target = context.args[0]
    status = await update.message.reply_text(f"🌐 IP lookup for {target}...", parse_mode=ParseMode.HTML)

    try:
        result = await asyncio.to_thread(ip_lookup, target)
        if not result.get("ok"):
            try:
                left = spend_credits(uid, 1)
                txt += f"\n{credits_line(uid)}"
            except:
                pass
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

        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(txt, parse_mode=ParseMode.HTML)

    except Exception as e:
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def domain_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    can_use, creds, user = can_use_tool(uid)
    if not can_use:
        await update.message.reply_text(format_credits_over("domain_cmd"), parse_mode=ParseMode.HTML)
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/domain google.com</code>", parse_mode=ParseMode.HTML)
        return

    target = context.args[0]
    status = await update.message.reply_text(f"🌐 Full recon for {target}...", parse_mode=ParseMode.HTML)

    try:
        result = await asyncio.to_thread(full_recon, target)
        if result.get("type") == "ip":
            ip_info = result.get("ip_info", {})
            try:
                left = spend_credits(uid, 1)
                txt += f"\n{credits_line(uid)}"
            except:
                pass
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

        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.exception(e)
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def dns_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    can_use, creds, user = can_use_tool(uid)
    if not can_use:
        await update.message.reply_text(format_credits_over("dns_cmd"), parse_mode=ParseMode.HTML)
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/dns google.com</code>", parse_mode=ParseMode.HTML)
        return

    target = context.args[0]
    status = await update.message.reply_text(f"🔍 DNS lookup for {target}...", parse_mode=ParseMode.HTML)

    try:
        result = await asyncio.to_thread(dns_lookup, target)
        txt = f"🌐 <b>DNS for {result.get('domain')}</b>\n\n"
        for k, v in result.get("records", {}).items():
            txt += f"<b>{k}:</b> {', '.join(v) if isinstance(v, list) else v}\n\n"
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def whois_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    can_use, creds, user = can_use_tool(uid)
    if not can_use:
        await update.message.reply_text(format_credits_over("whois_cmd"), parse_mode=ParseMode.HTML)
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/whois google.com</code>", parse_mode=ParseMode.HTML)
        return

    target = context.args[0]
    status = await update.message.reply_text(f"🔍 WHOIS for {target}...", parse_mode=ParseMode.HTML)

    try:
        result = await asyncio.to_thread(whois_lookup, target)
        if not result.get("ok"):
            try:
                left = spend_credits(uid, 1)
                txt += f"\n{credits_line(uid)}"
            except:
                pass
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

        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def ssl_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    can_use, creds, user = can_use_tool(uid)
    if not can_use:
        await update.message.reply_text(format_credits_over("ssl_cmd"), parse_mode=ParseMode.HTML)
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/ssl google.com</code>", parse_mode=ParseMode.HTML)
        return

    target = context.args[0]
    status = await update.message.reply_text(f"🔒 SSL check for {target}...", parse_mode=ParseMode.HTML)

    try:
        result = await asyncio.to_thread(ssl_check, target)
        if not result.get("ok"):
            try:
                left = spend_credits(uid, 1)
                txt += f"\n{credits_line(uid)}"
            except:
                pass
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

        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(txt, parse_mode=ParseMode.HTML)

    except Exception as e:
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

# ========== EXIF ==========
# ========== OCR ==========
# ========== WEBSITE EXTRACTOR ==========
async def website_extract_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    can_use, creds, user = can_use_tool(uid)
    if not can_use:
        await update.message.reply_text(format_credits_over("website_extract_cmd"), parse_mode=ParseMode.HTML)
        return
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/wextract https://example.com</code>", parse_mode=ParseMode.HTML)
        return

    url = context.args[0]
    status = await update.message.reply_text(f"🔍 Extracting from {url}...", parse_mode=ParseMode.HTML)

    try:
        result = await asyncio.to_thread(website_extractor, url)
        if not result.get("ok"):
            try:
                left = spend_credits(uid, 1)
                txt += f"\n{credits_line(uid)}"
            except:
                pass
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

        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
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
    uid = update.effective_user.id
    can_use, creds, user = can_use_tool(uid)
    if not can_use:
        await update.message.reply_text(format_credits_over("js_secret_cmd"), parse_mode=ParseMode.HTML)
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
        result = await asyncio.to_thread(js_secret_finder, url)
        txt = format_js_report(result)
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e:
        logger.exception(e)
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(f"❌ Error: {str(e)[:300]}", parse_mode=ParseMode.HTML)

# ========== GITHUB LEAK HUNTER - PRO ==========
async def github_leak_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    can_use, creds, user = can_use_tool(uid)
    if not can_use:
        await update.message.reply_text(format_credits_over("github_leak_cmd"), parse_mode=ParseMode.HTML)
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
        result = await asyncio.to_thread(github_leak_hunter, query)
        txt = format_github_report(result)
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e:
        logger.exception(e)
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(f"❌ Error: {str(e)[:300]}", parse_mode=ParseMode.HTML)

# ========== TERABOX EXTRACTOR - PRO ==========
async def terabox_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    can_use, creds, user = can_use_tool(uid)
    if not can_use:
        await update.message.reply_text(format_credits_over("terabox_cmd"), parse_mode=ParseMode.HTML)
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
        result = await asyncio.to_thread(extract_terabox, url)
        txt = format_terabox_report(result)
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e:
        logger.exception(e)
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(f"❌ Error: {str(e)[:500]}", parse_mode=ParseMode.HTML)

# ========== PING - FAST TEST ==========
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # No force join, no credits - instant reply to test bot alive
    await update.message.reply_text(f"🏓 Pong! Bot alive - {datetime.now().strftime('%I:%M:%S %p')}\n\n✅ Fast stable mode ON\n⚡ No delay\n\nGrid: /start", parse_mode=ParseMode.HTML)

# ========== PAYMENTS & PREMIUM ==========
async def premium_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    get_user(uid, update.effective_user.first_name or "", update.effective_user.username or "")
    txt = format_plans()
    kb = [
        [InlineKeyboardButton("💎 30D ₹49", callback_data="buy_30d"), InlineKeyboardButton("🔥 60D ₹89", callback_data="buy_60d")],
        [InlineKeyboardButton("⭐ 90D ₹120", callback_data="buy_90d"), InlineKeyboardButton("🚀 180D ₹199", callback_data="buy_180d")],
        [InlineKeyboardButton("👑 365D ₹299", callback_data="buy_365d")],
        [InlineKeyboardButton("📦 50C ₹29", callback_data="buy_c50"), InlineKeyboardButton("📦 100C ₹49", callback_data="buy_c100"), InlineKeyboardButton("📦 250C ₹99", callback_data="buy_c250")],
        [InlineKeyboardButton("📊 My Plan", callback_data="myplan"), InlineKeyboardButton("📢 Channel", url=config.FORCE_CHANNEL_LINK)]
    ]
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

async def myplan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    u = get_user(uid, update.effective_user.first_name or "", update.effective_user.username or "")
    creds = get_credits(uid)
    txt = format_myplan(u, creds)
    kb = [[InlineKeyboardButton("👑 Premium Plans", callback_data="premium")]]
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

async def buy_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if not context.args:
        await premium_cmd(update, context)
        return
    plan_key = context.args[0].lower()
    plan = PLANS.get(plan_key)
    if not plan:
        await update.message.reply_text(f"❌ Invalid plan <code>{plan_key}</code>\n\nValid: {', '.join(PLANS.keys())}\n\n/premium se dekho", parse_mode=ParseMode.HTML)
        return
    uid = update.effective_user.id
    get_user(uid, update.effective_user.first_name or "", update.effective_user.username or "")
    txt = format_plan_detail(plan_key)
    kb = [
        [InlineKeyboardButton(f"💳 Pay ₹{plan['amount']} via UPI", url=get_upi_link(plan['amount'], f"OSINT {plan['name']}"))],
        [InlineKeyboardButton("✅ Paid - Send Screenshot", callback_data=f"paid_{plan_key}")],
        [InlineKeyboardButton("📖 How to Pay?", callback_data="howtopay")]
    ]
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

async def pay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Use: <code>/pay plan_key UTR</code>\n\n"
            "Example: <code>/pay 30d 123456789012</code>\n\n"
            "1. /buy 30d se UPI ID lo\n"
            "2. Payment karo\n"
            "3. UTR (12 digit) + screenshot bhejo\n\n"
            "/premium se plans dekho",
            parse_mode=ParseMode.HTML
        )
        return
    plan_key = context.args[0].lower()
    utr = context.args[1].strip()
    plan = PLANS.get(plan_key)
    if not plan:
        await update.message.reply_text(f"❌ Invalid plan {plan_key}", parse_mode=ParseMode.HTML)
        return
    if len(utr) < 6:
        await update.message.reply_text("❌ UTR kam se kam 6 digit ka hona chahiye", parse_mode=ParseMode.HTML)
        return
    if utr_exists(utr):
        await update.message.reply_text("❌ Ye UTR pehle use ho chuka hai! Duplicate UTR not allowed.", parse_mode=ParseMode.HTML)
        return
    
    uid = update.effective_user.id
    pid = create_payment(uid, plan_key, plan['name'], plan['amount'], plan['days'], utr)
    if not pid:
        await update.message.reply_text("❌ Payment record create failed, try again", parse_mode=ParseMode.HTML)
        return
    
    # Ask for screenshot
    context.user_data[f"pending_pay_{uid}"] = pid
    await update.message.reply_text(
        f"✅ Payment record created! ID: <code>{pid}</code>\n\n"
        f"📦 Plan: {plan['name']}\n"
        f"💰 Amount: ₹{plan['amount']}\n"
        f"🔢 UTR: <code>{utr}</code>\n\n"
        f"📸 Ab payment ka <b>screenshot bhejo</b> (photo ke roop me)\n\n"
        f"⏳ Owner 5-10 min me verify karega\n"
        f"📢 Channel: @osint_xpert",
        parse_mode=ParseMode.HTML
    )
    # Notify admin
    try:
        admin_text = f"""
💳 <b>NEW PAYMENT - ID {pid}</b>

👤 User: <code>{uid}</code> - @{update.effective_user.username or 'N/A'} - {update.effective_user.first_name}
📦 Plan: {plan['name']} - ₹{plan['amount']} - {plan['days']}d
🔢 UTR: <code>{utr}</code>
⏰ Time: {datetime.now().strftime('%d %B %Y %I:%M %p')}

📸 Screenshot ka wait...

[Approve] /approve {pid}
[Reject] /reject {pid}
"""
        kb = [
            [InlineKeyboardButton(f"✅ Approve {pid}", callback_data=f"adm_approve_{pid}"), InlineKeyboardButton(f"❌ Reject {pid}", callback_data=f"adm_reject_{pid}")],
            [InlineKeyboardButton("📊 Payments", callback_data="adm_payments")]
        ]
        msg = await context.bot.send_message(chat_id=8607774564, text=admin_text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
        set_payment_admin_msg(pid, 8607774564, msg.message_id)
    except Exception as e:
        print(f"Admin notify failed: {e}")

async def handle_payment_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo as payment screenshot"""
    try:
        uid = update.effective_user.id
        pending_key = f"pending_pay_{uid}"
        pid = context.user_data.get(pending_key)
        if not pid:
            # Check if user has recent pending payment without screenshot
            ups = user_payments(uid, 5)
            for p in ups:
                if p['status'] == 'pending' and not p.get('shot_file_id'):
                    pid = p['id']
                    break
        if not pid:
            return False
        
        # Get photo file_id
        photo = update.message.photo[-1] if update.message.photo else None
        if not photo:
            return False
        
        file_id = photo.file_id
        unique_id = photo.file_unique_id
        
        # Update payment with screenshot
        try:
            from modules.database import db
            con = db()
            con.execute("UPDATE payments SET shot_file_id=?, shot_unique_id=? WHERE id=?", (file_id, unique_id, pid))
            con.commit()
            con.close()
        except Exception as e:
            print(f"Screenshot update failed: {e}")
        
        await update.message.reply_text(
            f"✅ Screenshot received for Payment ID <code>{pid}</code>!\n\n"
            f"⏳ Owner verification me 5-10 min lagega\n"
            f"✅ Approve hote hi premium chalu ho jayega\n\n"
            f"📊 /myplan se status check karo\n"
            f"📢 @osint_xpert",
            parse_mode=ParseMode.HTML
        )
        
        # Notify admin with photo
        try:
            pay = get_payment(pid)
            admin_text = f"""
💳 <b>PAYMENT SCREENSHOT - ID {pid}</b>

👤 User: <code>{pay.get('user_id')}</code>
📦 Plan: {pay.get('plan_name')} - ₹{pay.get('amount')}
🔢 UTR: <code>{pay.get('utr_ref')}</code>
📸 Screenshot attached!

✅ Approve: /approve {pid}
❌ Reject: /reject {pid}
"""
            kb = [
                [InlineKeyboardButton(f"✅ Approve {pid}", callback_data=f"adm_approve_{pid}"), InlineKeyboardButton(f"❌ Reject {pid}", callback_data=f"adm_reject_{pid}")],
            ]
            await context.bot.send_photo(chat_id=8607774564, photo=file_id, caption=admin_text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
        except Exception as e:
            print(f"Admin screenshot notify failed: {e}")
        
        # Clear pending
        try:
            del context.user_data[pending_key]
        except:
            pass
        
        return True
    except Exception as e:
        print(f"handle_payment_screenshot error: {e}")
        return False

# ========== ADMIN PANEL - FULL CONTROLS ==========
async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not config.is_admin(uid):
        await update.message.reply_text("❌ Owner only", parse_mode=ParseMode.HTML)
        return
    
    stats = credits_stats()
    p_stats = payment_stats()
    pend_count = pending_payments_count()
    prem_count = len(premium_users())
    
    txt = f"""
╔══════════════════════════════════════╗
║  🛠️ <b>ADMIN PANEL - FULL CONTROLS</b>  ║
╚══════════════════════════════════════╝

📊 <b>Stats:</b>
👥 Total Users: {stats.get('total_users',0)}
💎 Premium Users: {prem_count}
🎁 Total Credits: {stats.get('total_credits',0)}
🔢 Total Uses: {stats.get('total_uses',0)}

💳 <b>Payments:</b>
⏳ Pending: {pend_count}
✅ Approved: {p_stats.get('approved',{}).get('count',0) if isinstance(p_stats.get('approved'), dict) else 0}
❌ Rejected: {p_stats.get('rejected',{}).get('count',0) if isinstance(p_stats.get('rejected'), dict) else 0}

💰 <b>UPI:</b> <code>{UPI_ID}</code>
👤 <b>Name:</b> {UPI_NAME}
🎁 <b>Free Credits:</b> {FREE_CREDITS}

<b>━━━━━━━━ Commands ━━━━━━━━</b>
/approve &lt;id&gt; - Approve payment
/reject &lt;id&gt; - Reject payment
/addcredit &lt;user_id&gt; &lt;amount&gt; - Add credits
/setcredit &lt;user_id&gt; &lt;amount&gt; - Set credits
/grant &lt;user_id&gt; &lt;days&gt; - Grant premium
/revoke &lt;user_id&gt; - Revoke premium
/ban &lt;user_id&gt; - Ban user
/unban &lt;user_id&gt; - Unban user
/stats - Detailed stats
/payments - Pending payments
/users - Recent users
/vips - Premium users list
/broadcast &lt;msg&gt; - Broadcast to all

<b>━━━━━━━━ Quick Actions ━━━━━━━━</b>
"""
    kb = [
        [InlineKeyboardButton(f"💳 Pending ({pend_count})", callback_data="adm_payments"), InlineKeyboardButton("👑 Vips", callback_data="adm_vips")],
        [InlineKeyboardButton("📊 Stats", callback_data="adm_stats"), InlineKeyboardButton("👥 Users", callback_data="adm_users")],
        [InlineKeyboardButton("💰 Add Credits", callback_data="adm_cred"), InlineKeyboardButton("👑 Grant Premium", callback_data="adm_grant")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast"), InlineKeyboardButton("🔧 Settings", callback_data="adm_settings")],
    ]
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

async def approve_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Use: /approve &lt;payment_id&gt;", parse_mode=ParseMode.HTML)
        return
    try:
        pid = int(context.args[0])
    except:
        await update.message.reply_text("Invalid ID", parse_mode=ParseMode.HTML)
        return
    
    pay = get_payment(pid)
    if not pay:
        await update.message.reply_text(f"❌ Payment {pid} not found", parse_mode=ParseMode.HTML)
        return
    if pay['status'] != 'pending':
        await update.message.reply_text(f"❌ Payment {pid} already {pay['status']}", parse_mode=ParseMode.HTML)
        return
    
    uid = pay['user_id']
    plan_key = pay.get('plan_key','')
    plan = PLANS.get(plan_key, {})
    days = plan.get('days', pay.get('plan_days',0))
    credits = plan.get('credits',0)
    
    # Grant
    if days > 0:
        new_until = grant_premium(uid, days, update.effective_user.id, plan_key, f"Payment {pid} approved")
        await update.message.reply_text(f"✅ Payment {pid} approved!\n\nUser: <code>{uid}</code>\nPlan: {pay['plan_name']}\nPremium until: {new_until}\nDays: {days}", parse_mode=ParseMode.HTML)
        # Notify user
        try:
            await context.bot.send_message(chat_id=uid, text=f"✅ <b>Payment Approved!</b>\n\n📦 Plan: {pay['plan_name']}\n⏰ Premium until: {new_until}\n\n🚀 Ab unlimited use karo!\n\n/myplan se dekho\n📢 @osint_xpert", parse_mode=ParseMode.HTML)
        except:
            pass
    elif credits > 0:
        new_cred = add_credits(uid, credits)
        await update.message.reply_text(f"✅ Payment {pid} approved!\n\nUser: <code>{uid}</code>\nCredits added: {credits}\nNew total: {new_cred}", parse_mode=ParseMode.HTML)
        try:
            await context.bot.send_message(chat_id=uid, text=f"✅ <b>Credits Added!</b>\n\n📦 {credits} credits added!\n🎁 Total: {new_cred}\n\n/myplan se dekho", parse_mode=ParseMode.HTML)
        except:
            pass
    
    set_payment_status(pid, "approved", update.effective_user.id, "Approved by admin")

async def reject_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Use: /reject &lt;payment_id&gt; [reason]", parse_mode=ParseMode.HTML)
        return
    try:
        pid = int(context.args[0])
    except:
        await update.message.reply_text("Invalid ID", parse_mode=ParseMode.HTML)
        return
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Rejected by admin"
    pay = get_payment(pid)
    if not pay:
        await update.message.reply_text(f"❌ Payment {pid} not found", parse_mode=ParseMode.HTML)
        return
    set_payment_status(pid, "rejected", update.effective_user.id, reason)
    await update.message.reply_text(f"❌ Payment {pid} rejected - {reason}", parse_mode=ParseMode.HTML)
    try:
        await context.bot.send_message(chat_id=pay['user_id'], text=f"❌ <b>Payment Rejected</b>\n\nID: {pid}\nReason: {reason}\n\nContact @Supermannn_x\n💳 UPI: {UPI_ID}", parse_mode=ParseMode.HTML)
    except:
        pass

async def addcredit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Use: /addcredit &lt;user_id&gt; &lt;amount&gt;\nExample: /addcredit 123456 50", parse_mode=ParseMode.HTML)
        return
    try:
        uid = int(context.args[0])
        amt = int(context.args[1])
    except:
        await update.message.reply_text("Invalid args", parse_mode=ParseMode.HTML)
        return
    new_total = add_credits(uid, amt)
    await update.message.reply_text(f"✅ Added {amt} credits to <code>{uid}</code>\nNew total: {new_total}", parse_mode=ParseMode.HTML)
    try:
        await context.bot.send_message(chat_id=uid, text=f"🎁 <b>{amt} credits added!</b>\n\nTotal: {new_total}\n\n/myplan", parse_mode=ParseMode.HTML)
    except:
        pass

async def setcredit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Use: /setcredit &lt;user_id&gt; &lt;amount&gt;", parse_mode=ParseMode.HTML)
        return
    try:
        uid = int(context.args[0])
        amt = int(context.args[1])
    except:
        await update.message.reply_text("Invalid", parse_mode=ParseMode.HTML)
        return
    set_credits(uid, amt)
    await update.message.reply_text(f"✅ Set credits of <code>{uid}</code> to {amt}", parse_mode=ParseMode.HTML)

async def grant_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Use: /grant &lt;user_id&gt; &lt;days&gt;\nExample: /grant 123456 30\nFor lifetime: /grant 123456 3650", parse_mode=ParseMode.HTML)
        return
    try:
        uid = int(context.args[0])
        days = int(context.args[1])
    except:
        await update.message.reply_text("Invalid", parse_mode=ParseMode.HTML)
        return
    new_until = grant_premium(uid, days, update.effective_user.id, "admin_grant", f"Granted by admin")
    await update.message.reply_text(f"✅ Granted {days} days premium to <code>{uid}</code>\nUntil: {new_until}", parse_mode=ParseMode.HTML)
    try:
        await context.bot.send_message(chat_id=uid, text=f"👑 <b>Premium Granted!</b>\n\n{days} days premium!\nUntil: {new_until}\n\n/myplan", parse_mode=ParseMode.HTML)
    except:
        pass

async def revoke_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Use: /revoke &lt;user_id&gt;", parse_mode=ParseMode.HTML)
        return
    try:
        uid = int(context.args[0])
    except:
        await update.message.reply_text("Invalid", parse_mode=ParseMode.HTML)
        return
    revoke_premium(uid, update.effective_user.id, "Revoked by admin")
    await update.message.reply_text(f"🗑️ Revoked premium of <code>{uid}</code>", parse_mode=ParseMode.HTML)

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Use: /ban &lt;user_id&gt;", parse_mode=ParseMode.HTML)
        return
    try:
        uid = int(context.args[0])
    except:
        await update.message.reply_text("Invalid", parse_mode=ParseMode.HTML)
        return
    set_ban(uid, 1)
    await update.message.reply_text(f"🚫 Banned <code>{uid}</code>", parse_mode=ParseMode.HTML)

async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Use: /unban &lt;user_id&gt;", parse_mode=ParseMode.HTML)
        return
    try:
        uid = int(context.args[0])
    except:
        await update.message.reply_text("Invalid", parse_mode=ParseMode.HTML)
        return
    set_ban(uid, 0)
    await update.message.reply_text(f"✅ Unbanned <code>{uid}</code>", parse_mode=ParseMode.HTML)

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    s = credits_stats()
    ps = payment_stats()
    pend = pending_payments_count()
    prem = premium_users()
    txt = f"""
📊 <b>DETAILED STATS</b>

👥 Users: {s.get('total_users',0)}
🎁 Total Credits: {s.get('total_credits',0)}
🔢 Total Uses: {s.get('total_uses',0)}
👑 Premium: {len(prem)}

💳 Payments:
"""
    for status, data in ps.items():
        if isinstance(data, dict):
            txt += f"  {status}: {data.get('count',0)} - ₹{data.get('amount',0)}\n"
    txt += f"\n⏳ Pending: {pend}\n"
    txt += f"💰 UPI: {UPI_ID}\n"
    txt += f"🎁 Free: {FREE_CREDITS}\n"
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

async def payments_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    pays = pending_payments(20)
    if not pays:
        await update.message.reply_text("✅ No pending payments", parse_mode=ParseMode.HTML)
        return
    txt = f"💳 <b>PENDING PAYMENTS ({len(pays)})</b>\n\n"
    for p in pays[:10]:
        txt += f"ID {p['id']} - User <code>{p['user_id']}</code> - {p['plan_name']} ₹{p['amount']} - UTR <code>{p['utr_ref']}</code> - /approve {p['id']}\n\n"
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    users = recent_users(20)
    txt = f"👥 <b>RECENT USERS ({len(users)})</b>\n\n"
    for u in users[:15]:
        prem = "👑" if is_premium(u) else "🆓"
        txt += f"{prem} <code>{u['user_id']}</code> - {u.get('name','')} - {u.get('credits',0)}c - {u.get('total_uses',0)} uses\n"
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

async def vips_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    vips = premium_users()
    txt = f"👑 <b>PREMIUM USERS ({len(vips)})</b>\n\n"
    for u in vips[:20]:
        txt += f"<code>{u['user_id']}</code> - {u.get('name','')} - {premium_expiry(u)}\n"
    if not vips:
        txt += "No premium users"
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Use: /broadcast &lt;message&gt;", parse_mode=ParseMode.HTML)
        return
    msg = " ".join(context.args)
    uids = all_user_ids()
    await update.message.reply_text(f"📢 Broadcasting to {len(uids)} users...", parse_mode=ParseMode.HTML)
    sent = 0
    for uid in uids:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 <b>Announcement</b>\n\n{msg}\n\n📢 @osint_xpert", parse_mode=ParseMode.HTML)
            sent += 1
        except:
            pass
    await update.message.reply_text(f"✅ Broadcast sent to {sent}/{len(uids)}", parse_mode=ParseMode.HTML)

# ========== CALLBACKS ==========
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # Force join check for callbacks too
    if not await is_user_joined_channel(query.from_user.id, context.bot):
        if not config.is_admin(query.from_user.id):
            kb = [[InlineKeyboardButton("📢 Join Channel", url=config.FORCE_CHANNEL_LINK)], [InlineKeyboardButton("✅ Verify", callback_data="check_joined")]]
            await query.message.reply_text(f"🚫 Join channel first: {config.FORCE_CHANNEL_LINK}", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
            return
    
    if data == "help_all":
        await help_cmd(update, context)
    elif data == "tools":
        await start(update, context)
    elif data == "check_joined":
        await check_joined_callback(update, context)
    elif data == "premium":
        # Show premium
        txt = format_plans()
        kb = [
            [InlineKeyboardButton("💎 30D ₹49", callback_data="buy_30d"), InlineKeyboardButton("🔥 60D ₹89", callback_data="buy_60d")],
            [InlineKeyboardButton("⭐ 90D ₹120", callback_data="buy_90d"), InlineKeyboardButton("🚀 180D ₹199", callback_data="buy_180d")],
            [InlineKeyboardButton("👑 365D ₹299", callback_data="buy_365d")],
            [InlineKeyboardButton("📊 My Plan", callback_data="myplan")]
        ]
        await query.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
    elif data == "myplan":
        uid = query.from_user.id
        u = get_user(uid)
        creds = get_credits(uid)
        txt = format_myplan(u, creds)
        await query.message.reply_text(txt, parse_mode=ParseMode.HTML)
    elif data.startswith("buy_"):
        plan_key = data.replace("buy_","")
        plan = PLANS.get(plan_key)
        if plan:
            try:
                txt = format_plan_detail(plan_key)
                kb = [
                    [InlineKeyboardButton(f"💳 Pay ₹{plan['amount']} via UPI", url=get_upi_link(plan['amount'], f"OSINT {plan['name']}"))],
                    [InlineKeyboardButton("✅ Paid - Send Screenshot", callback_data=f"paid_{plan_key}")],
                    [InlineKeyboardButton("📖 How to Pay?", callback_data="howtopay")]
                ]
                await query.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
            except Exception as e:
                print(f"Buy callback HTML error {plan_key}: {e}")
                try:
                    # Fallback without HTML
                    plain = f"Plan: {plan['name']}\nAmount: ₹{plan['amount']}\nDuration: {plan['days']} days\n\nUPI: {UPI_ID}\n\nSteps:\n1. Pay ₹{plan['amount']} to {UPI_ID}\n2. Send screenshot + UTR\n3. /pay {plan_key} UTR"
                    await query.message.reply_text(plain, reply_markup=InlineKeyboardMarkup(kb))
                except Exception as e2:
                    print(f"Fallback also failed: {e2}")
                    await query.message.reply_text(f"Plan {plan_key} - ₹{plan['amount']} - UPI {UPI_ID} - /pay {plan_key} UTR", parse_mode=ParseMode.HTML)
        else:
            await query.message.reply_text(f"❌ Invalid plan {plan_key}", parse_mode=ParseMode.HTML)
    elif data.startswith("paid_"):
        plan_key = data.replace("paid_","")
        try:
            await query.message.reply_text(f"✅ Aapne {plan_key} ke liye pay kiya?\n\n1️⃣ UTR bhejo: /pay {plan_key} YOUR_UTR\n2️⃣ Phir screenshot bhejo\n\nExample: /pay {plan_key} 123456789012", parse_mode=ParseMode.HTML)
        except:
            await query.message.reply_text(f"Aapne {plan_key} ke liye pay kiya? UTR bhejo: /pay {plan_key} YOUR_UTR + screenshot", parse_mode=ParseMode.HTML)
    elif data == "howtopay":
        await query.message.reply_text(
            f"📖 <b>How to Pay via UPI</b>\n\n"
            f"1️⃣ UPI ID copy karo: <code>{UPI_ID}</code>\n"
            f"2️⃣ PhonePe/GPay/Paytm kholo\n"
            f"3️⃣ UPI ID pe payment karo\n"
            f"4️⃣ Screenshot lo + UTR note karo\n"
            f"5️⃣ /pay plan_key UTR bhejo\n"
            f"6️⃣ Screenshot bhejo\n\n"
            f"⏳ 5-10 min me premium!\n\n"
            f"💳 UPI: <code>{UPI_ID}</code>",
            parse_mode=ParseMode.HTML
        )
    elif data.startswith("adm_approve_"):
        if not config.is_admin(query.from_user.id):
            return
        pid = int(data.replace("adm_approve_",""))
        pay = get_payment(pid)
        if not pay:
            await query.answer("Payment not found", show_alert=True)
            return
        uid = pay['user_id']
        plan_key = pay.get('plan_key','')
        plan = PLANS.get(plan_key, {})
        days = plan.get('days', pay.get('plan_days',0))
        credits = plan.get('credits',0)
        if days > 0:
            new_until = grant_premium(uid, days, query.from_user.id, plan_key, f"Approved via button {pid}")
            set_payment_status(pid, "approved", query.from_user.id, "Approved via admin panel")
            await query.edit_message_text(f"✅ Approved Payment {pid}\nUser {uid}\nPremium until {new_until}", parse_mode=ParseMode.HTML)
            try:
                await context.bot.send_message(chat_id=uid, text=f"✅ <b>Payment Approved!</b>\n\nPlan: {pay['plan_name']}\nPremium until: {new_until}\n\n/myplan", parse_mode=ParseMode.HTML)
            except:
                pass
        elif credits > 0:
            new_cred = add_credits(uid, credits)
            set_payment_status(pid, "approved", query.from_user.id, "Approved")
            await query.edit_message_text(f"✅ Approved {pid} - {credits} credits to {uid} - Total {new_cred}", parse_mode=ParseMode.HTML)
            try:
                await context.bot.send_message(chat_id=uid, text=f"✅ {credits} credits added! Total {new_cred}", parse_mode=ParseMode.HTML)
            except:
                pass
    elif data.startswith("adm_reject_"):
        if not config.is_admin(query.from_user.id):
            return
        pid = int(data.replace("adm_reject_",""))
        set_payment_status(pid, "rejected", query.from_user.id, "Rejected via button")
        await query.edit_message_text(f"❌ Rejected Payment {pid}", parse_mode=ParseMode.HTML)
        pay = get_payment(pid)
        if pay:
            try:
                await context.bot.send_message(chat_id=pay['user_id'], text=f"❌ Payment {pid} rejected. Contact @Supermannn_x", parse_mode=ParseMode.HTML)
            except:
                pass
    elif data == "adm_payments":
        if not config.is_admin(query.from_user.id):
            return
        pays = pending_payments(10)
        if not pays:
            await query.message.reply_text("No pending payments", parse_mode=ParseMode.HTML)
            return
        txt = "💳 Pending Payments:\n\n"
        for p in pays:
            txt += f"ID {p['id']} - {p['user_id']} - {p['plan_name']} ₹{p['amount']} UTR {p['utr_ref']}\n"
        await query.message.reply_text(txt, parse_mode=ParseMode.HTML)
    elif data == "adm_vips":
        if not config.is_admin(query.from_user.id):
            return
        vips = premium_users()
        txt = f"👑 Premium Users ({len(vips)}):\n\n"
        for u in vips[:15]:
            txt += f"{u['user_id']} - {premium_expiry(u)}\n"
        await query.message.reply_text(txt, parse_mode=ParseMode.HTML)
    elif data == "adm_stats":
        if not config.is_admin(query.from_user.id):
            return
        s = credits_stats()
        txt = f"📊 Stats:\nUsers: {s['total_users']}\nCredits: {s['total_credits']}\nUses: {s['total_uses']}\nPending: {pending_payments_count()}"
        await query.message.reply_text(txt, parse_mode=ParseMode.HTML)
    elif data == "adm_users":
        if not config.is_admin(query.from_user.id):
            return
        users = recent_users(10)
        txt = "Recent Users:\n"
        for u in users:
            txt += f"{u['user_id']} - {u.get('name','')} - {u.get('credits',0)}c\n"
        await query.message.reply_text(txt, parse_mode=ParseMode.HTML)
    elif data == "adm_cred":
        await query.message.reply_text("💳 Credits do: /addcredit user_id amount\nExample: /addcredit 123456 50", parse_mode=ParseMode.HTML)
    elif data == "adm_grant":
        await query.message.reply_text("👑 Grant: /grant user_id days\nExample: /grant 123456 30", parse_mode=ParseMode.HTML)
    elif data == "adm_broadcast":
        await query.message.reply_text("📢 Broadcast: /broadcast your message", parse_mode=ParseMode.HTML)
    elif data == "adm_settings":
        await query.message.reply_text(f"🔧 Settings:\nUPI: {UPI_ID}\nName: {UPI_NAME}\nFree Credits: {FREE_CREDITS}\n\nSet in Render env:\nUPI_ID, UPI_NAME, FREE_CREDITS", parse_mode=ParseMode.HTML)

async def main_async():
    global app, loop
    loop = asyncio.get_running_loop()
    print("Building 8 TOOLS FAST STABLE app...")
    
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

    # TeraBox Extractor
    app.add_handler(CommandHandler("terabox", terabox_cmd))
    app.add_handler(CommandHandler("tb", terabox_cmd))
    app.add_handler(CommandHandler("teraboxdl", terabox_cmd))

    # ========== PAYMENTS & PREMIUM - NEW ==========
    app.add_handler(CommandHandler(["premium", "vip", "plans"], premium_cmd))
    app.add_handler(CommandHandler(["myplan", "mycredits", "credits", "plan"], myplan_cmd))
    app.add_handler(CommandHandler("buy", buy_cmd))
    app.add_handler(CommandHandler("pay", pay_cmd))
    app.add_handler(CommandHandler(["ping", "alive", "test"], ping_cmd))

    # ========== ADMIN FULL CONTROLS ==========
    app.add_handler(CommandHandler(["admin", "adminpanel", "panel"], admin_cmd))
    app.add_handler(CommandHandler("approve", approve_cmd))
    app.add_handler(CommandHandler("reject", reject_cmd))
    app.add_handler(CommandHandler("addcredit", addcredit_cmd))
    app.add_handler(CommandHandler("setcredit", setcredit_cmd))
    app.add_handler(CommandHandler("grant", grant_cmd))
    app.add_handler(CommandHandler("revoke", revoke_cmd))
    app.add_handler(CommandHandler("ban", ban_cmd))
    app.add_handler(CommandHandler("unban", unban_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("payments", payments_cmd))
    app.add_handler(CommandHandler("users", users_cmd))
    app.add_handler(CommandHandler("vips", vips_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))

    # Grid handler - must be before document handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_grid_button))

    # Photo handler for payment screenshots - BEFORE pdf handler
    app.add_handler(MessageHandler(filters.PHOTO, handle_payment_screenshot))

    # Document handlers - PDF Renamer (owner only)
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf_renamer))

    print("Initializing app...")
    await app.initialize()
    await app.start()

    print("Setting webhook...")
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        await app.bot.set_webhook(url=WEBHOOK_URL, allowed_updates=["message","callback_query","my_chat_member"])
        print(f"Webhook set to {WEBHOOK_URL}")
        import requests
        # Fast stable + payments live notification
        try:
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', 
                         data={'chat_id': '8607774564', 
                               'text': f'✅ 8 TOOLS + PAYMENTS + CREDITS LIVE!\n\n💰 UPI: {UPI_ID}\n🎁 Free: {FREE_CREDITS} credits\n👑 Premium: 30d ₹49 - 365d ₹299\n🛠️ Admin: Full controls\n⚡ Fast: No delay fix\n\nGrid: Number, TG, IP, Website, JS, GitHub, TeraBox, PDF\nPayments: /premium /myplan /buy\nAdmin: /admin'}, timeout=5)
        except:
            pass
    except Exception as e:
        print(f"Webhook set error: {e}")
        traceback.print_exc()

    print("8 TOOLS + PAYMENTS + CREDITS + ADMIN FAST STABLE WEBHOOK READY!")
    while True:
        await asyncio.sleep(60)
        print(f"8 tools + payments alive - Users: {len(all_user_ids())} - Premium: {len(premium_users())} - Pending: {pending_payments_count()}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
