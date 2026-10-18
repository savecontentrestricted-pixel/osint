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

WAIT2 = ("⏳🔍 <b>Please wait a few seconds…</b> ⚡\n"
         "🚀 <i>Aapka result aa raha hai…</i>")
NF2 = "❌ <b>Data not found in any database.</b>"
BOT_VERSION = ("v2.5.5 — bot-1 jaisa SAME credit system: FREE_CREDITS=10 + TG_CREDITS=3 (alag TG pool, env-control, redeploy par sab reset) | v2.5.4b — USER ORDER 18 Oct: simple wait note (user ka data echo NAHI), fail par sirf Data-not-found line, TG card sirf Number/TG-ID/Username/Country, t.me-public fallback PERMANENT BAND (sirf apna hub) | v2.5.3 — 4 tools PERMANENT DELETE (JS SECRET FINDER, TERABOX, GITHUB LEAK, UPI INFO — user order 18 Oct) | v2.5.2 — tg cache namespace bump (number wapas) | v2.5.1 — 🆩 TG NUMBER FIX: provider AB PAID (403 'CHALO AB BUY KRO') — ab t.me PUBLIC profile fallback (naam + link, ~0.5s) + honest note; FAIL par credit nahi katta (pehle kat jata tha — bug) + asli error dikhta hai | "
    "v2.4 — ⚡ SPEED FIX (asli wajah mili): PTB ke default settings khatarnak the — "
    "connection_pool_size=1 (Telegram ke liye sirf EK connection), read_timeout=5s, pool_timeout=1s, "
    "aur concurrent_updates OFF (saare updates ek-ek). Isse messages CHUP-CHAAP fail hote the "
    "(silent timeout) — user ko lagta tha bot slow hai ya jawab nahi aata. Ab bot 1 jaisa: "
    "pool=32, read_timeout=60s, write=120s, 8 updates parallel (+50% throughput). "
    "Saath me: har tool ka TIMING log Render me turant dikhega (flush) aur fail hone par asli "
    "error dikhega (pehle timeout par bhi 'No records found' likha aata tha) | "
    "v2.3 — 🔒 WEBHOOK SECRET (security fix): repo public hai, isliye ab /webhook par sirf "
    "Telegram ke asli updates process hote hain (secret header ke bina 403). Pehle koi bhi fake admin "
    "command bhej sakta tha. | "
    "v2.2 — ⚡ FEEL-FAST (utility-duniya-bot jaisa instant feel): number bhejte hi TURANT "
    "(1 sec) hint dikhta hai — number valid, operator + circle approx (100% offline, 0 ms) — "
    "phir wahi message final card ban jata hai; galat number par API call hi nahi hoti (instant reply); "
    "wait time ab honest (5-10 sec) + 'dobara bhejo to INSTANT' note; har tool ka [TIMING] log "
    "(asli speed /health ke bajaye logs me proof) | "
    "v2.1 — ⚡ FAST-2 (poore bot me 2-layer cache: memory + DB): ab TG number, Pak number, "
    "IP/DNS/WHOIS/SSL recon, website extractor, JS secret finder, GitHub leak hunter aur TeraBox — "
    "SAB me cache hai. Wahi query dobara = INSTANT (0 ms), pehli call bhi warm hub se. "
    "TG/Pak lookup ab pooled connection + 25s timeout (pehle 40s) | "
    "v2.0 — 🚀 v127.7 PARITY (utility-duniya-bot jaisa fast+stable+premium): "
    "premium ke saare plan buttons FIX (upi:// url button Telegram reject karta tha -> poora message fail), "
    "persistent lookup cache (num/family/upi/tg/pak — ek baar dhoondha = 30 din INSTANT, restart ke baad bhi zinda), "
    "DB VAULT (deploy par users/premium/pending payments kabhi wipe nahi), rich /health, "
    "crash-shield + watchdog (RAM/hang auto-restart), keepalive public-URL 5 min + hub warm, "
    "hardcoded secrets hataye, Dockerfile")
# v2.0 SECURITY: token sirf Render env se (pehle public repo me hardcoded tha!)
BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
PORT = int(os.getenv('PORT','10000'))
BOT_SELF_URL = (os.getenv('BOT_SELF_URL') or 'https://osint-hunter-hub-bot.onrender.com').rstrip('/')
# v2.3 SECURITY: webhook secret — sirf Telegram ke asli updates process honge.
# (repo public hai aur ADMIN_ID public — warna koi fake update bhej kar admin
#  commands chala sakta tha. Secret Telegram header me aata hai.)
WEBHOOK_SECRET = (os.getenv('WEBHOOK_SECRET') or '').strip()
WEBHOOK_URL = (os.getenv('WEBHOOK_URL') or f"{BOT_SELF_URL}/webhook")

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
            if self.path in ['/ping', '/ping/']:
                self.wfile.write(b'OK')                      # ultra fast - pinger/cron ke liye
            elif self.path in ['/health', '/healthz']:
                self.wfile.write(health_html().encode('utf-8', 'ignore'))
            elif self.path == '/webhook':
                self.wfile.write(b'Webhook endpoint - POST only')
            else:
                html = b"<html><body><h1>OSINT Hunter Hub - 11 TOOLS FAST STABLE LIVE</h1><p>Webhook: /webhook | Health: /health | Ping: /ping</p></body></html>"
                self.wfile.write(html)
        except:
            pass
    
    def do_POST(self):
        try:
            if self.path == '/webhook':
                # v2.3 SECURITY: Telegram ka secret header check (403 = chup-chaap reject)
                if WEBHOOK_SECRET and self.headers.get('X-Telegram-Bot-Api-Secret-Token') != WEBHOOK_SECRET:
                    self.send_response(403)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'forbidden')
                    return
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                try:
                    data = json.loads(body)
                    # Fast ack first - critical for no delay
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'OK')
                    # Then process async
                    print(f"WEBHOOK POST update_id {data.get('update_id')} - Fast ACK sent", flush=True)
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
    uid_tag = data.get('update_id')
    try:
        from telegram import Update
        global app
        with _INFLIGHT_LOCK:
            _INFLIGHT[uid_tag] = time.time()
        if app:
            update = Update.de_json(data, app.bot)
            await app.process_update(update)
    except Exception as e:
        CRASH["caught"] += 1
        print(f"handle_update error: {e}")
        traceback.print_exc()
    finally:
        with _INFLIGHT_LOCK:
            _INFLIGHT.pop(uid_tag, None)

