"""
TeraBox API Hub - Own API (Combination of 4 upstreams)
Like utility-duniya-bot API pattern

Deploy on Render: terabox-api-hub.onrender.com

Endpoints:
- /api/terabox?key=YOUR_KEY&url=TERABOX_URL -> download + stream
- /api/terabox-file?key=&url= -> file only
- /health -> status
- / -> docs

Keys:
- Demo key: 1week (limited)
- Your own key: Set in env ADMIN_KEY or create via /admin
"""

import os
import time
import requests
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Config
ADMIN_KEY = os.getenv("ADMIN_KEY", "himanshu123")
DEMO_KEY = os.getenv("DEMO_KEY", "1week")
UPSTREAM_KEY = os.getenv("UPSTREAM_KEY", "1week")
PORT = int(os.getenv("PORT", "8080"))

# Upstream APIs - 4 APIs combination (2 live, 2 dead as per analysis)
UPSTREAMS = [
    {
        "name": "terabox-stream-v1",
        "url": "https://osint-apis-hub.onrender.com/api/terabox-stream",
        "status": "LIVE",
        "priority": 1
    },
    {
        "name": "terabox-file",
        "url": "https://osint-apis-hub.onrender.com/api/terabox-file",
        "status": "LIVE",
        "priority": 2
    },
    {
        "name": "terabox-stream-v2",
        "url": "https://osint-apis-hub.onrender.com/api/terabox-stream-v2",
        "status": "DEAD-429",
        "priority": 3
    },
    {
        "name": "terabox-stream-v3",
        "url": "https://osint-apis-hub.onrender.com/api/terabox-stream-v3",
        "status": "DEAD-502",
        "priority": 4
    },
]

# Simple key storage (in-memory + file)
KEYS = {
    "1week": {"owner": "demo", "limit": 100, "used": 0, "type": "demo"},
    "himanshu": {"owner": "himanshu", "limit": 10000, "used": 0, "type": "admin"},
    ADMIN_KEY: {"owner": "admin", "limit": 100000, "used": 0, "type": "admin"},
}

# Stats
STATS = {"total": 0, "ok": 0, "fail": 0, "start": time.time()}

HTML_DOCS = """
<html><head><title>TeraBox API Hub - @Supermannn_x</title>
<style>body{font-family:Arial;max-width:800px;margin:auto;padding:20px;background:#0f0f0f;color:#fff}
a{color:#4fc3f7} code{background:#222;padding:2px 6px;border-radius:4px}
.card{background:#1e1e1e;padding:15px;border-radius:10px;margin:10px 0}
.live{color:#4caf50} .dead{color:#f44336}
</style></head><body>
<h1>☁️ TeraBox API Hub - Pro</h1>
<p>Owner: @Supermannn_x | 4 APIs Combined (2 LIVE)</p>

<div class="card">
<h3>📊 Live Status (Analyzed)</h3>
<ul>
<li><span class="live">✅ LIVE</span> - <code>/api/terabox-stream</code> - download + stream m3u8 + thumbnail (33MB test OK)</li>
<li><span class="live">✅ LIVE</span> - <code>/api/terabox-file</code> - download only (109GB test OK)</li>
<li><span class="dead">❌ DEAD</span> - <code>/api/terabox-stream-v2</code> - 429 Guest limit (5 videos/6h)</li>
<li><span class="dead">❌ DEAD</span> - <code>/api/terabox-stream-v3</code> - 502 Bad Gateway</li>
</ul>
<p><b>Our API tries LIVE ones first with fallback</b></p>
</div>

<div class="card">
<h3>🔗 Endpoints</h3>
<p><code>/api/terabox?key=YOUR_KEY&url=TERABOX_URL</code> - Main (tries all 4)</p>
<p><code>/api/terabox-file?key=&url=</code> - File only</p>
<p><code>/api/terabox-stream?key=&url=</code> - Stream only</p>
<p><code>/health</code> - Status</p>
</div>

<div class="card">
<h3>📌 Example</h3>
<code>https://YOUR-API.onrender.com/api/terabox?key=1week&url=https://1024terabox.com/s/1EqwgqQWgmeOvQxc33258UA</code>
<p>Response: download_url, stream_url (m3u8), thumbnail, size</p>
</div>

<div class="card">
<h3>🔑 Keys</h3>
<p>Demo: <code>1week</code> (100/day)</p>
<p>Admin: Set <code>ADMIN_KEY</code> env var</p>
<p>Create new key: <code>/admin?key=ADMIN_KEY&newkey=mykey&limit=1000</code></p>
</div>

<div class="card">
<h3>📊 Stats</h3>
<p>Total: {{total}} | OK: {{ok}} | Fail: {{fail}} | Uptime: {{uptime}}s</p>
</div>

<p>🔥 Powered by @Supermannn_x | Like utility-duniya-bot pattern</p>
</body></html>
"""

