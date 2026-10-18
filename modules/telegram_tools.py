"""
Telegram Tools - TG Number, Pak Number, etc.
Same gateway as utility bot: utility-api-vu83
"""

import os
import re
import time
import requests
from .fast_cache import with_cache
from typing import Dict, Any

API_URL = os.getenv("MYNUM_API_URL", "https://utility-api-vu83.onrender.com/api")
API_KEY = os.getenv("MYNUM_API_KEY", "")
TIMEOUT = 25

def clean_input(text: str) -> str:
    return str(text or "").strip()

@with_cache("tg3", 300, 2592000)   # v2.5.2: tg2 ke public-card entries orphan (number wapas)
def lookup_tg(username: str) -> Dict[str, Any]:
    """
    Telegram to Number - tool=telegramtonumber or tgnum
    Input: @username or telegram username or phone?
    """
    term = clean_input(username).lstrip('@')
    if not term:
        return {"ok": False, "error": "Username bhejo. Example: @username ya username"}

    # Try both tool names - utility bot uses telegramtonumber and tgnum
    for tool_name in ["telegramtonumber", "tgnum"]:
        try:
            t0 = time.time()
            from .fast_cache import get_session
            r = get_session().get(
                API_URL,
                params={"key": API_KEY, "tool": tool_name, "term": term},
                timeout=TIMEOUT
            )
            ms = int((time.time()-t0)*1000)
            if r.status_code != 200:
                continue
            data = r.json()
            # Parse - similar to other tools
            if not data or not isinstance(data, dict):
                continue
            
            # Check success
            d = data.get("data") or data
            if isinstance(d, dict) and not d:
                continue
            
            # If has error field
            if isinstance(data, dict) and data.get("success") == False:
                continue

            return {"ok": True, "tool": tool_name, "term": term, "data": d, "ms": ms, "raw": data}
        except Exception as e:
            continue

    # v2.5.1 — 18 Oct 2026: number-source PAID ho gaya (403 "CHALO AB BUY KRO"),
    # isliye hub hamesha notfound deta tha aur user ko jhootha "no records"
    # dikhta tha. Ab Telegram ki PUBLIC profile (t.me) se asli kaam hota hai:
    # naam + profile link (~0.5s, free, legal) + honest note ki number-source
    # paid hai. Username exist hi na kare to saaf "username check karo".
    pub = _tme_public(term)
    if pub and pub.get("exists"):
        return {"ok": True, "term": term, "source": "t.me-public",
                "data": {"👤 Naam": pub.get("name") or "",
                         "👤 Username": "@" + term.lstrip("@"),
                         "🔗 Profile": pub.get("url") or "",
                         "⚠️ Number-source": _TME_NOTE},
                "ms": 0}
    if pub is not None and not pub.get("exists"):
        return {"ok": False, "not_found": True,
                "error": f"Telegram @{term.lstrip('@')} ka koi public account nahi mila — username check karo."}
    return {"ok": False, "not_found": True,
            "error": ("🆩 Telegram number-source ab PAID ho gaya hai "
                      "(provider: 'CHALO AB BUY KRO') — aur t.me public profile bhi "
                      "nahi khuli. Thodi der baad dobara try karo.")}


_TME_NOTE = ("Mobile-number database ab PAID ho gaya hai (provider: 'CHALO AB BUY KRO') "
             "- isliye number nahi mil sakta. Upar jo hai wo Telegram ki "
             "PUBLIC profile info hai (t.me se).")


def _tme_public(q: str, tmo: float = 8.0):
    """t.me/<username> public preview: naam + photo + link (free + legal)."""
    import html as _html
    uname = str(q or "").strip().lstrip("@").strip()
    if not uname or not re.match(r"^[A-Za-z0-9_]{3,32}$", uname):
        return None
    try:
        from .fast_cache import get_session
        r = get_session().get(f"https://t.me/{uname}", timeout=tmo,
                              headers={"User-Agent": "Mozilla/5.0"})
    except Exception:                                            # noqa: BLE001
        return None
    if getattr(r, "status_code", 0) != 200:
        return None
    body = r.text or ""
    mt = re.search(r'<meta property="og:title" content="([^"]*)"', body)
    mi = re.search(r'<meta property="og:image" content="([^"]*)"', body)
    title = _html.unescape(mt.group(1)) if mt else ""
    photo = mi.group(1) if mi else ""
    if not title or title.startswith("Telegram: Contact @") or "t_logo" in photo:
        return {"exists": False}
    return {"exists": True, "name": title,
            "photo": ("" if "t_logo" in photo else photo),
            "url": f"https://t.me/{uname}"}

@with_cache("pak", 300, 2592000)
def lookup_pak(cnic_or_number: str) -> Dict[str, Any]:
    term = re.sub(r'\D', '', clean_input(cnic_or_number))
    if len(term) < 10:
        term = clean_input(cnic_or_number)
    if not term:
        return {"ok": False, "error": "CNIC ya Pak number bhejo"}

    try:
        t0 = time.time()
        from .fast_cache import get_session
        r = get_session().get(
            API_URL,
            params={"key": API_KEY, "tool": "paknum", "term": term},
            timeout=TIMEOUT
        )
        ms = int((time.time()-t0)*1000)
        if r.status_code != 200:
            return {"ok": False, "error": f"API HTTP {r.status_code}"}
        data = r.json()
        d = data.get("data") or data
        if not d or (isinstance(d, dict) and not d):
            return {"ok": False, "not_found": True, "error": "❌ No records found for this number in any database."}
        return {"ok": True, "data": d, "ms": ms, "raw": data}
    except Exception as e:
        return {"ok": False, "error": f"Error: {str(e)[:100]}"}

def format_tg_card(result: Dict[str, Any]) -> str:
    if not result.get("ok"):
        return result.get("error", "❌ No records found")

    data = result.get("data", {})
    ms = result.get("ms",0)
    
    # Try to parse common fields
    txt = f"🆔 <b>Telegram OSINT: {result.get('term')}</b>\n\n"
    
    if isinstance(data, dict):
        # Flatten
        for k,v in list(data.items())[:20]:
            if v and str(v).lower() not in ("na","none","null"):
                txt += f"• <b>{k}:</b> {str(v)[:200]}\n"
    else:
        txt += f"{str(data)[:1000]}\n"

    txt += f"\n⚡ Response: {ms}ms"
    return txt

def format_pak_card(result: Dict[str, Any]) -> str:
    if not result.get("ok"):
        return result.get("error", "❌ No records found")
    
    data = result.get("data", {})
    ms = result.get("ms",0)
    txt = f"🇵🇰 <b>Pak Number Info</b>\n\n"
    if isinstance(data, dict):
        for k,v in list(data.items())[:20]:
            if v and str(v).lower() not in ("na","none","null"):
                txt += f"• <b>{k}:</b> {str(v)[:200]}\n"
    else:
        txt += f"{str(data)[:1000]}\n"
    txt += f"\n⚡ Response: {ms}ms"
    return txt
