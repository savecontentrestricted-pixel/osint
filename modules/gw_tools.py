# -*- coding: utf-8 -*-
"""
🛰️ GATEWAY TOOLS v2.8 — TOWER LOCATION · E-CHALLAN · FASTAG
===============================================================
Ye teeno tool USER ke APNE gateway (utility-api v2.8.0) par chalte hain:

    GET https://utility-api-vu83.onrender.com/api
        ?key=<MYNUM_API_KEY>&tool=tower|challan|fastag&term=<input>

Architectural rule (USER ORDER, 23 Oct 2026):
    "Pehle API ko MERE LIYE personally banao (gateway), PHIR bots mein lagao."
    → Bot kabhi kisi random third-party API ko directly nahi chhunta.
    → Source mare / key expire ho → sirf gateway ka Render env var badalta hai
      (TOWER_API_KEY / CHALLAN_API_URL / FASTAG_API_URL) — bot code ZERO
      badlega. Never-expire pattern.

Gateway ke slim response shapes (v2.8, live naapa gaya):
    tower   → flat dict: Tower Locations, Mobile State, Owner Name (masked),
              map_lat/map_lng, Tracking History[], ... (infra keys already hati)
    challan → {vehicle, status_queried, total_count, total_amount,
               results:{<status>:{count, total_amount, challans[<=5]}}}
    fastag  → {found, count, active_count, message, tags[<=8]}

Cache: fast_cache.with_cache — sirf ok/notfound cache hota hai, errors nahi
(safety built-in in api_cache_set).
"""

from __future__ import annotations

import html
import os
import re
import time
from typing import Any, Dict, List

from .fast_cache import with_cache, get_session

API_URL = os.getenv("MYNUM_API_URL", "https://utility-api-vu83.onrender.com/api").strip()
API_KEY = os.getenv("MYNUM_API_KEY", "").strip()
TIMEOUT = 45

# Gateway / tool infra keys — user ko nahi dikhani (noise ya secret)
_SKIP_KEYS = {"iframe_src", "title", "website", "Inputed Number"}


# ══════════════════════════════════════════════════════════════════
#  CORE GATEWAY CALL
# ══════════════════════════════════════════════════════════════════
def _call(tool: str, term: str) -> Dict[str, Any]:
    """Gateway lookup — telegram_tools.lookup_tg jaisa, par tool param naya."""
    t0 = time.time()
    if not term:
        return {"ok": False, "error": "Input khaali hai."}
    try:
        r = get_session().get(
            API_URL,
            params={"key": API_KEY, "tool": tool, "term": term},
            timeout=TIMEOUT,
        )
        ms = int((time.time() - t0) * 1000)
        if r.status_code != 200:
            return {"ok": False, "error": f"gateway HTTP {r.status_code}"}
        try:
            j = r.json()
        except Exception:
            return {"ok": False, "error": "gateway se bad JSON aaya"}
        if not isinstance(j, dict):
            return {"ok": False, "error": "gateway ne ajeeb jawab diya"}
        if not j.get("ok"):
            why = str(j.get("why") or j.get("message") or j.get("error") or "").strip()
            if why.lower() in ("notfound", "not_found", "no record found"):
                return {"ok": False, "not_found": True, "error": "Data not found."}
            return {"ok": False, "error": (why or "lookup fail")[:160]}
        d = j.get("data")
        if not isinstance(d, dict) or not d:
            return {"ok": False, "not_found": True, "error": "Data not found."}
        return {"ok": True, "tool": tool, "term": term, "data": d, "ms": ms}
    except Exception as e:                                         # noqa: BLE001
        return {"ok": False, "error": f"network: {str(e)[:120]}"}


