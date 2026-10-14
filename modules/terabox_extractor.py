"""
TeraBox Extractor - Pro Tool
Combines 4 upstream TeraBox APIs with fallback
Live status:
- v1 stream (terabox-stream): LIVE ✅ - returns download + stream m3u8 + thumbnail
- v2 stream (terabox-stream-v2): DEAD ❌ - Guest limit reached 429
- v3 stream (terabox-stream-v3): DEAD ❌ - 502 Bad Gateway
- file (terabox-file): LIVE ✅ - returns download only, 109GB file test OK

Upstream base: https://osint-apis-hub.onrender.com
"""

import requests
from .fast_cache import with_cache
import time

# Upstream APIs - in order of preference
UPSTREAM_APIS = [
    {
        "name": "terabox-stream-v1",
        "url": "https://osint-apis-hub.onrender.com/api/terabox-stream",
        "key": "1week",
        "status": "LIVE",
        "features": ["download", "stream_m3u8", "thumbnail", "size"]
    },
    {
        "name": "terabox-file",
        "url": "https://osint-apis-hub.onrender.com/api/terabox-file",
        "key": "1week",
        "status": "LIVE",
        "features": ["download", "size"]
    },
    {
        "name": "terabox-stream-v2",
        "url": "https://osint-apis-hub.onrender.com/api/terabox-stream-v2",
        "key": "1week",
        "status": "DEAD - 429 limit",
        "features": ["download", "stream"]
    },
    {
        "name": "terabox-stream-v3",
        "url": "https://osint-apis-hub.onrender.com/api/terabox-stream-v3",
        "key": "1week",
        "status": "DEAD - 502",
        "features": ["download", "stream"]
    },
]