def keepalive():
    try:
        print(f"WEBHOOK server on 0.0.0.0:{PORT} -> {WEBHOOK_URL} - FAST STABLE MODE")
        HTTPServer(('0.0.0.0', PORT), WebhookHandler).serve_forever()
    except Exception as e:
        print(f"Keepalive error: {e}")
        traceback.print_exc()

threading.Thread(target=keepalive, daemon=False).start()

# v2.0 KEEPALIVE: PUBLIC url ping (localhost ping Render ke spin-down ko nahi rokta!)
# + API hub bhi warm rakho (warna pehli tool call 12 sec leti hai)
def self_ping_loop():
    time.sleep(25)  # pehla ping 25s -> cold start ki jagah turant warm
    print(f"Keepalive pinger ON -> {BOT_SELF_URL}/ping + API hub (har 5 min)")
    while True:
        try:
            import requests
            requests.get(f"{BOT_SELF_URL}/ping", timeout=10)
        except Exception as e:
            print(f"Keepalive fail: {e}")
        try:
            import requests as _rq
            _rq.get("https://utility-api-vu83.onrender.com/health", timeout=10)
        except Exception:
            pass
        time.sleep(300)  # 5 min (pehle 10 min tha)

threading.Thread(target=self_ping_loop, daemon=True).start()

# Removed spam starting message - only notify after full init in main_async

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from telegram.constants import ParseMode
from telegram.error import BadRequest

# ========== GRID MENU - 6 TOOLS + PREMIUM + ADMIN (v2.5.3: 4 tools DELETE) ==========
KB_BTNS = [
    ["📱 NUMBER INFO", "🆔 TELEGRAM NUMBER"],
    ["👪 FAMILY INFO", "🌐 IP/DOMAIN RECON"],
    ["🌐 WEBSITE EXTRACTOR", "👑 PREMIUM"],
    ["📊 MY PLAN"],
]


def main_keyboard(admin: bool = False):
    """Grid keyboard - 10 tools + Premium + Admin controls"""
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
    "FAMILY INFO": "familyinfo",
    "FAMILY": "familyinfo",
    "FAMILYINFO": "familyinfo",
    "RATION CARD": "familyinfo",
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
    "familyinfo": {
        "head": "👪 FAMILY INFO - BEST",
        "ask": "12 Digit Aadhaar bhejein:",
        "ex": "401234567849",
    },
    "premium": {
        "head": "👑 PREMIUM PLANS",
        "ask": "Plan chuno ya /buy bhejo:",
        "ex": "/buy 30d",
    },
    "myplan": {
        "head": "📊 MY PLAN",
        "ask": "/myplan se status dekho:",
        "ex": "/myplan",
    },
    "admin_panel": {
        "head": "🛠️ ADMIN PANEL",
        "ask": "/admin se panel kholo:",
        "ex": "/admin",
    },
}

import config
from modules.ip_domain_recon import ip_lookup, dns_lookup, whois_lookup, ssl_check, full_recon
from modules.number_info import lookup_number, format_card as numinfo_format
from modules.telegram_tools import lookup_tg, lookup_pak, format_tg_card, format_pak_card
from modules.website_extractor import website_extractor
from modules.pdf_renamer import rename_pdf_filename, batch_rename, HACKER_NAME, OWNER_ID as PDF_OWNER_ID
from modules.family_info import lookup_family, format_family_card
from modules.database import (
    get_user, get_credits, add_credits, set_credits, spend_credits,
    is_premium_user, is_premium, premium_expiry, grant_premium, revoke_premium,
    create_payment, get_payment, set_payment_status, set_payment_admin_msg,
    utr_exists, pending_payments_count, pending_payments, recent_payments,
    user_payments, all_user_ids, premium_users, recent_users, credits_stats, payment_stats,
    is_banned, set_ban, FREE_CREDITS,
    get_tg_credits, set_tg_credits, spend_tg_credits, apply_credits_config, TG_CREDITS
)
from modules.payments import PLANS, UPI_ID, UPI_NAME, get_upi_link, format_plans, format_plan_detail, format_myplan, format_credits_over
from modules.upi_qr import generate_upi_qr

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ========== v2.0 — VAULT + HEALTH + CRASH-SHIELD + WATCHDOG ==========
START_TS = time.time()
CRASH = {"caught": 0, "fatal": 0}
_INFLIGHT = {}
_INFLIGHT_LOCK = threading.Lock()


