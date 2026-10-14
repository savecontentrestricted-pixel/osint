"""
JS Secret Finder - Pro OSINT Tool
Finds hidden API keys, endpoints, secrets in JavaScript files

Example: https://example.com -> extracts JS files -> finds api_key, /admin, etc.
"""

import re
import requests
from .fast_cache import with_cache
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Regex patterns for secrets
SECRET_PATTERNS = {
    "Google API Key": r"AIza[0-9A-Za-z\-_]{35}",
    "Google OAuth": r"ya29\.[0-9A-Za-z\-_]+",
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret": r"aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}",
    "GitHub Token": r"ghp_[0-9a-zA-Z]{36}",
    "GitHub PAT": r"github_pat_[0-9a-zA-Z_]{82}",
    "Stripe Key": r"sk_live_[0-9a-zA-Z]{24,}",
    "Stripe Publishable": r"pk_live_[0-9a-zA-Z]{24,}",
    "Slack Token": r"xox[bprs]-[0-9a-zA-Z\-]+",
    "Slack Webhook": r"https://hooks\.slack\.com/services/[A-Z0-9/]+",
    "Facebook Token": r"EAACEdEose0cBA[0-9A-Za-z]+",
    "Twitter Bearer": r"AAAAAAAAAAAAAAAAAAAAA%2F[A-Za-z0-9%]+",
    "Private Key": r"-----BEGIN PRIVATE KEY-----",
    "API Key Generic": r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}",
    "Password Generic": r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{3,}['\"]",
    "Secret Generic": r"(?i)(secret|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{10,}['\"]",
    "Endpoint /admin": r"['\"]/(admin|api|login|dashboard|config|backup|private)[^'\"]*['\"]",
    "URL with Key": r"https?://[^\s'\"]+\?(?:.*)?(?:key|token|api)=[A-Za-z0-9_\-]+",
}

ENDPOINT_PATTERNS = [
    r"['\"]/(api/v\d+/[^'\"]+)['\"]",
    r"['\"]/(admin[^'\"]*)['\"]",
    r"['\"]/(config[^'\"]*)['\"]",
    r"['\"]/(backup[^'\"]*)['\"]",
    r"['\"]/(private[^'\"]*)['\"]",
    r"['\"]/(v\d+/[^'\"]+)['\"]",
]

