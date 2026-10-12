import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
API_ID = int(os.getenv("API_ID", "0") or 0)
API_HASH = os.getenv("API_HASH", "").strip()
SESSION_STRING = os.getenv("SESSION_STRING", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0") or 0)

ADMINS = []
_admins_raw = os.getenv("ADMINS", "").strip()
if _admins_raw:
    for x in _admins_raw.split(","):
        try:
            ADMINS.append(int(x.strip()))
        except:
            pass

if ADMIN_ID and ADMIN_ID not in ADMINS:
    ADMINS.append(ADMIN_ID)

FORCE_CHANNEL = os.getenv("FORCE_CHANNEL", "").strip()
FORCE_CHANNEL_LINK = os.getenv("FORCE_CHANNEL_LINK", "").strip()

def is_admin(uid: int) -> bool:
    return uid in ADMINS if ADMINS else True

def validate():
    missing = []
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not API_ID:
        missing.append("API_ID")
    if not API_HASH:
        missing.append("API_HASH")
    if not SESSION_STRING:
        missing.append("SESSION_STRING (generate_session.py chalao)")
    return missing
