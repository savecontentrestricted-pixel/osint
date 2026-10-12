# OSINT - Hacker Tools Hub
### by savecontentrestricted-pixel

**Advanced OSINT Tools Collection** 🚀 - 8 Tools Ready

Ye repo OSINT + Hacker tools ke liye hai. Har tool max data nikalega, lekin sirf public data.

> ⚠️ Note: Ye project abhi GitHub pe hi hai, Render pe deploy nahi kiya gaya hai. Ye `himanshu75919-coder` me nahi, sirf `savecontentrestricted-pixel` me hai.

---

## 🔥 Available Tools (8 Ready)

### Tool 1: Telegram Channel Scraper (Advanced) ✅
- Public + private channel scraping
- Max data: message text, date, views, forwards, replies, media info, links, hashtags, mentions, reactions
- Commands: `/channel_info`, `/scrape`, `/scrape_search`, `/scrape_media`, `/stats`, `/batch`

### Tool 2: Instagram OSINT ✅
- Public profile info: followers, following, posts, bio, profile pic
- Command: `/insta @username`

### Tool 3: Email OSINT ✅
- Validation, disposable, Gravatar, breach check, MX records
- Command: `/email test@gmail.com`

### Tool 4: IP & Domain Recon ✅
- IP lookup + VPN detection + Maps, DNS, WHOIS, SSL
- Commands: `/ip 8.8.8.8`, `/domain google.com`, `/dns`, `/whois`, `/ssl`

### Tool 5: Image EXIF Forensics ✅
- GPS + Camera + Date + Editing detection
- Send photo as File → auto EXIF

### Tool 6: Social Media Security Checker ✅ (Educational)
- Email/phone leak in bio, suspicious links, username risk, security score 0-100
- Commands: `/igsecure @username`, `/security`, `/sec`

### Tool 7: Number Info (Same as utility-duniya-bot) ✅ NEW
- Same API as utility-duniya-bot: `utility-api-vu83`
- 10-digit Indian number se owner name, father, address, circle, aadhaar masked, alt phone
- No data pe sirf `❌ No records found for this number in any database.` (aapke kehne pe)
- Commands: `/numinfo 9876543210`, `/number`, `/num`
- Example: `/numinfo 9204507743`

### Tool 8: Telegram Tools (TG Number + Pak Number) ✅ NEW
- Telegram username se number/info lookup (tool=telegramtonumber)
- Pak number/CNIC lookup
- Commands: `/tginfo @username`, `/tgnum @username`, `/paknum 03001234567`

---

## 📜 All Commands

```
/start, /help

# Telegram Scraper
/channel_info @channel
/scrape @channel 100
/scrape_search @channel keyword 100
/scrape_media @channel 50
/stats @channel
/batch @ch1 @ch2 30

# Instagram + Security
/insta @username
/igsecure @username
/security @username

# Email
/email test@gmail.com

# IP/Domain
/ip 8.8.8.8
/domain google.com
/dns google.com
/whois google.com
/ssl google.com

# EXIF
Send photo as File → auto
/exif (reply to photo)

# Number Info (NEW - Same as utility bot)
/numinfo 9876543210
/number 9876543210
/num 9876543210

# TG Tools (NEW)
/tginfo @username
/tgnum @username
/paknum 03001234567
```

---

## ⚙️ Setup

1. my.telegram.org se API_ID, API_HASH lo
2. .env banao .env.example se
3. generate_session.py se SESSION_STRING banao
4. pip install -r requirements.txt
5. python bot.py

ENV:
```
BOT_TOKEN=...
API_ID=...
API_HASH=...
SESSION_STRING=...
ADMIN_ID=...
MYNUM_API_URL=https://utility-api-vu83.onrender.com/api
MYNUM_API_KEY=udb-SlhpCRCaziEfxTPvasAUHNFCPa9CYw6smolrP0QX
```

---

## Free Hosting (No Card) - Pella.app

Aapke paas UPI/Card nahi hai to Pella.app best hai - No card, 1-click, free forever. Guide: PELLA-DEPLOY-GUIDE.md

---

## Upcoming

- [ ] Tool 9: AI Background Remover
- [ ] Tool 10: File Converter Hub
- [ ] Tool 11: UPI QR Generator
- [ ] More...

Legal: Sirf public data, educational purpose.
