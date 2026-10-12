"""
OSINT Hacker Tools Hub - Main Bot
Repo: savecontentrestricted-pixel/osint

Tools:
1. Telegram Channel Scraper (Advanced)
2. Instagram OSINT
3. Email OSINT
4. IP & Domain Recon
5. Image EXIF Forensics

Note: Render pe abhi deploy nahi karna hai, sirf GitHub pe rakha hai as per user.
"""

import os
import asyncio
import logging
import json
import tempfile
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

import config
from modules.telegram_scraper import TelegramScraper
from modules.ip_domain_recon import ip_lookup, dns_lookup, whois_lookup, ssl_check, full_recon
from modules.image_exif import analyze_exif, exif_to_text
from modules.instagram_osint import instagram_osint
from modules.email_osint import email_osint
from modules.social_security_checker import social_security_check, security_report_text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global scraper instance
scraper: TelegramScraper = None

def get_scraper() -> TelegramScraper:
    global scraper
    if scraper is None:
        if not config.API_ID or not config.API_HASH or not config.SESSION_STRING:
            raise Exception("API_ID/API_HASH/SESSION_STRING missing in .env - Telegram scraper ke liye zaruri hai")
        scraper = TelegramScraper(config.API_ID, config.API_HASH, config.SESSION_STRING)
    return scraper

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    txt = f"""
🚀 <b>OSINT Hacker Hub - 5 Tools Ready</b>
👋 Hello {user.first_name}!

<b>Repo: savecontentrestricted-pixel/osint</b>

<b>🔥 Available Tools:</b>

<b>1. Telegram Scraper (Advanced)</b>
/channel_info @channel - Channel info
/scrape @channel 100 - Messages scrape
/scrape_search @channel keyword 100
/scrape_media @channel 50
/stats @channel
/batch @ch1 @ch2 30

<b>2. Instagram OSINT</b>
/insta @username - Public profile info

<b>3. Email OSINT</b>
/email test@gmail.com - Breach + Gravatar + Validation

<b>4. IP & Domain Recon</b>
/ip 8.8.8.8 - IP lookup + VPN detection + Maps
/domain google.com - Full domain recon
/dns google.com - DNS records
/whois google.com - WHOIS info
/ssl google.com - SSL certificate

<b>5. Image EXIF Forensics</b>
Photo bhejo (as file/document) → EXIF + GPS + Camera info
/exif - Reply to photo

<b>📌 Examples:</b>
<code>/scrape @durov 50</code>
<code>/insta @instagram</code>
<code>/email test@gmail.com</code>
<code>/ip 1.1.1.1</code>
<code>/domain github.com</code>

<b>⚠️ Note:</b> Sirf public data, educational OSINT ke liye.

Upcoming: Website Tech Detector, Link Scanner, Crypto Wallet OSINT etc.
"""
    kb = [
        [InlineKeyboardButton("📢 Channel", url="https://t.me/osint_xpert"), InlineKeyboardButton("💬 Support", url="https://t.me/Supermannn_x")],
        [InlineKeyboardButton("📜 Help", callback_data="help"), InlineKeyboardButton("🔧 All Tools", callback_data="tools")]
    ]
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = """
<b>📖 OSINT Hub - Full Guide</b>

<b>--- Tool 1: Telegram Scraper ---</b>
/channel_info @username - Full channel info
/scrape @channel [limit] - Last N messages (max 10000)
/scrape_search @channel keyword [limit] - Search inside channel
/scrape_media @channel [limit] - Only media messages
/stats @channel - Top posts + stats
/batch @ch1 @ch2 [limit] - Multiple channels

<b>--- Tool 2: Instagram OSINT ---</b>
/insta @username - Public profile: followers, bio, posts, pic

<b>--- Tool 3: Email OSINT ---</b>
/email test@gmail.com - Validation, disposable check, Gravatar, breach check (xposedornot), MX records

<b>--- Tool 4: IP & Domain Recon ---</b>
/ip 8.8.8.8 or /ip google.com - IP location, ISP, VPN/Proxy detection, Maps link
/domain google.com - Full recon: DNS + WHOIS + SSL + IP
/dns google.com - A, MX, NS, TXT records
/whois google.com - WHOIS info
/ssl google.com - SSL cert info

<b>--- Tool 5: Image EXIF ---</b>
Koi bhi photo ko <b>File/Document ke roop me bhejo</b> (compressed nahi), bot EXIF nikal dega: GPS location, camera model, date, editing info
Ya photo pe reply karke /exif likho

<b>🛡️ Safety:</b>
• Telegram scraper me FloodWait auto handle + delay
• IP/Domain free APIs (ip-api.com, hackertarget)
• EXIF sirf jo photo me hai wahi dikhega, stripped photo me nahi

<b>Setup:</b> .env.example dekho, generate_session.py se SESSION_STRING banao
"""
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

