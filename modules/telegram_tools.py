"""
Telegram Tools - TG Number, Pak Number, etc.
Same gateway as utility bot: utility-api-vu83
"""

import os
import re
import time
import requests
from typing import Dict, Any

API_URL = os.getenv("MYNUM_API_URL", "https://utility-api-vu83.onrender.com/api")
API_KEY = os.getenv("MYNUM_API_KEY", "")
TIMEOUT = 40

def clean_input(text: str) -> str:
    return str(text or "").strip()

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
            r = requests.get(
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

    return {"ok": False, "error": "❌ No records found for this username in any database."}

def lookup_pak(cnic_or_number: str) -> Dict[str, Any]:
    term = re.sub(r'\D', '', clean_input(cnic_or_number))
    if len(term) < 10:
        term = clean_input(cnic_or_number)
    if not term:
        return {"ok": False, "error": "CNIC ya Pak number bhejo"}

    try:
        t0 = time.time()
        r = requests.get(
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
            return {"ok": False, "error": "❌ No records found for this number in any database."}
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