def _ram_mb() -> int:
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(int(line.split()[1]) / 1024)
    except Exception:
        pass
    try:
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
    except Exception:
        return 0


def _fmt_age(ts) -> str:
    try:
        ts = float(ts or 0)
    except Exception:
        return "never"
    if not ts:
        return "never"
    s = int(time.time() - ts)
    if s < 90:
        return f"{s}s pehle"
    if s < 5400:
        return f"{s//60} min pehle"
    return f"{s//3600}h pehle"


# VAULT: naye deploy par DB khaali mile to GitHub (branch vault-backup) se
# encrypted backup wapas laao — users/premium/pending payments kabhi na khoye
try:
    import modules.vault as vault
    vault.boot_restore()
    vault.start_backup_loop()
    VAULT_OK = True
except Exception as _ve:
    VAULT_OK = False
    print(f"[VAULT] init skip: {_ve}")


def health_html() -> str:
    """Rich /health (utility-duniya-bot jaisa) — kabhi crash na kare."""
    try:
        commit = (os.getenv("RENDER_GIT_COMMIT") or "")[:7] or "local"
        up = int((time.time() - START_TS) / 60)
        cstats = {}
        db_c = {"live": 0, "total": 0, "hits": 0}
        users = prem = pend = 0
        try:
            from modules.fast_cache import cache_stats as _fs
            cstats = _fs()
        except Exception:
            pass
        try:
            from modules.database import (cache_stats as _dcs, all_user_ids,
                                          premium_users, pending_payments_count)
            db_c = _dcs()
            users = len(all_user_ids())
            prem = len(premium_users())
            pend = pending_payments_count()
        except Exception:
            pass
        vstat = {}
        if VAULT_OK:
            try:
                vstat = vault.status()
            except Exception:
                vstat = {}
        out = (
            "<h1>🚀 OSINT Hunter Hub — LIVE</h1>"
            "<p style='font-family:monospace'>"
            f"version: {BOT_VERSION}<br>"
            f"commit: {commit} | branch: {os.getenv('RENDER_GIT_BRANCH') or 'main'} | mode: WEBHOOK | up: {up}m | ram: {_ram_mb()}MB<br>"
            f"users: {users} | premium: {prem} | pending payments: {pend}<br>"
            f"lookup-cache: {db_c.get('live', 0)} live / {db_c.get('total', 0)} total | instant hits: {db_c.get('hits', 0)}<br>"
            f"memory-cache: {cstats.get('hit_rate', '-')} hit rate ({cstats.get('size', 0)} items)<br>"
            f"vault: {'ON' if VAULT_OK else 'OFF'} | last backup: {_fmt_age(vstat.get('last_ok', 0))}"
            f" | backups: {vstat.get('count', 0)} | restore: {vstat.get('restored') or '-'}"
            + (f" | err: {str(vstat.get('last_err'))[:90]}" if vstat.get('last_err') else "")
            + f"<br>crash-shield: caught={CRASH['caught']} fatal={CRASH['fatal']}"
            "</p>"
        )
        return out
    except Exception as e:
        return f"OK - Bot Alive ({e})"


def watchdog_loop():
    """RAM guard + hang guard (utility-duniya-bot jaisa auto-restart)."""
    mem_limit = int(os.getenv("MEM_RESTART_MB", "470") or 470)
    hang_limit = int(os.getenv("HANG_RESTART_SECONDS", "900") or 900)
    while True:
        time.sleep(60)
        try:
            rss = _ram_mb()
            if mem_limit and rss and rss > mem_limit:
                print(f"WATCHDOG: RAM {rss}MB > {mem_limit}MB — auto restart")
                CRASH["fatal"] += 1
                os._exit(7)
        except Exception:
            pass
        try:
            now = time.time()
            with _INFLIGHT_LOCK:
                stuck = [(k, int(now - v)) for k, v in list(_INFLIGHT.items()) if now - v > hang_limit]
            if stuck:
                print(f"WATCHDOG: update hung >{hang_limit}s {stuck[:3]} — auto restart")
                CRASH["fatal"] += 1
                os._exit(8)
        except Exception:
            pass


threading.Thread(target=watchdog_loop, daemon=True).start()


async def on_error(update, context):
    """Crash-shield: koi bhi error user ko silence na kare."""
    CRASH["caught"] += 1
    try:
        print(f"CRASH-SHIELD caught #{CRASH['caught']}: {str(context.error)[:300]}")
        logger.error("Exception while handling an update:", exc_info=context.error)
    except Exception:
        pass
    try:
        if update and getattr(update, "effective_message", None):
            await update.effective_message.reply_text("⚠️ Thodi technical dikkat aayi — dobara try karo.")
    except Exception:
        pass


async def vault_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    if not VAULT_OK:
        await update.message.reply_text("❌ Vault OFF (VAULT_GITHUB_TOKEN set karo)")
        return
    st = vault.status()
    txt = (
        "🛡️ <b>VAULT STATUS</b>\n\n"
        f"Repo: <code>{st.get('repo')}</code>\n"
        f"Token: {'✅ set' if st.get('token_set') else '❌ missing'}\n"
        f"DB: <code>{st.get('db_path')}</code>\n"
        f"Users in DB: {st.get('db_users', 0)} | size: {st.get('db_bytes', 0)} bytes\n"
        f"Last backup: {_fmt_age(st.get('last_ok', 0))} ({st.get('last_bytes', 0)} bytes, total {st.get('count', 0)})\n"
        f"Restore at boot: {st.get('restored') or '-'}\n"
        f"Last error: {st.get('last_err') or 'none'}"
    )
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)