# ========== TELEGRAM SCRAPER COMMANDS ==========

async def channel_info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/channel_info @channelusername</code>", parse_mode=ParseMode.HTML)
        return
    channel = context.args[0]
    await update.message.reply_text(f"🔍 Fetching info for <code>{channel}</code>...", parse_mode=ParseMode.HTML)
    try:
        scr = get_scraper()
        info = await scr.get_channel_info(channel)
        if not info.get("ok"):
            await update.message.reply_text(f"❌ Error: {info.get('error')}", parse_mode=ParseMode.HTML)
            return
        txt = f"""
📊 <b>Channel Info: {info.get('title')}</b>

🆔 <b>ID:</b> <code>{info.get('id')}</code>
👤 <b>Username:</b> @{info.get('username') or 'None'}
📛 <b>Title:</b> {info.get('title')}
🔰 <b>Type:</b> {info.get('type')} | Broadcast: {info.get('is_broadcast')} | Megagroup: {info.get('is_megagroup')}
👥 <b>Members:</b> {info.get('participants_count') or 'N/A'} | Online: {info.get('online_count') or 'N/A'}
✅ <b>Verified:</b> {info.get('is_verified')} | Scam: {info.get('is_scam')} | Fake: {info.get('is_fake')}
📅 <b>Created:</b> {info.get('creation_date') or 'N/A'}

📝 <b>Description:</b>
{info.get('description')[:1000] or 'No description'}

🔗 <b>Link:</b> https://t.me/{info.get('username') or ''}
"""
        await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.exception(e)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def scrape_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    status_msg = await update.message.reply_text(f"⏳ Scraping <code>{channel}</code> — {limit} messages...", parse_mode=ParseMode.HTML)
    try:
        scr = get_scraper()
        result = await scr.scrape_messages(channel, limit=limit)
        if not result.get("ok"):
            await status_msg.edit_text(f"❌ Error: {result.get('error')}", parse_mode=ParseMode.HTML)
            return
        messages = result.get("messages", [])
        stats = result.get("stats", {})
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, f"{channel.strip('@')}_{limit}.json")
            csv_path = os.path.join(tmpdir, f"{channel.strip('@')}_{limit}.csv")
            scr.export_json(result, json_path)
            scr.export_csv(messages, csv_path)
            summary = f"""
✅ <b>Scraped {len(messages)} messages from {channel}</b>

📊 <b>Stats:</b>
• Total: {stats.get('total')}
• Total Views: {stats.get('total_views')}
• Avg Views: {stats.get('avg_views')}
• Media: {stats.get('media_count')} ({stats.get('media_ratio')}%)
• Links: {stats.get('link_count')} | Hashtags: {stats.get('hashtag_count')}

🔝 <b>Top 3:</b>
"""
            for i, tp in enumerate(stats.get('top_posts', [])[:3], 1):
                summary += f"{i}. {tp.get('views')} views - {tp.get('link')}\n"
            await status_msg.edit_text(summary, parse_mode=ParseMode.HTML)
            await update.message.reply_document(document=open(json_path, 'rb'), filename=os.path.basename(json_path), caption="📄 Full JSON")
            await update.message.reply_document(document=open(csv_path, 'rb'), filename=os.path.basename(csv_path), caption="📊 CSV")
    except Exception as e:
        logger.exception(e)
        await status_msg.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def scrape_search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    status_msg = await update.message.reply_text(f"🔍 Searching '{keyword}' in {channel}...", parse_mode=ParseMode.HTML)
    try:
        scr = get_scraper()
        result = await scr.scrape_messages(channel, limit=limit, search_query=keyword)
        if not result.get("ok"):
            await status_msg.edit_text(f"❌ Error: {result.get('error')}", parse_mode=ParseMode.HTML)
            return
        messages = result.get("messages", [])
        if not messages:
            await status_msg.edit_text(f"❌ No results for '{keyword}'", parse_mode=ParseMode.HTML)
            return
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, f"{channel.strip('@')}_search_{keyword}.json")
            scr.export_json(result, json_path)
            summary = f"✅ Found {len(messages)} messages for '{keyword}'\n\n"
            for m in messages[:5]:
                summary += f"• {m['id']} | {m['views']} views | {m['link']}\n{m['text'][:80]}...\n\n"
            await status_msg.edit_text(summary[:4000], parse_mode=ParseMode.HTML)
            await update.message.reply_document(document=open(json_path, 'rb'), filename=os.path.basename(json_path))
    except Exception as e:
        logger.exception(e)
        await status_msg.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def scrape_media_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    status_msg = await update.message.reply_text(f"🎬 Scraping media from {channel}...", parse_mode=ParseMode.HTML)
    try:
        scr = get_scraper()
        result = await scr.scrape_messages(channel, limit=limit, media_only=True)
        if not result.get("ok"):
            await status_msg.edit_text(f"❌ Error: {result.get('error')}", parse_mode=ParseMode.HTML)
            return
        messages = result.get("messages", [])
        summary = f"✅ Found {len(messages)} media messages\n"
        for m in messages[:10]:
            summary += f"• {m['id']} | {m.get('media',{}).get('type')} | {m['link']}\n"
        await status_msg.edit_text(summary[:4000], parse_mode=ParseMode.HTML)
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/stats @channel</code>", parse_mode=ParseMode.HTML)
        return
    channel = context.args[0]
    status_msg = await update.message.reply_text(f"📊 Stats for {channel} (200 sample)...", parse_mode=ParseMode.HTML)
    try:
        scr = get_scraper()
        result = await scr.scrape_messages(channel, limit=200)
        if not result.get("ok"):
            await status_msg.edit_text(f"❌ Error: {result.get('error')}", parse_mode=ParseMode.HTML)
            return
        stats = result.get("stats", {})
        txt = f"""
📊 <b>Stats for {channel}</b>

• Total: {stats.get('total')}
• Views: {stats.get('total_views')} | Avg: {stats.get('avg_views')}
• Media: {stats.get('media_count')} ({stats.get('media_ratio')}%)
• Top 10:
"""
        for i, tp in enumerate(stats.get('top_posts', [])[:10], 1):
            txt += f"{i}. {tp.get('views')} views - {tp.get('link')}\n"
        await status_msg.edit_text(txt[:4000], parse_mode=ParseMode.HTML)
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def batch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❌ Use: <code>/batch @ch1 @ch2 [limit]</code>", parse_mode=ParseMode.HTML)
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
    status_msg = await update.message.reply_text(f"⏳ Batch {len(channels)} channels...", parse_mode=ParseMode.HTML)
    try:
        scr = get_scraper()
        results = await scr.batch_scrape(channels, limit_per_channel=limit)
        txt = f"✅ Batch done:\n\n"
        for ch, res in results.items():
            if res.get("ok"):
                txt += f"• {ch}: {res.get('scraped')} msgs\n"
            else:
                txt += f"• {ch}: ❌ {res.get('error')}\n"
        await status_msg.edit_text(txt, parse_mode=ParseMode.HTML)
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