@with_cache("tbx", 600, 3600)
def extract_terabox(url, custom_key=None, timeout=90):
    """
    Extract TeraBox file info using upstream APIs with fallback
    Returns unified format
    """
    result = {
        "ok": False,
        "url": url,
        "files": [],
        "source": None,
        "error": None,
        "attempts": []
    }
    
    # Try each upstream in order
    for api in UPSTREAM_APIS:
        attempt = {
            "api": api["name"],
            "status": "trying",
            "code": None,
            "error": None
        }
        try:
            # Build request URL
            req_url = f"{api['url']}?key={custom_key or api['key']}&url={url}"
            r = requests.get(req_url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
            attempt["code"] = r.status_code
            
            if r.status_code == 200:
                try:
                    data = r.json()
                    # Check if response has files
                    if data.get("status") == True or data.get("code") == 200:
                        files = data.get("files", [])
                        if files:
                            # Normalize files
                            normalized = []
                            for f in files:
                                normalized.append({
                                    "name": f.get("name",""),
                                    "download_url": f.get("download_url",""),
                                    "stream_url": f.get("stream_url",""),
                                    "thumbnail": f.get("thumbnail",""),
                                    "size": f.get("size",""),
                                    "size_bytes": f.get("size_bytes",0),
                                    "fs_id": f.get("fs_id",""),
                                })
                            result["files"] = normalized
                            result["ok"] = True
                            result["source"] = api["name"]
                            attempt["status"] = "success"
                            result["attempts"].append(attempt)
                            return result
                        else:
                            attempt["status"] = "no files"
                            attempt["error"] = "No files in response"
                    else:
                        attempt["status"] = "api error"
                        attempt["error"] = str(data)[:300]
                except Exception as e:
                    attempt["status"] = "parse error"
                    attempt["error"] = str(e)[:300]
            else:
                attempt["status"] = f"http {r.status_code}"
                attempt["error"] = r.text[:500]
                
        except Exception as e:
            attempt["status"] = "exception"
            attempt["error"] = str(e)[:500]
        
        result["attempts"].append(attempt)
        # Small delay before next attempt
        time.sleep(1)
    
    # All failed
    result["error"] = "All upstreams failed"
    return result

def create_own_api_wrapper():
    """
    Creates own API that wraps upstream APIs
    This is what user wants - apna API jaise utility-duniya-bot me banate the
    """
    # This will be implemented as a FastAPI/Flask server in terabox-api/
    # For now, return the logic
    code = '''
# Own TeraBox API - Combination of 4 upstreams
# File: terabox-api/server.py
# Deploy on Render: https://terabox-api-xxxx.onrender.com

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

UPSTREAMS = [
    "https://osint-apis-hub.onrender.com/api/terabox-stream",
    "https://osint-apis-hub.onrender.com/api/terabox-file",
    # Add more as fallback
]

MY_KEYS = {
    "1week": {"limit": 1000, "owner": "demo"},
    "YOUR_OWN_KEY": {"limit": 10000, "owner": "himanshu"},
    # User can add own keys
}

@app.route('/api/terabox')
def terabox_api():
    key = request.args.get('key','')
    url = request.args.get('url','')
    
    if key not in MY_KEYS:
        return jsonify({"ok": False, "error": "Invalid key"}), 403
    if not url:
        return jsonify({"ok": False, "error": "Missing url param"}), 400
    if "terabox.com" not in url and "1024terabox.com" not in url:
        return jsonify({"ok": False, "error": "Only terabox.com URLs"}), 400
    
    # Try upstreams
    for upstream in UPSTREAMS:
        try:
            r = requests.get(f"{upstream}?key=1week&url={url}", timeout=60)
            if r.status_code == 200:
                data = r.json()
                if data.get("files"):
                    # Add your branding
                    data["powered_by"] = "@Supermannn_x"
                    data["your_api"] = "https://your-terabox-api.onrender.com"
                    return jsonify(data)
        except:
            continue
    
    return jsonify({"ok": False, "error": "All upstreams failed"}), 502

@app.route('/health')
def health():
    return jsonify({"status": "active", "tools": ["terabox"]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
'''
    return code

def format_terabox_report(result):
    """Format as beautiful Telegram message"""
    if not result.get("ok"):
        txt = f"❌ <b>TeraBox Extract Failed</b>\n\n"
        txt += f"🌐 URL: <code>{result.get('url','')[:80]}</code>\n\n"
        txt += f"🔍 Attempts:\n"
        for att in result.get("attempts", [])[:4]:
            txt += f"• {att['api']}: {att['status']} (code {att.get('code')})\n"
            if att.get("error"):
                txt += f"  Error: {att['error'][:100]}\n"
        txt += f"\n💡 Tip: TeraBox link sahi hai? Key 1week expire hua kya? Try again in 5 min (Render wake up time)\n"
        txt += f"\n🔥 @Supermannn_x"
        return txt
    
    url = result.get("url")
    files = result.get("files", [])
    source = result.get("source")
    
    txt = f"""
╔══════════════════════════════════════╗
║  ☁️ <b>TERABOX EXTRACTOR - PRO</b>       ║
╚══════════════════════════════════════╝

🌐 <b>Original URL:</b>
<code>{url[:80]}</code>

📡 <b>Source:</b> {source} ✅ LIVE

📁 <b>Files Found:</b> {len(files)}

━━━━━━━━━━━━━━━━━━━━━━

"""
    for i, f in enumerate(files[:5], 1):
        txt += f"<b>{i}. {f.get('name','File')}</b>\n"
        txt += f"   📦 Size: {f.get('size','N/A')}\n"
        if f.get('download_url'):
            txt += f"   📥 <a href=\"{f.get('download_url')}\">Download Link</a>\n"
        if f.get('stream_url'):
            txt += f"   ▶️ <a href=\"{f.get('stream_url')}\">Stream (m3u8)</a>\n"
        txt += f"\n"
    
    txt += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    txt += f"⚡ <b>How to Use:</b>\n"
    txt += f"• Download Link pe click karo → direct download\n"
    txt += f"• Stream Link → VLC / MX Player me chalao\n\n"
    txt += f"🔥 Powered by @Supermannn_x\n"
    txt += f"🔗 Your API: /api/terabox?key=YOUR_KEY&url=TERABOX_URL\n"
    
    return txt

if __name__ == "__main__":
    # Test
    test_url = "https://1024terabox.com/s/1EqwgqQWgmeOvQxc33258UA"
    res = extract_terabox(test_url)
    print(format_terabox_report(res))
