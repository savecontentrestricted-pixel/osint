import os
from dotenv import load_dotenv

load_dotenv()

# Bot Token - Provided by user: @osint_hunter_hub_bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "8877252485:AAFA17x1puWA_maPksJs3RWaPIySmlxpTUg").strip()

# Telegram API - my.telegram.org
API_ID = int(os.getenv("API_ID", "0") or 0)
API_HASH = os.getenv("API_HASH", "").strip()
SESSION_STRING = os.getenv("SESSION_STRING", "").strip()

# Owner - Provided
ADMIN_ID = int(os.getenv("ADMIN_ID", "8607774564") or 8607774564)

ADMINS = [8607774564]
_admins_raw = os.getenv("ADMINS", "").strip()
if _admins_raw:
    for x in _admins_raw.split(","):
        try:
            adm = int(x.strip())
            if adm not in ADMINS:
                ADMINS.append(adm)
        except:
            pass

# Force Join - Provided
FORCE_CHANNEL = os.getenv("FORCE_CHANNEL", "-1004393596502").strip()
FORCE_CHANNEL_LINK = os.getenv("FORCE_CHANNEL_LINK", "https://t.me/osint_xpert").strip()
FORCE_CHANNEL_USERNAME = os.getenv("FORCE_CHANNEL_USERNAME", "osint_xpert").strip()

OWNER_USERNAME = os.getenv("OWNER_USERNAME", "@Supermannn_x").strip()
BRAND_TAG = os.getenv("BRAND_TAG", "@Supermannn_x").strip()

# APIs
MYNUM_API_URL = os.getenv("MYNUM_API_URL", "https://utility-api-vu83.onrender.com/api").strip()
MYNUM_API_KEY = os.getenv("MYNUM_API_KEY", "udb-SlhpCRCaziEfxTPvasAUHNFCPa9CYw6smolrP0QX").strip()

def is_admin(uid: int) -> bool:
    return uid in ADMINS

def validate():
    missing = []
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    # Telegram scraper needs these, but other tools work without
    if not API_ID:
        missing.append("API_ID (for Telegram scraper)")
    if not API_HASH:
        missing.append("API_HASH (for Telegram scraper)")
    if not SESSION_STRING:
        missing.append("SESSION_STRING (for Telegram scraper - generate_session.py)")
    return missing