_VEHICLE_RE = re.compile(r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$")
_MOBILE_RE = re.compile(r"^[6-9][0-9]{9}$")


def _clean_vehicle(term: Any) -> str:
    return re.sub(r"\s+", "", str(term or "")).upper()


# ══════════════════════════════════════════════════════════════════
#  LOOKUPS (grid + commands dono yahi use karte hain)
# ══════════════════════════════════════════════════════════════════
@with_cache("tower", 1800, 86400)
def lookup_tower(term: Any) -> Dict[str, Any]:
    """🗼 10-digit mobile → tower/tracking location (viraj source, gateway me env-swappable)."""
    num = re.sub(r"\D", "", str(term or ""))
    if not _MOBILE_RE.match(num):
        return {"ok": False, "error": "10 digit Indian mobile number bhejo (6-9 se shuru)."}
    return _call("tower", num)


@with_cache("echallan", 600, 43200)
def lookup_echallan(term: Any) -> Dict[str, Any]:
    """📑 Gaadi number → Parivahan e-challan (ansh source, gateway env: CHALLAN_API_*)."""
    v = _clean_vehicle(term)
    if not _VEHICLE_RE.match(v):
        return {"ok": False, "error": "Gaadi number sahi format me bhejo — jaise DL8CAB1234"}
    return _call("challan", v)


@with_cache("fastag", 1800, 86400)
def lookup_fastag(term: Any) -> Dict[str, Any]:
    """🏷️ Gaadi number → FASTAG tags (abhigyan source, gateway env: FASTAG_API_URL)."""
    v = _clean_vehicle(term)
    if not _VEHICLE_RE.match(v):
        return {"ok": False, "error": "Gaadi number sahi format me bhejo — jaise RJ14CV0002"}
    return _call("fastag", v)


# ══════════════════════════════════════════════════════════════════
#  FORMATTERS (HTML cards — bot style: box header + fields + footer)
# ══════════════════════════════════════════════════════════════════
def _e(v: Any) -> str:
    """HTML-escape API value (ParseMode.HTML na toote)."""
    return html.escape(str(v if v is not None else ""))


def _rupee(n: Any) -> str:
    try:
        return f"₹{int(n):,}"
    except Exception:
        return str(n or "0")


def _ms(result: Dict[str, Any]) -> str:
    return str(result.get("ms") or 0)


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, (list, tuple, dict)):
        return not v
    s = str(v).strip().lower()
    return s in ("", "na", "none", "null", "-", "0 reports ( report complaint )")


# ---------- 🗼 TOWER ----------
_TOWER_PRIORITY = [
    "Number", "Tower Locations", "Mobile Locations", "Mobile State",
    "Refrence City", "Hometown", "Owner Name", "Owner Address",
    "SIM card", "Connection", "Country", "IMEI number", "IP address",
    "MAC address", "Tracker Id", "Tracking History", "Language",
    "Helpline", "Complaints", "Owner Personality",
]


