# -*- coding: utf-8 -*-
"""
modules.ipinfo_free — 🌐 IP / DOMAIN INFO, BILKUL MUFT (v126)

Owner ka purana IP tool provider ke server par tha, jo band pada hai
(504 Gateway Timeout). Ab ye tool **kisi provider par depend nahi karta**.

Source: http://ip-api.com/json/{ip}
  • koi API key NAHI
  • ~30 ms (naapa gaya)
  • free plan: 45 request/minute — hamare liye kaafi
  • 24 field deta hai: country, region, city, ISP, org, ASN, timezone,
    currency, lat/lon, zip, continent, mobile/proxy/hosting flags,
    aur reverse DNS (PTR) bhi

Backup: https://ipwho.is/{ip} (ye bhi muft + bina key)

Domain bhi chalta hai: google.com -> pehle IP nikalte hain, phir lookup.

❌ NMAP PORT SCAN jaan-bujh kar NAHI daala:
   kisi dusre ke server ke port scan karna (a) kai jagah gair-kanooni hai,
   (b) Render hamara server block kar sakta hai, (c) har lookup 20-30
   second lamba kar deta. Baaki poora report waisa hi hai.

Koi nayi library nahi — sirf Python ka apna socket + project ka net.http_get.
"""

from __future__ import annotations

import ipaddress
import json
import re
import socket
import time

try:
    from modules.core.net import http_get as _http_get
except Exception:                                                # noqa: BLE001
    _http_get = None

try:
    from modules.core.nodata import no_data as _no_data
except Exception:                                                # noqa: BLE001
    def _no_data(term="", what=""):                              # fallback
        return "❌ <b>NO DATA FOUND</b>\n📭 Database me iska koi record nahi hai."

__all__ = ["lookup", "render", "validate"]

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# ip-api ka field bitmask — upar wale saare field ek hi call me aa jate hain
_PRIMARY = ("http://ip-api.com/json/{}"
            "?fields=status,message,continent,country,countryCode,region,"
            "regionName,city,district,zip,lat,lon,timezone,offset,currency,"
            "isp,org,as,asname,reverse,mobile,proxy,hosting,query")
_BACKUP = "https://ipwho.is/{}"

_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

_DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))+$")


# --------------------------------------------------------------- helpers
def _clean(v) -> str:
    s = str(v if v is not None else "").strip()
    return "" if s.lower() in ("none", "null", "n/a", "-", "unknown", "") else s


def _is_ip(s: str) -> bool:
    try:
        ipaddress.ip_address(s)
        return True
    except Exception:                                            # noqa: BLE001
        return False


def validate(text) -> tuple:
    """IP ya domain — dono chalenge. (ok, saaf_value, error_message)"""
    t = str(text or "").strip().lower()
    t = re.sub(r"^https?://", "", t).split("/")[0].split("?")[0].strip()
    t = t.strip("[]")
    if not t:
        return False, "", ("IP address ya domain bhejo.\n"
                           "📌 Jaise: <code>8.8.8.8</code> ya "
                           "<code>google.com</code>")
    if _is_ip(t):
        return True, t, ""
    if _DOMAIN_RE.match(t):
        return True, t, ""
    return False, t, ("Ye IP ya domain jaisa nahi lag raha.\n"
                      "📌 IP: <code>8.8.8.8</code>\n"
                      "📌 Domain: <code>google.com</code>\n"
                      f"Aapne bheja: <code>{t[:40]}</code>")


def _resolve(host: str) -> str:
    """Domain -> IP (2 second se zyada nahi rukte)."""
    old = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(3)
        return socket.gethostbyname(host)
    except Exception:                                            # noqa: BLE001
        return ""
    finally:
        socket.setdefaulttimeout(old)


def _ptr(ip: str) -> str:
    """Reverse DNS — ip-api na de to Python khud nikal lega."""
    old = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(3)
        return socket.gethostbyaddr(ip)[0]
    except Exception:                                            # noqa: BLE001
        return ""
    finally:
        socket.setdefaulttimeout(old)


def _get_json(url: str, timeout: int = 12):
    if _http_get is None:
        return None
    try:
        r = _http_get(url, timeout=timeout, retries=0,
                      headers={"User-Agent": _UA})
        if getattr(r, "status_code", 0) != 200:
            return None
        return json.loads(r.text)
    except Exception:                                            # noqa: BLE001
        return None


