# OSINT - Hacker Tools Hub
### by savecontentrestricted-pixel

**First Tool: Advanced Telegram Channel Scraper** 🚀

Ye repo OSINT + Hacker tools ke liye hai. Pehla tool Telegram Channel Scraping ka sabse advanced version hai — jitna zyada data ho sake utna nikalega, lekin sirf public data (Telegram ToS ke andar).

> ⚠️ Note: Ye project abhi GitHub pe hi hai, Render pe deploy nahi kiya gaya hai (aapke kehne pe hi karenge). Ye `himanshu75919-coder` wale account me nahi, sirf `savecontentrestricted-pixel` me hai.

---

## 🔥 Tool 1: Telegram Channel Scraper (Advanced)

### Kya karta hai?
- Kisi bhi **public channel** ka pura data scrape karta hai
- Private channel jahan aap member ho, uska bhi data (aapke session se)
- Max data: message text, date, views, forwards, replies, media info, links, hashtags, mentions, reactions, etc.
- Export: JSON, CSV, TXT, Excel

### Features (Advanced)
- ✅ Channel Info: title, username, participants count, creation date, description
- ✅ Message Scraping: limit 1-10000, offset ID, date range filter
- ✅ Media Only Scraping: sirf photos/videos/docs
- ✅ Keyword Search: channel ke andar keyword search
- ✅ Stats: total messages, avg views, top 10 most viewed posts, media ratio
- ✅ Batch Mode: ek saath 5 channels
- ✅ FloodWait handling + rate limit (Telegram ban se bachao)
- ✅ JSON/CSV/Excel export + Telegram file ke roop me bhejta hai

### Bot Commands
```
/start - welcome + help
/channel_info @channel - channel ka full info
/scrape @channel 100 - last 100 messages scrape
/scrape_search @channel keyword 100 - keyword search
/scrape_media @channel 50 - sirf media wale messages
/stats @channel - channel stats + top posts
/help - full guide
```

### Setup (Local)
1. my.telegram.org se API_ID, API_HASH lo
2. `.env` banao `.env.example` se
3. `python generate_session.py` se SESSION_STRING banao (ek baar phone login)
4. `pip install -r requirements.txt`
5. `python bot.py` — bot chalu

### ENV Example
```
BOT_TOKEN=123456:ABC...
API_ID=1234567
API_HASH=your_api_hash
SESSION_STRING=your_telethon_session_string
ADMIN_ID=your_telegram_id
```

### Upcoming Tools (Isi repo me ayenge)
- [ ] Tool 2: Instagram OSINT Scraper
- [ ] Tool 3: Website OSINT + Subdomain Finder
- [ ] Tool 4: Phone Number OSINT (public data only)
- [ ] Tool 5: Email + Username OSINT
- [ ] Tool 6: IP + Domain Recon
- [ ] Tool 7: Dark Web Search (Tor)
- [ ] Tool 8: More...

---

**Legal:** Sirf public data aur jahan aapka access hai wahi scrape karo. Private data, phone numbers, spam ke liye use mat karo. Educational OSINT purpose ke liye hai.