async def backup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    if not VAULT_OK:
        await update.message.reply_text("❌ Vault OFF")
        return
    m = await update.message.reply_text("⏳ Backup chal raha hai...")
    ok = await asyncio.to_thread(vault.backup_now, True)
    await m.edit_text("✅ Backup ho gaya! /vault se dekho" if ok else "❌ Backup fail — /vault dekho")


async def restore_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.is_admin(update.effective_user.id):
        return
    if not VAULT_OK:
        await update.message.reply_text("❌ Vault OFF")
        return
    res = await asyncio.to_thread(vault.boot_restore)
    await update.message.reply_text(f"🛡️ Restore: {res}")

# ========== CREDITS CHECK - FAST ==========
def can_use_tool(uid: int, tool: str = "") -> tuple:
    """Check if user can use tool - returns (can_use:bool, credits:int, user:dict)
    v2.5.5 (bot-1 jaisa SAME system): tool="tg" -> ALAG TG-credit pool."""
    try:
        if config.is_admin(uid):
            u = get_user(uid)
            return True, u.get("credits", FREE_CREDITS), u
        if is_banned(uid):
            return False, 0, {}
        u = get_user(uid)
        if is_premium(u):
            return True, u.get("credits", FREE_CREDITS), u
        if str(tool).lower() == "tg":
            tg = get_tg_credits(uid)
            return (tg > 0), tg, u
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
        tg = get_tg_credits(uid)
        if credits <= 3 and credits > 0:
            return f"⚠️ <i>Sirf {credits} credits bache - /premium</i> · 🆩 {tg} TG\n"
        elif credits <= 0:
            return f"🔒 <i>Credits khatam - /premium</i> · 🆩 {tg} TG\n"
        else:
            return f"🎁 <i>{credits} credits · 🆩 {tg} TG credits bache</i>\n"
    except:
        return ""

# ========== FORCE JOIN - ULTRA FAST + REAL - FINAL ==========
# Caches for speed: bot admin + user joined (60 sec TTL)
_bot_admin_cache = {"is_admin": None, "timestamp": 0, "notified": 0}
_user_join_cache = {}  # uid -> (bool, expiry)
_user_join_lock = threading.Lock()

def _join_cache_get(uid: int):
    with _user_join_lock:
        if uid in _user_join_cache:
            val, exp = _user_join_cache[uid]
            if time.time() < exp:
                return val
            else:
                del _user_join_cache[uid]
    return None

def _join_cache_set(uid: int, is_joined: bool, ttl: int = 60):
    with _user_join_lock:
        _user_join_cache[uid] = (is_joined, time.time() + ttl)

async def is_user_joined_channel(user_id: int, bot) -> bool:
    """
    ULTRA FAST + REAL verification
    - Owner bypass: instant (no API)
    - Cache: 60 sec per user (fast, secure, rechecks after leave)
    - Single getChatMember call (was 2-3 calls -> 1 call)
    - Temp allow when bot not admin to avoid loop from video
    - Fail closed when possible, but temp allow when bot not admin to avoid UX loop
    """
    if not config.FORCE_CHANNEL:
        return True
    if config.is_admin(user_id):
        return True
    
    # Check cache first - ULTRA FAST 0ms
    cached = _join_cache_get(user_id)
    if cached is not None:
        return cached
    
    try:
        member = await bot.get_chat_member(chat_id=config.FORCE_CHANNEL, user_id=user_id)
        is_joined = member.status in ['member', 'administrator', 'creator', 'restricted']
        _join_cache_set(user_id, is_joined, ttl=60)  # Cache 60 sec
        return is_joined
    except BadRequest as e:
        err = str(e).lower()
        if "member list is inaccessible" in err or "chat not found" in err:
            import time as _time
            now = _time.time()
            if now - _bot_admin_cache.get("notified", 0) > 3600:
                _bot_admin_cache["notified"] = now
                logger.error(f"FORCE JOIN: Bot NOT admin in {config.FORCE_CHANNEL_LINK}! Temp allow user {user_id}. Owner MUST make bot admin.")
                try:
                    asyncio.create_task(
                        bot.send_message(
                            chat_id=config.ADMIN_ID,
                            text=f"⚠️ <b>BOT NOT ADMIN!</b>\n\nBot not admin in {config.FORCE_CHANNEL_LINK}\n\nTemp allowing users to avoid loop. Make bot admin for REAL check!\n\n1. Open channel → Admins → Add @osint_hunter_hub_bot",
                            parse_mode=ParseMode.HTML
                        )
                    )
                except:
                    pass
            _join_cache_set(user_id, True, ttl=300)  # Temp allow 5 min when bot not admin
            return True
        else:
            logger.warning(f"FORCE JOIN BadRequest {user_id}: {e}")
            _join_cache_set(user_id, False, ttl=30)
            return False
    except Exception as e:
        err = str(e).lower()
        if "member list is inaccessible" in err or "forbidden" in err:
            _join_cache_set(user_id, True, ttl=300)
            return True
        logger.warning(f"FORCE JOIN error {user_id}: {e}")
        _join_cache_set(user_id, False, ttl=30)
        return False