# --------------------------------------------------------------- lookup
def lookup(term) -> dict:
    """
    IP ya domain ka poora report. KABHI raise nahi karta.

    return: {ok, term, ip, host, data, ms}  ya  {ok:False, error, notfound?}
    """
    ok, val, err = validate(term)
    if not ok:
        return {"ok": False, "bad_input": True,
                "error": "⚠️ <b>GALAT INPUT</b>\n\n" + err}

    t0 = time.time()
    host = "" if _is_ip(val) else val
    ip = val if _is_ip(val) else _resolve(val)
    if not ip:
        return {"ok": False, "notfound": True,
                "error": _no_data(val, "domain")}

    d = _get_json(_PRIMARY.format(ip))
    src = "ip-api"
    if not isinstance(d, dict) or d.get("status") != "success":
        b = _get_json(_BACKUP.format(ip))                        # backup
        if isinstance(b, dict) and b.get("success"):
            d, src = {
                "query": b.get("ip"), "country": b.get("country"),
                "countryCode": b.get("country_code"),
                "regionName": b.get("region"), "city": b.get("city"),
                "zip": b.get("postal"), "lat": b.get("latitude"),
                "lon": b.get("longitude"), "continent": b.get("continent"),
                "isp": ((b.get("connection") or {}).get("isp")),
                "org": ((b.get("connection") or {}).get("org")),
                "as": ((b.get("connection") or {}).get("asn")),
                "timezone": ((b.get("timezone") or {}).get("id")),
                "currency": ((b.get("currency") or {}).get("code")),
                "is_eu": b.get("is_eu"),
            }, "ipwho"
        else:
            msg = ""
            if isinstance(d, dict):
                msg = _clean(d.get("message"))
            if msg in ("private range", "reserved range"):
                return {"ok": False, "notfound": True,
                        "error": ("❌ <b>NO DATA FOUND</b>\n\n"
                                  f"🔎 <code>{ip}</code>\n"
                                  "📭 Ye private/reserved IP hai — iski koi "
                                  "public jaankari nahi hoti.")}
            return {"ok": False, "notfound": True, "error": _no_data(ip, "IP")}

    if not _clean(d.get("reverse")):
        d["reverse"] = _ptr(ip)

    return {"ok": True, "term": str(term).strip(), "ip": ip, "host": host,
            "data": d, "src": src, "ms": int((time.time() - t0) * 1000)}


# --------------------------------------------------------------- card
def render(res: dict, *, hesc, brand: str) -> str:
    """Owner ke diye format wala IP report card."""
    res = res if isinstance(res, dict) else {}
    d = res.get("data") or {}

    def g(k):
        return _clean(d.get(k))

    W = 30
    L = []
    L.append("╭" + "─" * W + "⭓")
    L.append("│ 🌐 <b>IP &amp; DOMAIN REPORT</b>")
    L.append("├" + "─" * W)
    L.append(f"│ 🌍 <b>Input:</b> <code>{hesc(res.get('term') or '')}</code>")
    if res.get("host"):
        L.append(f"│ 🔗 <b>Domain:</b> <code>{hesc(res['host'])}</code>")
    L.append(f"│ 🌐 <b>Target IP:</b> <code>{hesc(res.get('ip') or '')}</code>")

    # ---------------- geolocation ----------------
    L.append("│")
    L.append("│ 🔹 <b>[IP GEOLOCATION]</b>")
    for label, key in (("Country", "country"), ("Region", "regionName"),
                       ("City", "city"), ("Pincode", "zip"),
                       ("ISP", "isp"), ("Organization", "org")):
        if g(key):
            L.append(f"│ • <b>{label}:</b> {hesc(g(key))}")
    _asn = g("as") or g("asname")
    if _asn:
        L.append(f"│ • <b>ASN:</b> {hesc(_asn[:70])}")

    # ---------------- reverse DNS ----------------
    if g("reverse"):
        L.append("│")
        L.append("│ 🔹 <b>[REVERSE IP (PTR)]</b>")
        L.append(f"│ • {hesc(g('reverse'))}")

    # ---------------- network type ----------------
    flags = []
    if d.get("mobile"):
        flags.append("📱 Mobile network")
    if d.get("proxy"):
        flags.append("🕵️ Proxy / VPN")
    if d.get("hosting"):
        flags.append("🏢 Datacenter / Hosting")
    if flags:
        L.append("│")
        L.append("│ 🔹 <b>[NETWORK TYPE]</b>")
        for f in flags:
            L.append(f"│ • {f}")

    # ---------------- advanced ----------------
    adv = []
    if g("continent"):
        adv.append(("Continent", g("continent")))
    if g("countryCode"):
        adv.append(("Country Code", g("countryCode")))
    if g("timezone"):
        adv.append(("Timezone", g("timezone")))
    if g("currency"):
        adv.append(("Currency", g("currency")))
    if d.get("is_eu") is not None:
        adv.append(("EU Member", "true" if d.get("is_eu") else "false"))
    if g("lat") and g("lon"):
        adv.append(("Coordinates", f"{g('lat')}, {g('lon')}"))
    if adv:
        L.append("│")
        L.append("│ 🔹 <b>[ADVANCED]</b>")
        for k, v in adv:
            L.append(f"│ • <b>{k}:</b> {hesc(str(v))}")

    # ---------------- footer ----------------
    tm = time.localtime(time.time() + 19800)                     # IST
    L.append("│")
    L.append(f"│ 📅 <b>Date:</b> {tm.tm_mday} {_MONTHS[tm.tm_mon - 1]} "
             f"{tm.tm_year}")
    L.append(f"│ ⚡ <b>Speed:</b> {int(res.get('ms') or 0)}ms  ·  <i>free API</i>")
    L.append("╰" + "─" * W + "⭓")
    L.append("")
    L.append(brand)

    out = "\n".join(L)
    if len(out) > 3900:
        out = out[:3850].rsplit("\n", 1)[0] + "\n╰" + "─" * W + "⭓\n\n" + brand
    return out