# ========== TOOL 2: INSTAGRAM ==========
async def insta_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
📸 <b>Instagram OSINT: @{result.get('username')}</b>

👤 <b>Name:</b> {result.get('full_name') or 'N/A'}
📝 <b>Bio:</b> {result.get('bio')[:500] or 'N/A'}
👥 <b>Followers:</b> {result.get('followers') or 'N/A'}
👤 <b>Following:</b> {result.get('following') or 'N/A'}
📸 <b>Posts:</b> {result.get('posts') or 'N/A'}
🔗 <b>URL:</b> {result.get('profile_url')}
🖼️ <b>Pic:</b> {result.get('profile_pic') or 'N/A'}

⚠️ Note: Instagram blocks heavily, data limited to public OG tags
"""
        await status.edit_text(txt, parse_mode=ParseMode.HTML)
    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

# ========== TOOL 3: EMAIL ==========
async def email_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
📧 <b>Email OSINT: {email}</b>

✅ <b>Validation:</b>
• Valid Format: {v.get('is_valid_format')}
• Domain: {v.get('domain')}
• Disposable: {v.get('is_disposable')}
• Free Provider: {v.get('is_free_provider')}

🖼️ <b>Gravatar:</b>
• Has Gravatar: {g.get('has_gravatar')}
• Hash: <code>{g.get('hash')}</code>
• URL: {g.get('gravatar_url') or 'N/A'}

🔓 <b>Breach Check (xposedornot):</b>
• Breached: {b.get('breached')}
• Count: {b.get('breach_count')}
• Breaches: {', '.join(b.get('breaches', [])[:5]) or 'None'}

📡 <b>MX Records:</b> {', '.join(result.get('mx_records', [])[:3]) or 'N/A'}

💡 <b>Notes:</b>
{chr(10).join(result.get('suggestions', [])) or 'No issues'}
"""
        await status.edit_text(txt, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

# ========== TOOL 4: IP & DOMAIN ==========
async def ip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
🌐 <b>IP Recon: {result.get('ip')}</b>

📍 <b>Location:</b> {result.get('city')}, {result.get('region')}, {result.get('country')} ({result.get('continent')})
🗺️ <b>Coords:</b> {result.get('lat')}, {result.get('lon')}
🔗 <b>Maps:</b> {result.get('google_maps')}
🏙️ <b>Zip:</b> {result.get('zip')} | ⏰ <b>TZ:</b> {result.get('timezone')}

🏢 <b>ISP:</b> {result.get('isp')}
🏛️ <b>Org:</b> {result.get('org')}
🔢 <b>AS:</b> {result.get('as')}

🛡️ <b>Security:</b>
• Is Proxy: {result.get('is_proxy')}
• Is Hosting: {result.get('is_hosting')}
• VPN/Proxy Detected: {result.get('is_vpn_proxy')}

🔁 <b>Reverse DNS:</b> {result.get('reverse_dns') or 'N/A'}
"""
        await status.edit_text(txt, parse_mode=ParseMode.HTML)
    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def domain_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/domain google.com</code>", parse_mode=ParseMode.HTML)
        return
    target = context.args[0]
    status = await update.message.reply_text(f"🌐 Full recon for {target}...", parse_mode=ParseMode.HTML)
    try:
        result = full_recon(target)
        if result.get("type") == "ip":
            # It's IP
            ip_info = result.get("ip_info", {})
            await status.edit_text(f"IP detected, use /ip command. Info: {ip_info}", parse_mode=ParseMode.HTML)
            return
        
        dns_info = result.get("dns", {})
        whois_info = result.get("whois", {})
        ssl_info = result.get("ssl", {})
        ip_info = result.get("ip_info", {})

        txt = f"""
🌐 <b>Domain Recon: {result.get('target')}</b>

<b>--- DNS ---</b>
• A: {', '.join(dns_info.get('records',{}).get('A',[])[:2]) if isinstance(dns_info.get('records',{}).get('A'), list) else dns_info.get('records',{}).get('A')}
• MX: {', '.join(dns_info.get('records',{}).get('MX',[])[:2]) if isinstance(dns_info.get('records',{}).get('MX'), list) else 'N/A'}
• NS: {', '.join(dns_info.get('records',{}).get('NS',[])[:2]) if isinstance(dns_info.get('records',{}).get('NS'), list) else 'N/A'}
• IP: {dns_info.get('ip') or 'N/A'}

<b>--- WHOIS ---</b>
• Registrar: {whois_info.get('registrar') or 'N/A'}
• Created: {whois_info.get('creation_date') or 'N/A'}
• Expires: {whois_info.get('expiration_date') or 'N/A'}
• NS: {', '.join(whois_info.get('name_servers',[])[:2]) if whois_info.get('name_servers') else 'N/A'}

<b>--- SSL ---</b>
• Issuer: {ssl_info.get('issuer') or 'N/A'}
• Subject: {ssl_info.get('subject') or 'N/A'}
• Valid From: {ssl_info.get('not_before') or 'N/A'}
• Valid To: {ssl_info.get('not_after') or 'N/A'}
• SAN: {', '.join(ssl_info.get('san',[])[:3]) if ssl_info.get('san') else 'N/A'}

<b>--- IP Info ---</b>
• IP: {ip_info.get('ip') if ip_info and ip_info.get('ok') else 'N/A'}
• Location: {ip_info.get('city') if ip_info and ip_info.get('ok') else 'N/A'}, {ip_info.get('country') if ip_info and ip_info.get('ok') else ''}
• ISP: {ip_info.get('isp') if ip_info and ip_info.get('ok') else 'N/A'}
"""
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def dns_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/dns google.com</code>", parse_mode=ParseMode.HTML)
        return
    target = context.args[0]
    status = await update.message.reply_text(f"🔍 DNS lookup for {target}...", parse_mode=ParseMode.HTML)
    try:
        result = dns_lookup(target)
        txt = f"🌐 <b>DNS for {result.get('domain')}</b>\n\n"
        for k, v in result.get("records", {}).items():
            txt += f"<b>{k}:</b> {', '.join(v) if isinstance(v, list) else v}\n"
        await status.edit_text(txt[:4000], parse_mode=ParseMode.HTML)
    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def whois_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# ========== TOOL 5: EXIF ==========
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Photo as document or photo
    file = None
    if update.message.document:
        file = await update.message.document.get_file()
        file_name = update.message.document.file_name
    elif update.message.photo:
        # Get highest resolution
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
            
            # Send raw JSON if has GPS
            if analysis.get("has_gps"):
                json_path = os.path.join(tmpdir, f"{file_name}_exif.json")
                with open(json_path, 'w') as f:
                    json.dump(analysis, f, indent=2, default=str)
                await update.message.reply_document(document=open(json_path, 'rb'), filename=os.path.basename(json_path), caption="📍 Full EXIF JSON with GPS")
    except Exception as e:
        logger.exception(e)
        await status.edit_text(f"❌ EXIF Error: {str(e)}", parse_mode=ParseMode.HTML)

async def exif_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # If reply to photo
    if update.message.reply_to_message and (update.message.reply_to_message.photo or update.message.reply_to_message.document):
        # Reuse handle_photo logic but with replied message
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
        await update.message.reply_text("❌ Photo bhejo as <b>Document/File</b> (compressed nahi), ya kisi photo pe reply karke /exif likho.\n\nTip: Telegram photo ko compress karta hai aur EXIF hata deta hai, isliye hamesha <b>File ke roop me bhejo</b> (📎 → File → Gallery se select).", parse_mode=ParseMode.HTML)


async def igsecure_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/igsecure @username</code> ya <code>/security @username</code>\nExample: <code>/igsecure @instagram</code>", parse_mode=ParseMode.HTML)
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
        import logging
        logging.exception(e)
        await status.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

def main():

    # Telegram scraper needs API_ID etc, but other tools work without it
    # So we don't hard fail if missing, just warn
    missing = config.validate()
    if missing:
        print(f"⚠️ Missing for Telegram scraper: {', '.join(missing)} - Telegram scraper commands fail karenge, baaki tools chalenge")

    if not config.BOT_TOKEN:
        print("❌ BOT_TOKEN missing in .env")
        return

    app = Application.builder().token(config.BOT_TOKEN).build()

    # Core
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))

    # Tool 1: Telegram Scraper
    app.add_handler(CommandHandler("channel_info", channel_info_cmd))
    app.add_handler(CommandHandler("scrape", scrape_cmd))
    app.add_handler(CommandHandler("scrape_search", scrape_search_cmd))
    app.add_handler(CommandHandler("scrape_media", scrape_media_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("batch", batch_cmd))

    # Tool 2: Instagram
    app.add_handler(CommandHandler("insta", insta_cmd))
    app.add_handler(CommandHandler("instagram", insta_cmd))
    app.add_handler(CommandHandler("igsecure", igsecure_cmd))
    app.add_handler(CommandHandler("security", igsecure_cmd))
    app.add_handler(CommandHandler("sec", igsecure_cmd))

    # Tool 3: Email
    app.add_handler(CommandHandler("email", email_cmd))

    # Tool 4: IP & Domain
    app.add_handler(CommandHandler("ip", ip_cmd))
    app.add_handler(CommandHandler("domain", domain_cmd))
    app.add_handler(CommandHandler("dns", dns_cmd))
    app.add_handler(CommandHandler("whois", whois_cmd))
    app.add_handler(CommandHandler("ssl", ssl_cmd))
    app.add_handler(CommandHandler("recon", domain_cmd))

    # Tool 5: EXIF
    app.add_handler(CommandHandler("exif", exif_cmd))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_photo))

    print("🚀 OSINT Hacker Hub Bot started with 5 tools...")
    print(f"Repo: savecontentrestricted-pixel/osint")
    app.run_polling()

if __name__ == "__main__":
    main()
