"""
OSINT - Telegram Channel Scraper Bot (Advanced)
Tool 1 of OSINT Hacker Hub
Repo: savecontentrestricted-pixel/osint

Features:
- /channel_info, /scrape, /scrape_search, /scrape_media, /stats
- Max data extraction
- Export JSON/CSV/TXT
- FloodWait protection

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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global scraper instance
scraper: TelegramScraper = None

def get_scraper() -> TelegramScraper:
    global scraper
    if scraper is None:
        if not config.API_ID or not config.API_HASH or not config.SESSION_STRING:
            raise Exception("API_ID/API_HASH/SESSION_STRING missing in .env")
        scraper = TelegramScraper(config.API_ID, config.API_HASH, config.SESSION_STRING)
    return scraper

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    txt = f"""
🚀 <b>OSINT Hacker Hub - Telegram Scraper (Advanced)</b>
👋 Hello {user.first_name}!

<b>Ye Tool 1 hai is repo ka — Telegram Channel Scraping ka sabse advanced version.</b>

<b>🔥 Kya kar sakta hai?</b>
• Kisi bhi public channel ka pura data nikalna
• 10,000 messages tak ek baar me
• Media, links, hashtags, mentions, views, forwards, reactions sab
• JSON/CSV/TXT/Excel export

<b>📜 Commands:</b>
/channel_info @channel - Channel ka full info (members, description, etc)
/scrape @channel 100 - Last 100 messages scrape
/scrape_search @channel keyword 100 - Channel me keyword search
/scrape_media @channel 50 - Sirf media wale messages
/stats @channel - Top posts + stats
/help - Full guide
/batch @ch1 @ch2 @ch3 - Ek saath 3-5 channels scrape

<b>📌 Example:</b>
<code>/scrape @durov 50</code>
<code>/scrape_search @breakingnews bitcoin 100</code>
<code>/channel_info @osint_xpert</code>

<b>⚠️ Note:</b> Sirf public channels ya jahan aap member ho. Private data scrape mat karo.

<b>Upcoming:</b> Instagram OSINT, Website Recon, Phone OSINT, Email OSINT etc isi repo me ayenge.

Repo: <code>savecontentrestricted-pixel/osint</code>
"""
    kb = [
        [InlineKeyboardButton("📢 Channel", url="https://t.me/osint_xpert"), InlineKeyboardButton("💬 Support", url="https://t.me/Supermannn_x")],
        [InlineKeyboardButton("📜 Help", callback_data="help"), InlineKeyboardButton("🔧 Tools List", callback_data="tools")]
    ]
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = """
<b>📖 OSINT Telegram Scraper - Full Guide</b>

<b>1. /channel_info @username</b>
Channel ka full info: ID, Title, Username, Members count, Online, Verified, Description, Creation date

<b>2. /scrape @channel [limit]</b>
Last N messages scrape karta hai (default 50, max 10000)
Example: <code>/scrape @durov 200</code>
Output: JSON + CSV file + stats summary

<b>3. /scrape_search @channel keyword [limit]</b>
Channel ke andar keyword search
Example: <code>/scrape_search @cryptonews bitcoin 100</code>

<b>4. /scrape_media @channel [limit]</b>
Sirf photo/video/doc wale messages
Example: <code>/scrape_media @movies 50</code>

<b>5. /stats @channel</b>
Channel stats: total scraped, avg views, media ratio, top 10 most viewed posts

<b>6. /batch @ch1 @ch2 @ch3 [limit]</b>
Ek saath multiple channels
Example: <code>/batch @durov @telegram @breaking 30</code>

<b>⚙️ Filters (Advanced):</b>
Bot me code level pe date_from, date_to, min_id, max_id filters bhi hain — modules/telegram_scraper.py me dekho.

<b>📤 Export:</b>
Har scrape ke baad 3 files milti hain:
• JSON (full data with reactions, links etc)
• CSV (Excel me khul jayega)
• TXT (simple readable)

<b>🛡️ Safety:</b>
• FloodWait auto handle
• Har 50 messages pe 0.5s delay
• Batch me har channel ke beech 2s delay
• Max 5 channels ek saath

<b>Setup apne bot ke liye:</b>
1. my.telegram.org se API_ID, API_HASH lo
2. generate_session.py chalao → SESSION_STRING milega
3. .env me daalo aur bot.py chalao