def format_tower_card(result: Dict[str, Any]) -> str:
    d = result.get("data") or {}
    num = str(d.get("phone_number") or result.get("term") or "").strip()

    txt = (
        "\n╔══════════════════════════════════════╗\n"
        "║  🗼 <b>TOWER LOCATION TRACK</b>            ║\n"
        "╚══════════════════════════════════════╝\n\n"
        f"📱 <b>Number:</b> <code>{_e(num)}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    shown = set()
    # Priority order me pehle
    for k in _TOWER_PRIORITY:
        if k in d:
            shown.add(k)
            txt += _tower_field(k, d[k])
    # Phir baaki sab (infra keys chhod kar)
    for k, v in d.items():
        if k in shown or k in _SKIP_KEYS:
            continue
        txt += _tower_field(k, v)

    # Map link
    lat, lng = d.get("map_lat"), d.get("map_lng")
    if lat and lng:
        url = f"https://maps.google.com/?q={_e(lat)},{_e(lng)}"
        txt += f"🗺 <b>Map:</b> <a href=\"{url}\">Open Location ({_e(lat)}, {_e(lng)})</a>\n\n"

    txt += (
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡ <b>Response:</b> {_ms(result)}ms\n"
        "🔥 <b>Powered by @ANONYMOUS_XH</b>"
    )
    return txt


def _tower_field(k: str, v: Any) -> str:
    if _is_empty(v):
        return ""
    if k in ("Tracking History",) and isinstance(v, list):
        body = "\n".join(f"   • {_e(x)}" for x in v if x)
        return f"🕓 <b>{k}:</b>\n{body}\n\n"
    if isinstance(v, list):
        v = " · ".join(str(x) for x in v if x)
    s = _e(v)
    if len(s) > 300:
        s = s[:300] + "…"
    return f"🔹 <b>{_e(k)}:</b> {s}\n\n"


# ---------- 📑 E-CHALLAN ----------
def format_echallan_card(result: Dict[str, Any]) -> str:
    d = result.get("data") or {}
    veh = str(d.get("vehicle") or result.get("term") or "").strip().upper()
    total = d.get("total_count", 0)
    amount = d.get("total_amount", 0)
    queried = str(d.get("status_queried") or "").strip()

    txt = (
        "\n╔══════════════════════════════════════╗\n"
        "║  📑 <b>E-CHALLAN (PARIVAHAN)</b>            ║\n"
        "╚══════════════════════════════════════╝\n\n"
        f"🚗 <b>Vehicle:</b> <code>{_e(veh)}</code>\n"
        f"📊 <b>Total:</b> {_e(total)} challan(s) · <b>{_rupee(amount)}</b>\n"
    )
    if queried:
        txt += f"🔎 <b>Status queried:</b> {_e(queried)}\n"
    txt += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n"

    results = d.get("results") or {}
    if not isinstance(results, dict) or not results:
        txt += "\n❌ Koi challan record nahi mila.\n"
    else:
        for status, grp in list(results.items())[:4]:
            if not isinstance(grp, dict):
                continue
            gcount = grp.get("count", 0)
            gamt = grp.get("total_amount", 0)
            txt += f"\n🗂 <b>{_e(str(status).upper())}</b> — {_e(gcount)} · <b>{_rupee(gamt)}</b>\n"
            for i, ch in enumerate((grp.get("challans") or [])[:5], 1):
                if not isinstance(ch, dict):
                    continue
                cn = ch.get("challan_number") or ch.get("id") or "?"
                date = str(ch.get("challan_date") or "")[:10]
                amt = _rupee(ch.get("amount"))
                line = f"   {i}. <code>{_e(cn)}</code> · {_e(date)} · <b>{amt}</b>"
                txt += line + "\n"
                who = str(ch.get("accused_name") or "").strip()
                src = str(ch.get("source") or "").strip()
                if who or src:
                    parts = []
                    if who:
                        parts.append(f"👤 {_e(who)}")
                    if src:
                        parts.append(f"📍 {_e(src)}")
                    txt += "      " + " · ".join(parts) + "\n"
                cd = ch.get("court_data")
                if isinstance(cd, dict) and cd.get("is_virtual_court"):
                    txt += "      🏛 Virtual Court\n"
            more = int(gcount or 0) - min(int(gcount or 0), 5)
            if more > 0:
                txt += f"   … +{more} aur (gateway pe poora data safe hai)\n"

    txt += (
        "\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡ <b>Response:</b> {_ms(result)}ms\n"
        "🔥 <b>Powered by @ANONYMOUS_XH</b>"
    )
    return txt


# ---------- 🏷️ FASTAG ----------
def format_fastag_card(result: Dict[str, Any]) -> str:
    d = result.get("data") or {}
    tags = d.get("tags") or []
    reg = ""
    for t in tags:
        if isinstance(t, dict) and t.get("reg_number"):
            reg = str(t["reg_number"])
            break
    reg = reg or str(result.get("term") or "").strip().upper()

    txt = (
        "\n╔══════════════════════════════════════╗\n"
        "║  🏷️ <b>FASTAG INFO</b>                     ║\n"
        "╚══════════════════════════════════════╝\n\n"
        f"🚗 <b>Vehicle:</b> <code>{_e(reg)}</code>\n"
        f"📋 <b>Tags:</b> {_e(d.get('count', len(tags)))} total · "
        f"✅ {_e(d.get('active_count', 0))} active\n"
    )
    msg = str(d.get("message") or "").strip()
    if msg:
        txt += f"ℹ️ {_e(msg)}\n"
    txt += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n"

    if not isinstance(tags, list) or not tags:
        txt += "\n❌ Koi FASTAG tag nahi mila.\n"
    else:
        for i, t in enumerate(tags[:8], 1):
            if not isinstance(t, dict):
                continue
            bank = str(t.get("bank_name") or "Unknown Bank")
            st = str(t.get("status") or "?")
            icon = "🟢" if st.lower() == "active" else "⚫"
            vc = str(t.get("vehicle_class") or "").strip()
            iss = str(t.get("issue_date") or "").strip()
            txt += f"\n{icon} <b>{_e(bank)}</b> — {_e(st)}\n"
            meta = " · ".join(x for x in [_e(vc) if vc else "", f"Issued {_e(iss)}" if iss else ""] if x)
            if meta:
                txt += f"   {meta}\n"
            if t.get("tag_id"):
                txt += f"   🪪 <code>{_e(str(t['tag_id'])[:28])}</code>\n"

    txt += (
        "\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡ <b>Response:</b> {_ms(result)}ms\n"
        "🔥 <b>Powered by @ANONYMOUS_XH</b>"
    )
    return txt
