"""
💸 UPI INFO - BEST - OSINT Hunter Hub
API: utility-api-vu83 - lynxosint__upi / upi
UPI ID → Name + Bank + Valid + App
Your API key: udb-SlhpCRCaziEfxTPvasAUHNFCPa9CYw6smolrP0QX
Tested: kumaranil98787@axl → ANIL KUMAR, Axis Bank, PhonePe, SAVINGS, valid true
"""

import os
import re
import time
import requests

API_URL = os.getenv("UPIINFO_API_URL", "https://utility-api-vu83.onrender.com/api").strip()
API_KEY = os.getenv("UPIINFO_API_KEY", "udb-SlhpCRCaziEfxTPvasAUHNFCPa9CYw6smolrP0QX").strip()
TIMEOUT = int(os.getenv("UPIINFO_API_TIMEOUT", "30") or 30)

# Also support generic MYNUM API env
if not API_URL:
    API_URL = os.getenv("MYNUM_API_URL", "https://utility-api-vu83.onrender.com/api").strip()
if not API_KEY:
    API_KEY = os.getenv("MYNUM_API_KEY", "udb-SlhpCRCaziEfxTPvasAUHNFCPa9CYw6smolrP0QX").strip()

def lookup_upi(upi_id: str) -> dict:
    """
    Lookup UPI info
    Returns dict with ok, data, etc
    """
    start = time.time()
    upi_id = str(upi_id).strip()
    
    if not upi_id or "@" not in upi_id:
        return {
            "ok": False,
            "error": "Invalid UPI ID format. Must contain @, e.g., name@okaxis",
            "ms": int((time.time() - start) * 1000)
        }
    
    # Try tool names
    for tool in ["lynxosint__upi", "upi"]:
        try:
            params = {
                "key": API_KEY,
                "tool": tool,
                "term": upi_id
            }
            resp = requests.get(API_URL, params=params, timeout=TIMEOUT)
            if resp.status_code == 200:
                try:
                    j = resp.json()
                    # Check if ok true and has data with success
                    if j.get("ok") and j.get("data"):
                        data = j["data"]
                        if isinstance(data, dict) and data.get("success"):
                            return {
                                "ok": True,
                                "data": data,
                                "raw": j.get("raw", ""),
                                "ms": j.get("ms", int((time.time() - start) * 1000)),
                                "source": "utility-api",
                                "tool": tool
                            }
                        # Also check if data itself is success false? Then not found
                    # If ok false and why notfound, return no data
                    if not j.get("ok") and j.get("why") == "notfound":
                        return {
                            "ok": False,
                            "error": "No UPI data found or invalid UPI",
                            "raw": j.get("raw", ""),
                            "ms": j.get("ms", int((time.time() - start) * 1000))
                        }
                except Exception as e:
                    print(f"UPI {tool} JSON error: {e}")
                    continue
        except Exception as e:
            print(f"UPI {tool} API error: {e}")
            continue
    
    return {
        "ok": False,
        "error": "No data found or API down",
        "ms": int((time.time() - start) * 1000)
    }

def format_upi_card(result: dict) -> str:
    """Format UPI card - BEST"""
    import html
    
    if not result.get("ok"):
        return f"""
╔══════════════════════════════════════╗
║  💸 <b>UPI INFO - No Data</b>           ║
╚══════════════════════════════════════╝

❌ {html.escape(result.get('error','No data found'))}

📭 Database me iska koi record nahi hai ya invalid UPI.

💡 Valid UPI: <code>name@okaxis</code>, <code>name@okicici</code>, <code>name@ybl</code>

⏱️ Response: {result.get('ms',0)}ms
🔥 Powered by @Supermannn_x
"""
    
    data = result.get("data", {})
    ms = result.get("ms", 0)
    source = result.get("source", "utility-api")
    
    upi_id = data.get("upi_id") or ""
    name = data.get("name") or ""
    username = data.get("username") or ""
    handle = data.get("handle") or ""
    valid = data.get("valid")
    account_type = data.get("account_type") or ""
    bank = data.get("bank") or ""
    bank_id = data.get("bank_id") or ""
    app = data.get("app") or ""
    handle_bank = data.get("handle_bank") or ""
    
    txt = f"""
╔══════════════════════════════════════╗
║  💸 <b>UPI INFO - Verified</b>          ║
╚══════════════════════════════════════╝

💳 <b>UPI ID:</b> <code>{html.escape(str(upi_id)[:60])}</code>

"""
    
    if name:
        txt += f"👤 <b>Name:</b> {html.escape(str(name)[:80])}\n\n"
    
    if username:
        txt += f"🆔 <b>Username:</b> <code>{html.escape(str(username)[:40])}</code>\n\n"
    
    if handle:
        txt += f"🔗 <b>Handle:</b> <code>{html.escape(str(handle)[:20])}</code>\n\n"
    
    if valid is not None:
        valid_str = "✅ Valid" if valid else "❌ Invalid"
        txt += f"✅ <b>Status:</b> {valid_str}\n\n"
    
    if account_type:
        txt += f"🏦 <b>Account Type:</b> {html.escape(str(account_type))}\n\n"
    
    if bank:
        txt += f"🏛️ <b>Bank:</b> {html.escape(str(bank)[:80])}\n\n"
    
    if handle_bank and handle_bank != bank:
        txt += f"🏦 <b>Handle Bank:</b> {html.escape(str(handle_bank)[:80])}\n\n"
    
    if app:
        txt += f"📱 <b>App:</b> {html.escape(str(app)[:40])}\n\n"
    
    if bank_id:
        txt += f"🆔 <b>Bank ID:</b> <code>{html.escape(str(bank_id)[:60])}</code>\n\n"
    
    txt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📡 <b>Source:</b> {html.escape(source)}
⚡ <b>Response:</b> {ms}ms
🔒 <b>Note:</b> UPI info from bank verification

🔥 <b>Powered by @Supermannn_x</b>
"""
    
    return txt