Koi error aaye to /start pe wapas jao ya support pe pucho.
"""
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

async def channel_info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/channel_info @channelusername</code>\nExample: <code>/channel_info @durov</code>", parse_mode=ParseMode.HTML)
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

🔗 <b>Link:</b> https://t.me/{info.get('username')} if info.get('username') else 'Private'
"""
        await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.exception(e)
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def scrape_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/scrape @channel [limit]</code>\nExample: <code>/scrape @durov 100</code>", parse_mode=ParseMode.HTML)
        return

    channel = context.args[0]
    limit = 50
    if len(context.args) > 1:
        try:
            limit = int(context.args[1])
        except:
            limit = 50
    limit = max(1, min(limit, 10000))

    status_msg = await update.message.reply_text(f"⏳ Scraping <code>{channel}</code> — {limit} messages...\nYe 10-60 sec lag sakta hai, wait karo.", parse_mode=ParseMode.HTML)

    try:
        scr = get_scraper()
        result = await scr.scrape_messages(channel, limit=limit)

        if not result.get("ok"):
            await status_msg.edit_text(f"❌ Error: {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        messages = result.get("messages", [])
        stats = result.get("stats", {})

        # Create exports
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, f"{channel.strip('@')}_{limit}.json")
            csv_path = os.path.join(tmpdir, f"{channel.strip('@')}_{limit}.csv")
            txt_path = os.path.join(tmpdir, f"{channel.strip('@')}_{limit}.txt")

            scr.export_json(result, json_path)
            scr.export_csv(messages, csv_path)
            scr.export_txt(messages, txt_path)

            # Summary
            summary = f"""
✅ <b>Scraped {len(messages)} messages from {channel}</b>

📊 <b>Stats:</b>
• Total: {stats.get('total')}
• Total Views: {stats.get('total_views')}
• Avg Views: {stats.get('avg_views')}
• Total Forwards: {stats.get('total_forwards')}
• Media Count: {stats.get('media_count')} ({stats.get('media_ratio')}%)
• Links: {stats.get('link_count')} | Hashtags: {stats.get('hashtag_count')} | Mentions: {stats.get('mention_count')}

🔝 <b>Top 3 Most Viewed:</b>
"""
            top = stats.get('top_posts', [])[:3]
            for i, tp in enumerate(top, 1):
                summary += f"{i}. ID {tp.get('id')} - {tp.get('views')} views - {tp.get('link')}\n"

            if result.get("partial"):
                summary += f"\n⚠️ Partial data - FloodWait {result.get('flood_wait')}s - {result.get('warning')}"

            summary += f"\n📁 Files: JSON (full), CSV (Excel), TXT (readable)"

            await status_msg.edit_text(summary, parse_mode=ParseMode.HTML)

            # Send files
            await update.message.reply_document(document=open(json_path, 'rb'), filename=os.path.basename(json_path), caption="📄 Full JSON data")
            await update.message.reply_document(document=open(csv_path, 'rb'), filename=os.path.basename(csv_path), caption="📊 CSV for Excel")
            # TXT only if small
            if len(messages) <= 200:
                await update.message.reply_document(document=open(txt_path, 'rb'), filename=os.path.basename(txt_path), caption="📝 TXT readable")

    except Exception as e:
        logger.exception(e)
        await status_msg.edit_text(f"❌ Error: {str(e)}\n\nCheck: API_ID/HASH/SESSION valid hai? Channel public hai?", parse_mode=ParseMode.HTML)