async def send_force_join_ui(update: Update, context: ContextTypes.DEFAULT_TYPE, is_retry: bool = False):
    """FAST force join UI - text only, no photo for speed (6 sec -> 1 sec), channel above Verify Now"""
    user = update.effective_user
    
    kb = [
        [InlineKeyboardButton("📢 Join Channel @osint_xpert", url=config.FORCE_CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Verify Now", callback_data="check_joined")]
    ]
    
    if is_retry:
        txt = (
            f"❌ <b>You haven't joined our channel yet. Join the channel first, then tap Verify Now.</b>\n\n"
            f"👋 Hello <b>{user.first_name}</b>!\n\n"
            f"📢 <b>Channel:</b> {config.FORCE_CHANNEL_LINK}\n\n"
            f"1️⃣ Tap Join Channel above\n"
            f"2️⃣ Join the channel\n"
            f"3️⃣ Come back and tap Verify Now\n\n"
            f"🔒 Tools will work only after verification!"
        )
    else:
        txt = (
            f"🚫 <b>ACCESS DENIED - CHANNEL JOIN REQUIRED!</b>\n\n"
            f"👋 Hello <b>{user.first_name}</b>!\n\n"
            f"⚠️ <b>Bot use karne ke liye channel join karna compulsory hai!</b>\n\n"
            f"📢 <b>Channel:</b> {config.FORCE_CHANNEL_LINK}\n"
            f"🔒 Bina join kiye koi bhi tool kaam nahi karega!\n\n"
            f"👇 <b>Step 1:</b> Join Channel pe click karo\n"
            f"👇 <b>Step 2:</b> Wapas aake Verify Now pe click karo\n\n"
            f"✅ Verify ke baad hi tools kaam karenge!"
        )
    
    # FAST: text only, no photo upload for force join (fixes 6-7 sec delay)
    try:
        if update.message:
            await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
        elif update.callback_query:
            await update.callback_query.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
    except Exception as e:
        logger.warning(f"Force join UI send failed: {e}")

async def check_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """FAST check before every protected action - single API call, no extra admin check"""
    if not config.FORCE_CHANNEL:
        return True
    
    user_id = update.effective_user.id
    if config.is_admin(user_id):
        return True

    joined = await is_user_joined_channel(user_id, context.bot)
    if joined:
        return True

    await send_force_join_ui(update, context, is_retry=False)
    return False

async def check_joined_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    FAST verification - single getChatMember check, fixes infinite loop from video
    - If bot not admin, temp allow to avoid loop (user reported Verify Now loop)
    - After bot admin, REAL strict verification
    """
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        joined = await is_user_joined_channel(user_id, context.bot)
        if joined:
            # Verified - either real or temp allow when bot not admin
            await query.edit_message_text(
                f"✅ <b>VERIFIED SUCCESSFULLY!</b>\n\n"
                f"🎉 Aapne channel join kar liya!\n"
                f"🚀 Ab aap bot ke saare tools use kar sakte ho!\n\n"
                f"👇 /start pe click karo tools dekhne ke liye",
                parse_mode=ParseMode.HTML
            )
            try:
                await start(update, context)
            except Exception as e:
                logger.warning(f"Auto start after verify failed: {e}")
        else:
            # Not joined - show retry with channel above Verify Now
            await query.answer("❌ You haven't joined our channel yet. Join the channel first, then tap Verify Now.", show_alert=True)
            kb = [
                [InlineKeyboardButton("📢 Join Channel @osint_xpert", url=config.FORCE_CHANNEL_LINK)],
                [InlineKeyboardButton("✅ Verify Now", callback_data="check_joined")]
            ]
            try:
                await query.edit_message_text(
                    f"❌ <b>You haven't joined our channel yet. Join the channel first, then tap Verify Now.</b>\n\n"
                    f"📢 <b>Channel:</b> {config.FORCE_CHANNEL_LINK}\n\n"
                    f"1️⃣ Tap Join Channel above\n"
                    f"2️⃣ Join the channel\n"
                    f"3️⃣ Come back and tap Verify Now\n\n"
                    f"🔒 Tools will work only after verification!",
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(kb)
                )
            except:
                try:
                    await query.message.reply_text(
                        f"❌ <b>You haven't joined our channel yet.</b>\n\n📢 {config.FORCE_CHANNEL_LINK}",
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(kb)
                    )
                except:
                    pass
    except Exception as e:
        logger.warning(f"check_joined_callback error: {e}")
        await query.answer(f"❌ Verification failed, retry!", show_alert=True)
        kb = [
            [InlineKeyboardButton("📢 Join Channel @osint_xpert", url=config.FORCE_CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Verify Now", callback_data="check_joined")]
        ]
        try:
            await query.message.reply_text(f"⚠️ Retry!\n\n📢 {config.FORCE_CHANNEL_LINK}", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
        except:
            pass

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

        # Try to send photo banner + caption + grid - NO WHITE LINING MESSAGE
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
                # REMOVED white lining message as per user request - no extra "Neeche menu se tool chuno - 8 Tools Ready!" message
            else:
                if reply_kb:
                    await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=reply_kb)
                else:
                    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
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
                    "👑 <b>Owner:</b> @Supermannn_x\n\n🤖 <b>Bot:</b> @osint_hunter_hub_bot",
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
            if len(d) == 12 and len(raw)>=12:
                # Aadhaar 12 digits
                current_mode = "familyinfo"
            elif len(d) == 10 and d[0] in "6789":
                current_mode = "numinfo"
            elif raw.startswith("@") or raw.replace("@","").replace("_","").isalnum() and len(raw) >= 4 and len(raw) <= 32 and " " not in raw:
                # Could be telegram username
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
        
        print(f"Processing input '{text}' as mode {current_mode}", flush=True)
        
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
        elif current_mode == "familyinfo":
            context.args = [text]
            await family_info_cmd(update, context)
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
            # v2.5.4 (USER ORDER): user ka text echo nahi karna
            await update.message.reply_text("🔧 Ye mode abhi available nahi hai — /start se menu kholo.", parse_mode=ParseMode.HTML)
            
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
    # ⚡ v2.2 FEEL-FAST (utility-duniya-bot jaisa): offline parse 0 ms me hota
    # hai — pehle number validate karo aur TURANT circle/operator hint dikhao.
    # Provider 8-11 sec leta hai, par user ko 1 second me pata chal jata hai
    # ki number sahi hai. Galat number par API call HI NAHI hoti (instant reply).
    _off = {"ok": True}
    try:
        from modules.phone_offline import lookup_phone_info as _offline
        _off = _offline(number)
    except Exception:
        pass
    if not _off.get("ok"):
        await update.message.reply_text(
            f"❌ {_off.get('error')}", parse_mode=ParseMode.HTML)
        return
    # v2.5.4 (USER ORDER): wait msg me user ka number/operator/circle echo NAHI.
    status = await update.message.reply_text(WAIT2, parse_mode=ParseMode.HTML)

    _t0 = time.time()
    try:
        result = await asyncio.to_thread(lookup_number, number)
        try:
            print(f"[TIMING] numinfo {int((time.time()-_t0)*1000)}ms ok={result.get('ok')} cached={result.get('cached', False)}", flush=True)
        except Exception:
            pass
        
        # Advanced formatting with spaces and emojis
        if not result.get("ok"):
            # v2.5.4 (USER ORDER): fail/timeout/error — sab par sirf ek line.
            # v2.5.4 (USER ORDER): fail = sirf ye ek line.
            await status.edit_text(NF2, parse_mode=ParseMode.HTML)
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
"""

        await status.edit_text(txt, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.exception(e)
        await status.edit_text(NF2, parse_mode=ParseMode.HTML)

# ========== FAMILY INFO - BEST ==========
async def family_info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    can_use, creds, user = can_use_tool(uid)
    if not can_use:
        await update.message.reply_text(format_credits_over("Family Info"), parse_mode=ParseMode.HTML)
        return
    if not context.args:
        await update.message.reply_text(
            f"❌ <b>Use:</b> <code>/family 401234567849</code>\n\n"
            f"📌 Example:\n"
            f"<code>/family 401234567849</code>\n"
            f"<code>/finfo 401234567849</code>\n\n"
            f"🔒 Aadhaar masked: XXXX-XXXX-1234\n"
            f"📋 Ration card + family members\n\n"
            f"{credits_line(uid)}",
            parse_mode=ParseMode.HTML
        )
        return

    aadhaar = context.args[0]
    status = await update.message.reply_text(WAIT2, parse_mode=ParseMode.HTML)

    _t0 = time.time()
    try:
        result = await asyncio.to_thread(lookup_family, aadhaar)
        try:
            print(f"[TIMING] family {int((time.time()-_t0)*1000)}ms ok={result.get('ok')} cached={result.get('cached', False)}", flush=True)
        except Exception:
            pass
        txt = format_family_card(result)
        # Spend credit
        try:
            left = spend_credits(uid, 1)
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.exception(e)
        await status.edit_text(NF2, parse_mode=ParseMode.HTML)

# ========== UPI INFO - BEST - YOUR API ==========
# ========== TG TOOLS ==========
async def tg_number_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    uid = update.effective_user.id
    can_use, creds, user = can_use_tool(uid, "tg")   # v2.5.5: TG ka ALAG pool
    if not can_use:
        from modules.payments import UPI_ID
        import html as _h
        await update.message.reply_text(
            f"🔒 <b>Aapke {TG_CREDITS} free TG credits khatam ho gaye</b>\n\n"
            f"Har naye user ko <b>{TG_CREDITS} free TG credits</b> milte hain —\n"
            f"aapne saare use kar liye. 👏\n\n"
            f"👑 <b>Premium lo</b> — TELEGRAM NUMBER + baaki saare tools <b>unlimited</b>!\n"
            f"💎 /premium se plans dekho\n\n"
            f"💳 UPI: <code>{_h.escape(UPI_ID)}</code>",
            parse_mode=ParseMode.HTML)
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
    status = await update.message.reply_text(WAIT2, parse_mode=ParseMode.HTML)

    _t0 = time.time()
    try:
        result = await asyncio.to_thread(lookup_tg, username)
        try:
            print(f"[TIMING] tg {int((time.time()-_t0)*1000)}ms ok={result.get('ok')} cached={result.get('cached', False)}", flush=True)
        except Exception:
            pass
        
        if not result.get("ok"):
            # v2.5.1 FIX: pehle FAIL hone par bhi credit kat jata tha (bug) aur
            # hamesha wahi ek jhootha line dikhta tha. Ab asli error dikhta hai
            # aur credit SIRF success par katta hai.
            await status.edit_text(NF2, parse_mode=ParseMode.HTML)
            return

        data = result.get("data", {}) if isinstance(result.get("data"), dict) else {}
        ms = result.get("ms", 0)
        # v2.5.4 (USER ORDER): public-profile/t.me data ab card NAHI banta —
        # number na mile to sirf "data not found in any database".
        _mobile = str(data.get("mobile") or data.get("owner_number") or data.get("phone_number") or "").strip()
        if not _mobile or data.get("source") == "t.me-public":
            await status.edit_text(NF2, parse_mode=ParseMode.HTML)
            return
        _tgid = str(data.get("telegram_id") or data.get("tg_id") or "").strip()
        _uname = str(data.get("username") or result.get("term") or "").strip().lstrip("@")
        _ctry = str(data.get("country_code") or data.get("country") or "").strip()
        _L = [f"🆩 <b>TELEGRAM NUMBER — @{_uname}</b>",
              "━━━━━━━━━━━━━━━━━━━━━━",
              "",
              f"📱 Number : <code>{_mobile}</code>"]
        if _tgid:
            _L.append(f"🆩 Telegram ID : <code>{_tgid}</code>")
        if _uname:
            _L.append(f"👤 Username : @{_uname}")
        if _ctry:
            _L.append(f"🌍 Country : {_ctry}")
        _L += ["", f"⚡ <b>Response:</b> {ms}ms",
               "🔥 <b>Powered by @Supermannn_x</b>"]
        txt = "\n".join(_L)
        try:
            left = spend_tg_credits(uid, 1)   # v2.5.5: TG pool se kato
            txt += f"\n{credits_line(uid)}"
        except:
            pass
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        await status.edit_text(NF2, parse_mode=ParseMode.HTML)

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
    status = await update.message.reply_text(WAIT2, parse_mode=ParseMode.HTML)

    _t0 = time.time()
    try:
        result = await asyncio.to_thread(lookup_pak, num)
        try:
            print(f"[TIMING] pak {int((time.time()-_t0)*1000)}ms ok={result.get('ok')} cached={result.get('cached', False)}", flush=True)
        except Exception:
            pass
        if not result.get("ok"):
            try:
                left = spend_credits(uid, 1)
                txt += f"\n{credits_line(uid)}"
            except:
                pass
            await status.edit_text(NF2, parse_mode=ParseMode.HTML)
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
        await status.edit_text(NF2, parse_mode=ParseMode.HTML)

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
        await status.edit_text(NF2, parse_mode=ParseMode.HTML)

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
    status = await update.message.reply_text(WAIT2, parse_mode=ParseMode.HTML)

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
        await status.edit_text(NF2, parse_mode=ParseMode.HTML)

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
    status = await update.message.reply_text(WAIT2, parse_mode=ParseMode.HTML)

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
        await status.edit_text(NF2, parse_mode=ParseMode.HTML)

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
    status = await update.message.reply_text(WAIT2, parse_mode=ParseMode.HTML)

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
        await status.edit_text(NF2, parse_mode=ParseMode.HTML)

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
        await status.edit_text(NF2, parse_mode=ParseMode.HTML)

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
    status = await update.message.reply_text(WAIT2, parse_mode=ParseMode.HTML)

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
        await status.edit_text(NF2, parse_mode=ParseMode.HTML)

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
# ========== GITHUB LEAK HUNTER - PRO ==========
# ========== TERABOX EXTRACTOR - PRO ==========
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
    # Try to send with QR for default plan (30D) - per user request QR wala
    try:
        # Default QR for 30D plan ₹49
        default_plan = PLANS.get("30d") or list(PLANS.values())[0]
        qr_bio = await asyncio.to_thread(generate_upi_qr, default_plan['amount'], default_plan['name'], f"OSINT {default_plan['name']}")
        if qr_bio:
            await update.message.reply_photo(
                photo=qr_bio,
                caption=txt[:1000],
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(kb)
            )
        else:
            await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
    except Exception as e:
        print(f"premium_cmd QR error: {e}")
        try:
            await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
        except Exception as e2:
            print(f"premium_cmd text also failed: {e2}")
            await update.message.reply_text(f"Premium plans: /buy 30d etc\nUPI: {UPI_ID}", reply_markup=InlineKeyboardMarkup(kb))

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
        await update.message.reply_text(f"❌ Invalid plan <code>{html.escape(plan_key)}</code>\n\nValid: {', '.join(PLANS.keys())}\n\n/premium se dekho", parse_mode=ParseMode.HTML)
        return
    uid = update.effective_user.id
    get_user(uid, update.effective_user.first_name or "", update.effective_user.username or "")
    txt = format_plan_detail(plan_key)
    kb = [
        [InlineKeyboardButton("📢 Channel", url=config.FORCE_CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Paid - Send Screenshot", callback_data=f"paid_{plan_key}")],
        [InlineKeyboardButton("📖 How to Pay?", callback_data="howtopay")]
    ]
    # Send with QR
    try:
        qr_bio = await asyncio.to_thread(generate_upi_qr, plan['amount'], plan['name'], f"OSINT {plan['name']}")
        if qr_bio:
            await update.message.reply_photo(
                photo=qr_bio,
                caption=txt[:1000],
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(kb)
            )
        else:
            await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
    except Exception as e:
        print(f"buy_cmd QR error: {e}")
        try:
            await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
        except:
            plain = f"Plan: {plan['name']}\nAmount: ₹{plan['amount']}\nUPI: {UPI_ID}\n/pay {plan_key} UTR + screenshot"
            await update.message.reply_text(plain, reply_markup=InlineKeyboardMarkup(kb))

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
        
        try:
            if VAULT_OK:
                vault.backup_soon()
        except Exception:
            pass
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
    try:
        if VAULT_OK:
            vault.backup_soon()
    except Exception:
        pass

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
                    [InlineKeyboardButton("📢 Channel", url=config.FORCE_CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ Paid - Send Screenshot", callback_data=f"paid_{plan_key}")],
                    [InlineKeyboardButton("📖 How to Pay?", callback_data="howtopay")]
                ]
                # Generate QR with fixed price
                try:
                    qr_bio = await asyncio.to_thread(generate_upi_qr, plan['amount'], plan['name'], f"OSINT {plan['name']}")
                    if qr_bio:
                        # Send photo with QR + caption
                        await context.bot.send_photo(
                            chat_id=query.message.chat_id,
                            photo=qr_bio,
                            caption=txt[:1000],
                            parse_mode=ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(kb)
                        )
                    else:
                        # Fallback without QR
                        await query.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
                except Exception as qr_err:
                    print(f"QR send failed for {plan_key}: {qr_err}")
                    # Try without QR
                    try:
                        await query.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
                    except Exception as html_err:
                        print(f"HTML parse failed for buy_{plan_key}: {html_err}, sending plain")
                        plain = f"Plan: {plan['name']}\nAmount: ₹{plan['amount']}\nDuration: {plan['days']} days\n\nUPI: {UPI_ID}\n\nSteps:\n1. Pay ₹{plan['amount']} to {UPI_ID}\n2. Send screenshot + UTR\n3. /pay {plan_key} UTR"
                        await query.message.reply_text(plain, reply_markup=InlineKeyboardMarkup(kb))
            except Exception as e:
                print(f"Buy callback error {plan_key}: {e}")
                traceback.print_exc()
                try:
                    await query.message.reply_text(f"Plan {plan_key} - ₹{plan['amount']} - UPI {UPI_ID} - /pay {plan_key} UTR", parse_mode=ParseMode.HTML)
                except:
                    pass
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
    # v2.5.5 (bot-1 jaisa): Render env FREE_CREDITS/TG_CREDITS badle -> sab reset
    try:
        print("💳", apply_credits_config(), flush=True)
    except Exception as _ce:
        print("credits cfg skip:", _ce, flush=True)
    
    # ==================================================================
    #  ⚡ v2.4 SPEED FIX — ASLI WAJAH YAHI THI (bot 1 ke barabar settings)
    # ==================================================================
    #  PTB ke DEFAULT khatarnak hain:
    #    connection_pool_size = 1   -> Telegram API ke liye sirf EK connection
    #    read_timeout = 5.0         -> 5 sec me jawab na aaye to TimeoutError
    #    pool_timeout = 1.0         -> connection busy ho to 1 sec me FAIL
    #    concurrent_updates = OFF   -> saare updates EK-EK karke (ek slow
    #                                  lookup poore bot ko rok deta hai)
    #  Iska nateeja: silent timeouts — message bhejna chup-chaap fail ho jata
    #  tha, user ko lagta tha "bot slow hai / jawab hi nahi aaya".
    #  Ab: 32 connections, 60s read timeout, 8 updates parallel.
    try:
        _max_cu = int(os.getenv('MAX_CONCURRENT_UPDATES', '8') or 8)
    except Exception:
        _max_cu = 8
    _max_cu = max(2, min(32, _max_cu))
    app = (Application.builder().token(BOT_TOKEN)
           .connect_timeout(30.0).read_timeout(60.0).write_timeout(120.0)
           .pool_timeout(60.0).connection_pool_size(32)
           .http_version("1.1")
           .concurrent_updates(_max_cu)
           .build())
    print(f"[SPEED] concurrent_updates={_max_cu} | pool=32 | read_timeout=60s "
          f"(PTB default tha: OFF / pool=1 / 5s)", flush=True)
    app.add_error_handler(on_error)
    print(f"🔎 SELF-CHECK | {BOT_VERSION.split('(')[0].strip()} | crypto=ON | vault={'ON' if VAULT_OK else 'OFF'} | channel=@{config.FORCE_CHANNEL_USERNAME} | self_url={BOT_SELF_URL}")

    # Core
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(help_callback))

    # Number Info - KEEP
    app.add_handler(CommandHandler("numinfo", number_info_cmd))
    app.add_handler(CommandHandler("number", number_info_cmd))
    app.add_handler(CommandHandler("num", number_info_cmd))

    # Family Info - BEST
    app.add_handler(CommandHandler("family", family_info_cmd))
    app.add_handler(CommandHandler("finfo", family_info_cmd))
    app.add_handler(CommandHandler("familyinfo", family_info_cmd))
    app.add_handler(CommandHandler("ration", family_info_cmd))
    app.add_handler(CommandHandler("aadhaar", family_info_cmd))

    # UPI Info - NEW BEST - YOUR API

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

    # TeraBox Extractor

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
    app.add_handler(CommandHandler("vault", vault_cmd))
    app.add_handler(CommandHandler("backup", backup_cmd))
    app.add_handler(CommandHandler("restore", restore_cmd))
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
        await app.bot.set_webhook(url=WEBHOOK_URL, allowed_updates=["message","callback_query","my_chat_member"],
                                   secret_token=(WEBHOOK_SECRET or None))
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
        print(f"6 tools + payments alive - Users: {len(all_user_ids())} - Premium: {len(premium_users())} - Pending: {pending_payments_count()}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
