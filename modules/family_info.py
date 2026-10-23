"""
👪 FAMILY INFO - BEST - OSINT Hunter Hub
API: utility-api-vu83 + supabase fallback
Aadhaar → Ration Card + Family Members
"""

import os
import re
import time
import requests
from .fast_cache import get_session, api_cache_get, api_cache_set

API_URL = os.getenv("FAMINFO_API_URL", "https://utility-api-vu83.onrender.com/api").strip()
API_KEY = os.getenv("FAMINFO_API_KEY", "").strip()
TIMEOUT = int(os.getenv("FAMINFO_API_TIMEOUT", "25") or 25)  # Reduced for speed

BUILTIN_URL = "https://jgvicvhgfwcfndgookul.supabase.co/functions/v1/bot-api"
BUILTIN_KEY = "Demo"

NUM_RE = re.compile(r"\D")

def _clean_aadhaar(aadhaar: str) -> str:
    digits = NUM_RE.sub("", str(aadhaar))
    return digits

def _mask_aadhaar(aadhaar: str) -> str:
    d = _clean_aadhaar(aadhaar)
    if len(d) == 12:
        return f"XXXX-XXXX-{d[-4:]}"
    return "XXXX-XXXX-XXXX"

def _normalize_ration(d: dict) -> dict:
    """v2.8: sarkari ?=ration data -> format_family_card ka contract.
    Khaali/fake aadhaar (sab N/A + 0 members) par {} (not found)."""
    def clean(v):
        s = str(v or "").strip()
        return "" if s.lower() in ("n/a", "na", "none", "null", "-", "0") else s
    out = {}
    card = clean(d.get("ration_card_number"))
    scheme = clean(d.get("scheme"))
    st = clean(d.get("state"))
    dist = clean(d.get("district"))
    fps = clean(d.get("fps_id"))
    sd = " / ".join(x for x in (st, dist) if x)
    try:
        tm = int(d.get("total_members") or 0)
    except Exception:
        tm = 0
    names = []
    mem = d.get("members")
    if isinstance(mem, list):
        for m in mem:
            if isinstance(m, dict):
                nm = clean(m.get("name") or m.get("member_name") or m.get("full_name") or m.get("member_name_english"))
            else:
                nm = clean(m)
            if nm and nm not in names:
                names.append(nm)
    head = clean(d.get("head_of_family"))
    if head and head not in names:
        names.insert(0, head)
    # fake aadhaar = members empty + state/district/fps sab N/A
    if not names and tm <= 0 and not sd and not fps:
        return {}
    if card:
        out["card_number"] = card
    if scheme:
        out["card_type"] = scheme
    if sd:
        out["state_dist"] = sd
    if fps:
        out["fps_id"] = fps
    if names:
        out["name"] = names[0]
        for i, nm in enumerate(names[1:9], 1):
            out[f"name_{i}"] = nm
    out["family_count"] = tm if tm > 0 else len(names)
    return out

def lookup_family(aadhaar: str) -> dict:
    start = time.time()
    aadhaar_clean = _clean_aadhaar(aadhaar)
    
    if len(aadhaar_clean) != 12:
        return {
            "ok": False,
            "error": "Aadhaar must be 12 digits",
            "masked": _mask_aadhaar(aadhaar),
            "ms": int((time.time() - start) * 1000)
        }
    
    # Cache check - ULTRA FAST
    cached = api_cache_get("family", aadhaar_clean)
    if cached:
        cached = cached.copy()
        cached["ms"] = 0
        cached["cached"] = True
        return cached
    
    masked = _mask_aadhaar(aadhaar_clean)
    
    # Try primary API with session pooling
    try:
        session = get_session()
        params = {
            "key": API_KEY,
            "tool": "familyinfo",
            "term": aadhaar_clean
        }
        resp = session.get(API_URL, params=params, timeout=TIMEOUT)
        if resp.status_code == 200:
            try:
                data = resp.json()
                # Check if data has family info
                if data.get("success") and data.get("data"):
                    d = data["data"]
                    # Check if not found
                    if "family_info_not_found" in str(d).lower() or "not_found" in str(d).lower():
                        # Try raw field
                        raw = data.get("raw", "")
                        if "not found" in raw.lower():
                            return {
                                "ok": False,
                                "error": "No family data found",
                                "masked": masked,
                                "ms": int((time.time() - start) * 1000),
                                "raw": data
                            }
                    # Found data
                    result = {
                        "ok": True,
                        "data": d,
                        "masked": masked,
                        "ms": int((time.time() - start) * 1000),
                        "source": "utility-api"
                    }
                    api_cache_set("family", aadhaar_clean, result, ttl=3600)
                    return result
                else:
                    if isinstance(data, dict) and data.get("data"):
                        result = {
                            "ok": True,
                            "data": data["data"],
                            "masked": masked,
                            "ms": int((time.time() - start) * 1000),
                            "source": "utility-api"
                        }
                        api_cache_set("family", aadhaar_clean, result, ttl=3600)
                        return result
            except Exception as e:
                print(f"Family primary JSON parse error: {e}")
                pass
        # Cache not found? Try parsing anyway
        try:
            data = resp.json()
            if isinstance(data, dict) and data.get("data"):
                result = {
                    "ok": True,
                    "data": data["data"],
                    "masked": masked,
                    "ms": int((time.time() - start) * 1000),
                    "source": "utility-api"
                }
                api_cache_set("family", aadhaar_clean, result, ttl=3600)
                return result
        except:
            pass
    except Exception as e:
        print(f"Family primary API error: {e}")
    
    # v2.8: purana supabase fallback BAND (host NXDOMAIN/mar chuka) → sarkari ?=ration direct
    try:
        session = get_session()
        url = (f"https://api.sarkariallupdates.com/api?=ration&key=30day"
               f"&q={aadhaar_clean}&xr={aadhaar_clean}&term={aadhaar_clean}")
        resp = session.get(url, timeout=20)
        if resp.status_code == 200:
            j = resp.json()
            d0 = j.get("data") if isinstance(j, dict) else None
            if isinstance(j, dict) and j.get("status") and isinstance(d0, dict) and d0:
                out = _normalize_ration(d0)
                if out:
                    result = {
                        "ok": True,
                        "data": out,
                        "masked": masked,
                        "ms": int((time.time() - start) * 1000),
                        "source": "sarkari-api"
                    }
                    api_cache_set("family", aadhaar_clean, result, ttl=3600)
                    return result
    except Exception as e:
        print(f"Family sarkari fallback error: {e}")
    
    return {
        "ok": False,
        "error": "No data found or API down",
        "masked": masked,
        "ms": int((time.time() - start) * 1000)
    }

