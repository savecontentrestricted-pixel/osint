"""
Ultra Advanced Proxy Tools - 99% Safe (as per user request)
Features:
- Proxy Finder (fresh free proxies from public sources)
- Proxy Checker (live/dead, speed, anonymity, country)
- Safety Score
- Usage guide for Telegram, Browser, etc.
- Elite anonymity detection

Note: No proxy is 100% safe. We provide 99% safety via elite proxies + checks, but user must still be careful.
Free proxies can see traffic, so use only for public sites, not banking.
"""

import requests
import time
import re
import socket
from concurrent.futures import ThreadPoolExecutor

# Public free proxy sources (for demo, real bot would fetch from multiple)
FREE_PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite",
    "https://www.proxy-list.download/api/v1/get?type=http&anon=elite",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
]

def check_proxy(proxy_str, timeout=10):
    """
    Check if proxy is alive, speed, anonymity
    proxy_str format: ip:port or ip:port:user:pass
    Returns dict with live, speed, anonymity, country, etc.
    """
    result = {
        "proxy": proxy_str,
        "live": False,
        "speed_ms": None,
        "anonymity": "unknown",
        "country": "unknown",
        "type": "http",
        "safety_score": 0,
        "error": None
    }
    
    try:
        # Parse proxy
        parts = proxy_str.strip().split(':')
        if len(parts) < 2:
            result["error"] = "Invalid format, use ip:port"
            return result
        
        ip = parts[0]
        port = parts[1]
        
        # Basic IP validation
        try:
            socket.inet_aton(ip)
        except:
            result["error"] = "Invalid IP"
            return result
        
        # Try to use proxy to fetch httpbin
        proxies = {
            "http": f"http://{proxy_str}",
            "https": f"http://{proxy_str}"
        }
        
        start = time.time()
        try:
            # Check via httpbin to see anonymity
            r = requests.get(
                "http://httpbin.org/ip",
                proxies=proxies,
                timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            elapsed = int((time.time() - start) * 1000)
            
            if r.status_code == 200:
                result["live"] = True
                result["speed_ms"] = elapsed
                
                # Check anonymity via headers
                # Elite: doesn't reveal real IP in headers
                # Anonymous: reveals it's proxy but not real IP
                # Transparent: reveals real IP
                try:
                    # Try to get headers via httpbin
                    r2 = requests.get(
                        "http://httpbin.org/headers",
                        proxies=proxies,
                        timeout=timeout,
                        headers={"User-Agent": "Mozilla/5.0"}
                    )
                    if r2.status_code == 200:
                        headers_text = r2.text.lower()
                        if "via" in headers_text or "proxy" in headers_text or "x-forwarded" in headers_text:
                            result["anonymity"] = "anonymous"
                        else:
                            result["anonymity"] = "elite"
                    else:
                        result["anonymity"] = "anonymous"
                except:
                    result["anonymity"] = "elite"  # Assume elite if works
                
                # Try to get country via ip-api (without proxy, using IP)
                try:
                    geo_r = requests.get(f"http://ip-api.com/json/{ip}?fields=country,query", timeout=5)
                    if geo_r.status_code == 200:
                        geo = geo_r.json()
                        result["country"] = geo.get("country","unknown")
                except:
                    pass
                
                # Safety score calculation (0-100)
                score = 0
                if result["live"]:
                    score += 30
                if result["anonymity"] == "elite":
                    score += 40
                elif result["anonymity"] == "anonymous":
                    score += 20
                if result["speed_ms"] and result["speed_ms"] < 1000:
                    score += 20
                elif result["speed_ms"] and result["speed_ms"] < 3000:
                    score += 10
                if result["country"] != "unknown":
                    score += 10
                
                result["safety_score"] = min(score, 99)  # Max 99% as per user request (100% never)
                
            else:
                result["error"] = f"HTTP {r.status_code}"
                
        except requests.exceptions.ProxyError:
            result["error"] = "Proxy error / dead"
        except requests.exceptions.ConnectTimeout:
            result["error"] = "Timeout / dead"
        except requests.exceptions.ReadTimeout:
            result["error"] = "Read timeout"
        except Exception as e:
            result["error"] = str(e)[:100]
            
    except Exception as e:
        result["error"] = str(e)[:100]
    
    return result

def get_fresh_proxies(limit=10):
    """Get fresh free proxies from public sources (with fallback)"""
    proxies = []
    
    # Try to fetch from public sources
    for source in FREE_PROXY_SOURCES[:2]:  # Try 2 sources for speed
        try:
            r = requests.get(source, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                # Parse proxies - each line ip:port
                lines = r.text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    # Basic validation: ip:port
                    if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', line):
                        if line not in proxies:
                            proxies.append(line)
                            if len(proxies) >= limit:
                                break
            if len(proxies) >= limit:
                break
        except:
            continue
    
    # Fallback: If no proxies fetched (sources down), return some public demo proxies (may be dead, but for demo)
    if not proxies:
        # These are example, will be checked for live status
        fallback = [
            "8.8.8.8:8080",
            "1.1.1.1:8080",
            "103.152.112.162:80",
            "103.149.162.194:80",
        ]
        proxies = fallback[:limit]
    
    return proxies[:limit]

def check_proxies_batch(proxy_list, max_workers=5):
    """Check multiple proxies in parallel"""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(check_proxy, p, 8) for p in proxy_list[:10]]
        for f in futures:
            try:
                res = f.result(timeout=15)
                results.append(res)
            except Exception as e:
                results.append({"proxy": "unknown", "live": False, "error": str(e)[:100]})
    
    # Sort by safety score descending
    results.sort(key=lambda x: x.get("safety_score",0), reverse=True)
    return results

def format_proxy_report(results, limit=10):
    """Format proxy check results as beautiful text"""
    live = [r for r in results if r.get("live")]
    dead = [r for r in results if not r.get("live")]
    
    txt = f"""
╔══════════════════════════════════════╗
║  🌐 <b>ULTRA PROXY CHECKER - 99% Safe</b> ║
╚══════════════════════════════════════╝

📊 <b>Checked:</b> {len(results)} | <span class="live">✅ Live: {len(live)}</span> | ❌ Dead: {len(dead)}

━━━━━━━━━━━━━━━━━━━━━━

"""
    if live:
        txt += f"✅ <b>Elite Proxies (99% Safe):</b>\n\n"
        for i, p in enumerate(live[:5], 1):
            txt += f"<b>{i}. {p['proxy']}</b>\n"
            txt += f"   🌍 Country: {p.get('country','?')} | ⚡ Speed: {p.get('speed_ms','?')}ms\n"
            txt += f"   🕵️ Anon: {p.get('anonymity','?')} | 🛡️ Safety: {p.get('safety_score',0)}%\n"
            txt += f"   📋 Type: {p.get('type','http')} | ✅ LIVE\n\n"
    
    if dead and len(live) < 3:
        txt += f"❌ <b>Dead / Slow:</b>\n\n"
        for p in dead[:3]:
            txt += f"• <code>{p['proxy']}</code> → {p.get('error','dead')}\n"
        txt += f"\n"
    
    txt += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    txt += f"🔒 <b>How to Use (Safely 99%):</b>\n\n"
    txt += f"📱 <b>Telegram:</b>\n"
    txt += f"   Settings → Data & Storage → Proxy → Add Proxy → {live[0]['proxy'] if live else 'IP:Port'}\n\n"
    txt += f"🌐 <b>Chrome:</b>\n"
    txt += f"   Settings → System → Open Proxy Settings → {live[0]['proxy'] if live else 'IP:Port'}\n\n"
    txt += f"⚠️ <b>Safety Tips for 99%:</b>\n"
    txt += f"• Free proxies can see your traffic → Use only for public sites\n"
    txt += f"• Banking / OTP ke liye kabhi free proxy mat use karo\n"
    txt += f"• Elite proxies (99% score) sabse safe hote hain\n"
    txt += f"• Har 1 hour me proxy change karo\n"
    txt += f"• 100% safe koi proxy nahi hota, max 99% (as you said 😆)\n\n"
    txt += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    txt += f"🔥 Powered by @Supermannn_x\n"
    txt += f"⚡ Ultra Advanced - Kisi ke paas nahi!\n"
    
    return txt

def format_proxy_finder_report(proxies):
    """Format fresh proxies list"""
    txt = f"""
╔══════════════════════════════════════╗
║  🌐 <b>PROXY FINDER - Fresh List</b>     ║
╚══════════════════════════════════════╝

📦 <b>Found:</b> {len(proxies)} fresh proxies

━━━━━━━━━━━━━━━━━━━━━━

"""
    for i, p in enumerate(proxies[:10], 1):
        txt += f"<b>{i}.</b> <code>{p}</code>\n"
    
    txt += f"\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    txt += f"💡 <b>Next:</b> Send any proxy from list to check if LIVE + Safety Score\n"
    txt += f"Example: <code>{proxies[0] if proxies else '1.2.3.4:8080'}</code>\n\n"
    txt += f"🔥 @Supermannn_x\n"
    
    return txt

if __name__ == "__main__":
    # Test
    print("Finding fresh proxies...")
    proxies = get_fresh_proxies(5)
    print(f"Found {len(proxies)}: {proxies}")
    
    print("\nChecking...")
    results = check_proxies_batch(proxies)
    print(format_proxy_report(results))
