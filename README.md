# OSINT - Hacker Tools Hub
### by savecontentrestricted-pixel

**Advanced OSINT Tools Collection** 🚀

Ye repo OSINT + Hacker tools ke liye hai. Har tool max data nikalega, lekin sirf public data (ToS ke andar).

> ⚠️ Note: Ye project abhi GitHub pe hi hai, Render pe deploy nahi kiya gaya hai (aapke kehne pe hi karenge). Ye `himanshu75919-coder` wale account me nahi, sirf `savecontentrestricted-pixel` me hai.

---

## 🔥 Available Tools (5 Ready)

### Tool 1: Telegram Channel Scraper (Advanced) ✅
- Public + private (where you are member) channel scraping
- Max data: message text, date, views, forwards, replies, media info, links, hashtags, mentions, reactions
- Export: JSON, CSV, TXT
- Commands: `/channel_info`, `/scrape`, `/scrape_search`, `/scrape_media`, `/stats`, `/batch`

### Tool 2: Instagram OSINT ✅
- Public profile info: followers, following, posts, bio, profile pic, full name
- Uses OG tags + Instaloader fallback
- Command: `/insta @username`

### Tool 3: Email OSINT ✅
- Validation, disposable check, free provider check
- Gravatar existence + hash
- Breach check via xposedornot.com API (HaveIBeenPwned alternative)
- MX records
- Command: `/email test@gmail.com`

### Tool 4: IP & Domain Recon ✅ (NEW)
- **IP Lookup:** location, city, region, country, lat/lon, Google Maps link, ISP, Org, AS, VPN/Proxy detection (ip-api.com free API)
- **DNS Lookup:** A, MX, NS, TXT, CNAME, AAAA records
- **WHOIS:** registrar, creation/expiry date, name servers, status
- **SSL Check:** issuer, subject, valid from/to, SAN, serial
- **Full Recon:** `/domain google.com` gives DNS+WHOIS+SSL+IP in one
- Commands: `/ip 8.8.8.8`, `/domain google.com`, `/dns google.com`, `/whois google.com`, `/ssl google.com`

### Tool 5: Image EXIF Forensics ✅ (NEW)
- Extracts EXIF from photos: camera make/model, lens, software, date/time, exposure, ISO, focal length
- **GPS Location:** If photo has GPS, gives lat/lon + Google Maps + OSM link
- Forensics warnings: edited with Photoshop, screenshot detection, GPS stripped etc
- Must send photo as **File/Document** (not compressed, else Telegram strips EXIF)
- Commands: Send photo as file → auto EXIF, or reply to photo with `/exif`

---

## 📜 All Bot Commands

```
/start - welcome
/help - full guide

# Tool 1
/channel_info @channel
/scrape @channel 100
/scrape_search @channel keyword 100
/scrape_media @channel 50
/stats @channel
/batch @ch1 @ch2 @ch3 30

# Tool 2
/insta @username

# Tool 3
/email test@gmail.com

# Tool 4
/ip 8.8.8.8
/domain google.com
/dns google.com
/whois google.com
/ssl google.com

# Tool 5
Send photo as File → auto EXIF
/exif (reply to photo)
```

---

## ⚙️ Setup

1. `my.telegram.org` se `API_ID`, `API_HASH` lo
2. `.env` banao `.env.example` se
3. `python generate_session.py` se `SESSION_STRING` banao
4. `pip install -r requirements.txt`
5. `python bot.py`

### ENV Example
```
BOT_TOKEN=123456:ABC...
API_ID=1234567
API_HASH=your_api_hash
SESSION_STRING=your_telethon_session_string
ADMIN_ID=your_telegram_id
```

---

## 🚀 Upcoming Tools (Isi repo me ayenge)

- [ ] Tool 6: Website Tech Stack Detector (Wappalyzer style)
- [ ] Tool 7: Link Scanner (VirusTotal + Safe Browsing)
- [ ] Tool 8: Crypto Wallet OSINT (BTC/ETH balance)
- [ ] Tool 9: File Metadata Extractor (PDF/DOCX)
- [ ] Tool 10: Hash Identifier + Decoder Toolkit
- [ ] Tool 11: Password Leak & Strength Checker
- [ ] Tool 12: More...

---

**Legal:** Sirf public data aur jahan aapka access hai wahi scrape karo. Private data, phone numbers, spam ke liye use mat karo. Educational OSINT purpose ke liye hai.