def is_valid_key(k):
    return k in KEYS

def check_rate_limit(k):
    # Simple daily limit (in-memory, resets on restart - for production use DB)
    if k not in KEYS:
        return False
    info = KEYS[k]
    if info["used"] >= info["limit"]:
        return False
    info["used"] += 1
    return True

@app.route('/')
def docs():
    uptime = int(time.time() - STATS["start"])
    return render_template_string(HTML_DOCS, total=STATS["total"], ok=STATS["ok"], fail=STATS["fail"], uptime=uptime)

@app.route('/health')
def health():
    return jsonify({
        "status": "active",
        "uptime": int(time.time() - STATS["start"]),
        "upstreams": UPSTREAMS,
        "stats": STATS,
        "keys": len(KEYS),
        "timestamp": time.time()
    })

@app.route('/api/terabox')
def terabox_combined():
    """Main endpoint - tries all 4 upstreams"""
    key = request.args.get('key','')
    url = request.args.get('url','')
    
    STATS["total"] += 1
    
    if not is_valid_key(key):
        STATS["fail"] += 1
        return jsonify({"ok": False, "code": 403, "error": "Invalid key, get demo key: 1week"}), 403
    if not check_rate_limit(key):
        STATS["fail"] += 1
        return jsonify({"ok": False, "code": 429, "error": "Rate limit reached"}), 429
    if not url:
        STATS["fail"] += 1
        return jsonify({"ok": False, "code": 400, "error": "Missing url param"}), 400
    if "terabox.com" not in url:
        STATS["fail"] += 1
        return jsonify({"ok": False, "code": 400, "error": "Only terabox.com URLs allowed"}), 400
    
    # Try upstreams in priority order
    attempts = []
    for api in sorted(UPSTREAMS, key=lambda x: x["priority"]):
        try:
            req_url = f"{api['url']}?key={UPSTREAM_KEY}&url={url}"
            r = requests.get(req_url, timeout=90, headers={"User-Agent": "Mozilla/5.0"})
            attempts.append({"api": api["name"], "code": r.status_code, "status": "tried"})
            
            if r.status_code == 200:
                try:
                    data = r.json()
                    # Check if has files
                    if data.get("files") or data.get("status") == True or data.get("code") == 200:
                        # Add branding + our wrapper
                        data["ok"] = True
                        data["source"] = api["name"]
                        data["powered_by"] = "@Supermannn_x"
                        data["your_api"] = request.host_url.rstrip('/')
                        data["attempts"] = attempts
                        STATS["ok"] += 1
                        return jsonify(data)
                except:
                    continue
        except Exception as e:
            attempts.append({"api": api["name"], "error": str(e)[:200], "status": "exception"})
            continue
    
    STATS["fail"] += 1
    return jsonify({
        "ok": False,
        "code": 502,
        "error": "All upstreams failed",
        "attempts": attempts,
        "tip": "Upstream osint-apis-hub may be sleeping (50s wake up) or rate limited. Try again in 1 min."
    }), 502

@app.route('/api/terabox-file')
def terabox_file():
    """File only endpoint"""
    key = request.args.get('key','')
    url = request.args.get('url','')
    if not is_valid_key(key):
        return jsonify({"ok": False, "error": "Invalid key"}), 403
    # Proxy to upstream file API
    try:
        r = requests.get(f"https://osint-apis-hub.onrender.com/api/terabox-file?key={UPSTREAM_KEY}&url={url}", timeout=90)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 502

@app.route('/api/terabox-stream')
def terabox_stream():
    """Stream only endpoint"""
    key = request.args.get('key','')
    url = request.args.get('url','')
    if not is_valid_key(key):
        return jsonify({"ok": False, "error": "Invalid key"}), 403
    try:
        r = requests.get(f"https://osint-apis-hub.onrender.com/api/terabox-stream?key={UPSTREAM_KEY}&url={url}", timeout=90)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 502

@app.route('/admin')
def admin():
    """Simple admin to create keys"""
    key = request.args.get('key','')
    newkey = request.args.get('newkey','')
    limit = int(request.args.get('limit','1000'))
    
    if key != ADMIN_KEY:
        return jsonify({"ok": False, "error": "Invalid admin key"}), 403
    if not newkey:
        return jsonify({"ok": True, "keys": KEYS, "stats": STATS})
    
    KEYS[newkey] = {"owner": "custom", "limit": limit, "used": 0, "type": "custom"}
    return jsonify({"ok": True, "message": f"Key {newkey} created with limit {limit}", "keys": KEYS})

if __name__ == '__main__':
    print(f"TeraBox API Hub starting on port {PORT}")
    print(f"Upstreams: {UPSTREAMS}")
    print(f"Keys: {list(KEYS.keys())}")
    app.run(host='0.0.0.0', port=PORT, threaded=True)