def format_family_card(result: dict) -> str:
    """Format family info card - BEST"""
    import html
    
    if not result.get("ok"):
        masked = result.get("masked", "XXXX-XXXX-XXXX")
        return f"""
╔══════════════════════════════════════╗
║  👪 <b>FAMILY INFO - No Data</b>        ║
╚══════════════════════════════════════╝

🔒 <b>Aadhaar:</b> <code>{html.escape(masked)}</code>

❌ No records found for this Aadhaar in any database.

📭 Database me iska koi record nahi hai.

⏱️ Response: {result.get('ms',0)}ms
🔥 @ANONYMOUS_XH | 📢 @osint_xpert
"""
    
    data = result.get("data", {})
    masked = result.get("masked", "XXXX-XXXX-XXXX")
    ms = result.get("ms", 0)
    source = result.get("source", "api")
    
    # Extract fields
    card_number = data.get("card_number") or data.get("rc_number") or data.get("ration_card") or ""
    card_type = data.get("card_type") or data.get("cardtype") or ""
    state_dist = data.get("statedist") or data.get("state_dist") or data.get("district") or ""
    fps_id = data.get("fps_id") or ""
    fps_name = data.get("fps_name") or data.get("fps") or ""
    family_count = data.get("family_count") or data.get("members") or ""
    full_address = data.get("full_address") or data.get("address") or ""
    ekyc = data.get("ekyc_status") or data.get("ekyc") or ""
    
    # Members - name, name_, name__, etc
    members = []
    for k in sorted(data.keys()):
        if k.startswith("name"):
            v = data.get(k)
            if v and str(v).strip() and str(v).lower() not in ["", "na", "n/a", "none"]:
                # Avoid duplicates
                if str(v).strip() not in members:
                    members.append(str(v).strip())
    
    # Also check member_id pattern
    if not members and data.get("name"):
        members = [str(data.get("name")).strip()]
    
    txt = f"""
╔══════════════════════════════════════╗
║  👪 <b>FAMILY INFO - Ration Card</b>    ║
╚══════════════════════════════════════╝

🔒 <b>Aadhaar:</b> <code>{html.escape(masked)}</code>

"""
    
    if card_number:
        txt += f"💳 <b>Ration Card No:</b> <code>{html.escape(str(card_number)[:30])}</code>\n\n"
    
    if card_type:
        txt += f"📋 <b>Card Type:</b> {html.escape(str(card_type))}\n\n"
    
    if state_dist:
        txt += f"🌍 <b>State/District:</b> {html.escape(str(state_dist)[:100])}\n\n"
    
    if fps_id or fps_name:
        txt += f"🏪 <b>FPS Shop:</b>\n"
        if fps_id:
            txt += f"   ID: <code>{html.escape(str(fps_id)[:20])}</code>\n"
        if fps_name:
            txt += f"   Name: {html.escape(str(fps_name)[:80])}\n"
        txt += "\n"
    
    if family_count:
        txt += f"👥 <b>Family Members:</b> {html.escape(str(family_count))}\n\n"
    
    if full_address:
        txt += f"🏠 <b>Address:</b>\n{html.escape(str(full_address)[:300])}\n\n"
    
    if members:
        txt += f"👨‍👩‍👧‍👦 <b>Members ({len(members)}):</b>\n"
        for i, m in enumerate(members[:10], 1):
            txt += f"   {i}. {html.escape(m[:60])}\n"
        txt += "\n"
    
    if ekyc:
        txt += f"✅ <b>eKYC:</b> {html.escape(str(ekyc)[:50])}\n\n"
    
    txt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📡 <b>Source:</b> {html.escape(source)}
⚡ <b>Response:</b> {ms}ms
🔒 <b>Privacy:</b> Full Aadhaar never shown, only {html.escape(masked)}

🔥 <b>Powered by @ANONYMOUS_XH</b>
"""
    
    return txt