async def scrape_search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❌ Use: <code>/scrape_search @channel keyword [limit]</code>\nExample: <code>/scrape_search @durov telegram 50</code>", parse_mode=ParseMode.HTML)
        return

    channel = context.args[0]
    keyword = context.args[1]
    limit = 50
    if len(context.args) > 2:
        try:
            limit = int(context.args[2])
        except:
            pass

    status_msg = await update.message.reply_text(f"🔍 Searching '{keyword}' in {channel} - {limit} results...", parse_mode=ParseMode.HTML)

    try:
        scr = get_scraper()
        result = await scr.scrape_messages(channel, limit=limit, search_query=keyword)
        if not result.get("ok"):
            await status_msg.edit_text(f"❌ Error: {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        messages = result.get("messages", [])
        if not messages:
            await status_msg.edit_text(f"❌ No results for '{keyword}' in {channel}", parse_mode=ParseMode.HTML)
            return

        # Export
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, f"{channel.strip('@')}_search_{keyword}_{limit}.json")
            scr.export_json(result, json_path)

            summary = f"✅ Found {len(messages)} messages for '{keyword}' in {channel}\n\n"
            for m in messages[:10]:
                summary += f"• ID {m['id']} | {m['views']} views | {m['date'][:10]}\n{m['text'][:100]}...\nLink: {m['link']}\n\n"

            await status_msg.edit_text(summary[:4000], parse_mode=ParseMode.HTML)
            await update.message.reply_document(document=open(json_path, 'rb'), filename=os.path.basename(json_path), caption=f"🔍 Search results for {keyword}")

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

    status_msg = await update.message.reply_text(f"🎬 Scraping media only from {channel} - {limit}...", parse_mode=ParseMode.HTML)

    try:
        scr = get_scraper()
        result = await scr.scrape_messages(channel, limit=limit, media_only=True)
        if not result.get("ok"):
            await status_msg.edit_text(f"❌ Error: {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        messages = result.get("messages", [])
        summary = f"✅ Found {len(messages)} media messages in {channel}\n"
        for m in messages[:10]:
            summary += f"• ID {m['id']} | {m.get('media',{}).get('type')} | {m['views']} views | {m['link']}\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, f"{channel.strip('@')}_media_{limit}.json")
            scr.export_json(result, json_path)
            await status_msg.edit_text(summary[:4000], parse_mode=ParseMode.HTML)
            await update.message.reply_document(document=open(json_path, 'rb'), filename=os.path.basename(json_path), caption="🎬 Media only results")

    except Exception as e:
        logger.exception(e)
        await status_msg.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: <code>/stats @channel</code>", parse_mode=ParseMode.HTML)
        return
    channel = context.args[0]
    # Scrape 200 for stats
    status_msg = await update.message.reply_text(f"📊 Calculating stats for {channel} (200 messages sample)...", parse_mode=ParseMode.HTML)

    try:
        scr = get_scraper()
        result = await scr.scrape_messages(channel, limit=200)
        if not result.get("ok"):
            await status_msg.edit_text(f"❌ Error: {result.get('error')}", parse_mode=ParseMode.HTML)
            return

        stats = result.get("stats", {})
        txt = f"""
📊 <b>Stats for {channel}</b> (200 msg sample)

• Total Sampled: {stats.get('total')}
• Total Views: {stats.get('total_views')}
• Avg Views: {stats.get('avg_views')}
• Total Forwards: {stats.get('total_forwards')}
• Media: {stats.get('media_count')} ({stats.get('media_ratio')}%)
• Links: {stats.get('link_count')}
• Hashtags: {stats.get('hashtag_count')}
• Mentions: {stats.get('mention_count')}

🔝 <b>Top 10 Most Viewed Posts:</b>
"""
        for i, tp in enumerate(stats.get('top_posts', [])[:10], 1):
            txt += f"{i}. {tp.get('views')} views - ID {tp.get('id')} - {tp.get('link')}\nText: {tp.get('text','')[:60]}...\n\n"

        await status_msg.edit_text(txt[:4000], parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.exception(e)
        await status_msg.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

async def batch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❌ Use: <code>/batch @ch1 @ch2 @ch3 [limit]</code>\nExample: <code>/batch @durov @telegram 30</code>", parse_mode=ParseMode.HTML)
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

    if not channels:
        await update.message.reply_text("❌ No channels found. Use @username format.", parse_mode=ParseMode.HTML)
        return

    channels = channels[:5]
    status_msg = await update.message.reply_text(f"⏳ Batch scraping {len(channels)} channels - {limit} each...\n{', '.join(channels)}", parse_mode=ParseMode.HTML)

    try:
        scr = get_scraper()
        results = await scr.batch_scrape(channels, limit_per_channel=limit)

        txt = f"✅ Batch done - {len(channels)} channels:\n\n"
        for ch, res in results.items():
            if res.get("ok"):
                txt += f"• {ch}: {res.get('scraped')} msgs, {res.get('stats',{}).get('total_views',0)} views\n"
            else:
                txt += f"• {ch}: ❌ {res.get('error')}\n"

        await status_msg.edit_text(txt, parse_mode=ParseMode.HTML)

        # Send combined JSON
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, f"batch_{limit}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            await update.message.reply_document(document=open(json_path, 'rb'), filename=os.path.basename(json_path), caption="📦 Batch results JSON")

    except Exception as e:
        logger.exception(e)
        await status_msg.edit_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)

def main():
    missing = config.validate()
    if missing:
        print(f"❌ Missing ENV: {', '.join(missing)}")
        print("Check .env.example and generate_session.py")
        return

    app = Application.builder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("channel_info", channel_info_cmd))
    app.add_handler(CommandHandler("scrape", scrape_cmd))
    app.add_handler(CommandHandler("scrape_search", scrape_search_cmd))
    app.add_handler(CommandHandler("scrape_media", scrape_media_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("batch", batch_cmd))

    print("🚀 OSINT Telegram Scraper Bot started...")
    print(f"Repo: savecontentrestricted-pixel/osint")
    print(f"Bot: @{(app.bot.username if hasattr(app.bot, 'username') else 'unknown')}")
    app.run_polling()

if __name__ == "__main__":
    main()