def extract_js_urls(html, base_url):
    """Extract JS file URLs from HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    js_urls = []
    for script in soup.find_all('script', src=True):
        src = script['src']
        full_url = urljoin(base_url, src)
        js_urls.append(full_url)
    # Also check inline scripts for endpoints
    return js_urls[:15]  # Limit to 15 JS files

def find_secrets_in_text(text, url=""):
    """Find secrets in text using regex"""
    findings = []
    for name, pattern in SECRET_PATTERNS.items():
        try:
            matches = re.findall(pattern, text)
            for match in matches[:5]:  # Limit per pattern
                # Clean match
                if isinstance(match, tuple):
                    match = match[0]
                match_str = str(match)[:200]  # Truncate
                if len(match_str) > 5:
                    findings.append({
                        "type": name,
                        "value": match_str,
                        "url": url
                    })
        except Exception:
            continue
    return findings

def find_endpoints_in_text(text, url=""):
    """Find hidden endpoints"""
    endpoints = []
    for pattern in ENDPOINT_PATTERNS:
        try:
            matches = re.findall(pattern, text)
            for match in matches[:10]:
                if isinstance(match, tuple):
                    match = match[0]
                ep = str(match)[:200]
                if len(ep) > 2:
                    endpoints.append({
                        "endpoint": ep,
                        "url": url
                    })
        except:
            continue
    return endpoints

@with_cache("jss", 1800, 21600)
def js_secret_finder(target_url):
    """Main function - finds secrets in JS files of a website"""
    if not target_url.startswith('http'):
        target_url = 'https://' + target_url
    
    result = {
        "ok": False,
        "url": target_url,
        "js_files": [],
        "secrets": [],
        "endpoints": [],
        "total_js": 0,
        "error": None
    }
    
    try:
        # Fetch main page
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        r = requests.get(target_url, headers=headers, timeout=15, verify=False)
        r.raise_for_status()
        html = r.text
        
        # Extract JS URLs
        js_urls = extract_js_urls(html, target_url)
        result["js_files"] = js_urls
        result["total_js"] = len(js_urls)
        
        all_secrets = []
        all_endpoints = []
        
        # Check main HTML for secrets too
        all_secrets.extend(find_secrets_in_text(html, target_url))
        all_endpoints.extend(find_endpoints_in_text(html, target_url))
        
        # Fetch each JS file and scan
        for js_url in js_urls[:10]:  # Limit to 10 JS files for speed
            try:
                js_r = requests.get(js_url, headers=headers, timeout=10, verify=False)
                if js_r.status_code == 200:
                    js_text = js_r.text
                    # Find secrets
                    secrets = find_secrets_in_text(js_text, js_url)
                    all_secrets.extend(secrets)
                    # Find endpoints
                    endpoints = find_endpoints_in_text(js_text, js_url)
                    all_endpoints.extend(endpoints)
            except Exception as e:
                continue
        
        # Deduplicate
        seen_secrets = set()
        unique_secrets = []
        for s in all_secrets:
            key = (s["type"], s["value"][:50])
            if key not in seen_secrets:
                seen_secrets.add(key)
                unique_secrets.append(s)
        
        seen_eps = set()
        unique_eps = []
        for ep in all_endpoints:
            if ep["endpoint"] not in seen_eps:
                seen_eps.add(ep["endpoint"])
                unique_eps.append(ep)
        
        result["secrets"] = unique_secrets[:20]  # Limit 20
        result["endpoints"] = unique_eps[:20]
        result["ok"] = True
        
        return result
        
    except Exception as e:
        result["error"] = str(e)[:300]
        return result

def format_js_report(result):
    """Format result as beautiful text"""
    if not result.get("ok"):
        return f"❌ Error: {result.get('error','Unknown')}"
    
    url = result.get("url")
    js_files = result.get("js_files", [])
    secrets = result.get("secrets", [])
    endpoints = result.get("endpoints", [])
    
    txt = f"""
╔══════════════════════════════════════╗
║  💎 <b>JS SECRET FINDER - PRO</b>        ║
╚══════════════════════════════════════╝

🌐 <b>URL:</b> {url}

📜 <b>JS Files Found:</b> {len(js_files)}

"""
    if js_files:
        for jf in js_files[:5]:
            txt += f"• <code>{jf[:80]}</code>\n"
        if len(js_files) > 5:
            txt += f"• ...and {len(js_files)-5} more\n"
    
    txt += f"\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    txt += f"🔑 <b>Secrets Found ({len(secrets)}):</b>\n\n"
    if secrets:
        for sec in secrets[:10]:
            txt += f"• <b>{sec['type']}:</b>\n  <code>{sec['value'][:100]}</code>\n  From: {sec['url'][:60]}\n\n"
        if len(secrets) > 10:
            txt += f"...and {len(secrets)-10} more secrets\n\n"
    else:
        txt += "✅ No obvious secrets found (good!)\n\n"
    
    txt += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    txt += f"🔗 <b>Hidden Endpoints ({len(endpoints)}):</b>\n\n"
    if endpoints:
        for ep in endpoints[:10]:
            txt += f"• <code>{ep['endpoint'][:80]}</code>\n  From: {ep['url'][:50]}\n\n"
        if len(endpoints) > 10:
            txt += f"...and {len(endpoints)-10} more\n\n"
    else:
        txt += "No hidden endpoints found\n\n"
    
    txt += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    txt += f"⚠️ <b>Note:</b> Only public JS files scanned. Use on your own sites or with permission.\n\n"
    txt += f"🔥 Powered by @Supermannn_x\n"
    
    return txt

if __name__ == "__main__":
    # Test
    res = js_secret_finder("https://example.com")
    print(format_js_report(res))
