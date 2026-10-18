# -*- coding: utf-8 -*-
"""
modules.udb_cards — v2.6: @utility_duniya_bot (bot-1) se port kiye gaye
tool cards + prompts (RC/CHALLAN, VEHICLE TO NUMBER, AADHAAR TO NUMBER,
BSEB RESULT CHECK). Bot-1 jaisa EXACT look.
"""
from html import escape as hesc
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from modules import userapi as uapi
from modules import bseb_result as bseb

PCARD_MID = "━━━━━━━━━━━━━━━━━━━━━━"
BRAND_LINK = '🔥 Powered by <a href="https://t.me/himanshu_1111">@himanshu_1111</a>'


def to_bold(text: str) -> str:
    return text



PROMPT_DATA = {
    "numinfo": {
        "head": "📱 NUMBER INFO V2 ENGINE",
        "ask": "10 Digit Number bhejein:",
        "ex": [('7857843092', '10 digit ka mobile number')],
        "tip": '+91 ya 0 pehle lagane ki zaroorat nahi — seedha 10 digit bhejo',
        "foot": 'Circle · operator · owner card',
    },
    "familyinfo": {
        "head": "👪 FAMILY INFO",
        "ask": "12-digit Aadhaar number bhejein:",
        "ex": [('401635555849', '12-digit Aadhaar number')],
        "tip": 'Aadhaar hamesha masked rehta hai (XXXX-XXXX-1234) — poora kabhi nahi dikhta',
        "foot": 'Ration card · family members · eKYC',
    },
    "rc": {
        "head": "🚘 VEHICLE & CHALLAN",
        "ask": "Gaadi ka number bhejein (RC + Challan):",
        "ex": [('BR30AR0802', 'bina space ke gaadi number (jaise BR30AR0802)')],
        "tip": 'Space ya dash lagao to bhi chalega — naya engine RC + Challan dono laata hai',
        "foot": 'Owner · model · RTO · insurance · PUC · fitness · challan list',
    },
    "vehicletomobile": {
        "head": "📲 VEHICLE TO NUMBER",
        "ask": "Gaadi ka number bhejein (RC → Mobile):",
        "ex": [('KL41V3504', 'gaadi number — RC se mobile number')],
        "tip": 'RC number se owner ka mobile number milega',
        "foot": 'Mobile number from RC',
    },
    "aadhaar2num": {
        "head": "🪪 AADHAAR TO NUMBER",
        "ask": "12-digit Aadhaar number bhejein (Aadhaar → Mobile list):",
        "ex": [('401635555849', 'Aadhaar se mobile numbers')],
        "tip": 'Aadhaar se jude mobile numbers ki list',
        "foot": 'Mobile numbers linked to Aadhaar',
    },
    "tgnum": {
        "head": "🆩 TELEGRAM NUMBER",
        "ask": "Telegram username ya user ID bhejein:",
        "ex": [('@Perfectamit65', 'Telegram username — @ ke saath (real example)')],
        "tip": 'Username @ ke saath ya bina @ ke, ya numeric ID — jaise @Perfectamit65 ya 5685588580',
        "foot": 'Username/ID se juda mobile number',
    },
    "paknum": {
        "head": "🇵🇰 PAK NUMBER / CNIC",
        "ask": "Pakistani mobile number YA 13-digit CNIC bhejein:",
        "ex": [('03406955998', 'mobile — 03 se shuru, kul 11 digit'),
               ('3520113625763', 'CNIC — poore 13 digit, bina dash')],
        "tip": '+92 ya 0092 lagao to bhi chalega — bot khud 03... bana lega. CNIC se bhi wahi record milta hai.',
        "foot": 'Naam · CNIC · number · address · operator',
    },
    "result": {
        "head": "📋 RESULT CHECK — BSEB",
        "ask": "Pehle exam chuno (neeche button se):",
        "ex": [('22050 2600046', 'roll code + roll number')],
        "tip": 'Sirf Bihar Board (BSEB). Result season ke bahar board data hata deta hai',
        "foot": 'Naam · pita · school · subject-wise marks · division',
    },
}


def tool_prompt(action: str) -> str:
    """Tool ka prompt (bot-1 v102 plain format) — head + divider + ask + example."""
    d = PROMPT_DATA.get(action)
    if not d:
        return ""
    head = str(d.get("head") or "")
    if " " in head:
        _icon, _rest = head.split(" ", 1)
        L = [f"{_icon} <b>{_rest}</b>", PCARD_MID]
    else:
        L = [f"<b>{head}</b>", PCARD_MID]
    L.append("")
    L.append(f"🔗 <b>{hesc(str(d.get('ask') or ''))}</b>")
    ex = d.get("ex") or []
    if ex:
        L.append("")
        L.append(f"     <code>{hesc(str(ex[0][0]))}</code>")
    return "\n".join(L)


def pcard_sep() -> str:
    """Separator — pehle aur baad me khali line (card saaf-suthra dikhe)."""
    return "\n" + PCARD_MID + "\n"


def vehicle_rc_card(res: dict) -> str:
    """v2.6 — RC + CHALLAN full report (vehicle_full primary unmasked + fallback).
    New fields: chassis, engine, owner_father, mobile, financer, insurance_company/policy, etc.
    """
    res = res if isinstance(res, dict) else {}
    data = res.get("data") or {}
    if not data:
        data = res
    if not data.get("owner_name") and not data.get("registration_number") and res.get("fields"):
        cfg = {"icon": "🚗", "label": "RC + CHALLAN"}
        L = [f"{cfg['icon']} <b>{cfg['label']} — {hesc(str(res.get('term') or ''))}</b>", PCARD_MID, ""]
        for lbl, val in (res.get("fields") or []):
            L.append(f"{lbl} <b>:</b> {hesc(str(val))}")
        L.append("")
        L.append(f"⚡ <b>Response:</b> {int(res.get('ms') or 0)}ms")
        L.append(BRAND_LINK)
        return "\n".join(L)
    def _g(k, d=""):
        v = data.get(k)
        if v is None or v == "" or str(v).upper() == "NA":
            return d
        return str(v).strip()
    def _h(txt):
        return hesc(txt)
    reg = _g("registration_number") or _g("reg_no") or _g("term") or res.get("term") or ""
    owner = _g("owner_name") or _g("owner") or "NA"
    owner_father = _g("owner_father_name") or _g("father_name") or ""
    model = _g("model") or _g("maker_model") or _g("vehicle") or ""
    maker = _g("manufacturer") or _g("maker") or ""
    vclass = _g("vehicle_class") or ""
    fuel = _g("fuel_type") or ""
    city = _g("city") or ""
    rto = _g("rto") or _g("rto_code") or ""
    addr = _g("address") or ""
    phone = _g("mobile_number") or _g("mobile") or _g("phone") or "NA"
    reg_date = _g("registration_date") or _g("reg_date") or ""
    fitness = _g("fitness_upto") or ""
    ins_upto = _g("insurance_upto") or ""
    ins_comp = _g("insurance_company") or ""
    ins_policy = _g("insurance_policy_number") or _g("insurance_policy") or ""
    puc_upto = _g("pucc_upto") or _g("puc_upto") or ""
    puc_no = _g("pucc_number") or _g("puc_number") or ""
    engine = _g("engine_number") or _g("engine") or _g("engine_cc") or ""
    chassis = _g("chassis_number") or _g("chassis") or ""
    financer = _g("financer") or _g("financer_name") or ""
    rc_status = _g("rc_status") or "ACTIVE"
    tax = _g("tax_upto") or ""
    age = _g("vehicle_age") or ""
    seat = _g("seat_capacity") or ""
    variant = _g("variant") or ""
    color = _g("color") or ""
    cubic = _g("cubic_capacity") or ""
    norms = _g("norms_type") or ""
    manu_month = _g("manufacturing_month_year") or ""
    challans = data.get("challan_details") or []
    summary = data.get("challan_summary") or {}
    L = []
    L.append("╔════════════════════════════╗")
    L.append("🚘 <b>𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢 𝗥𝗘𝗣𝗢𝗥𝗧</b>")
    L.append("╚════════════════════════════╝")
    L.append("")
    L.append("🚗 <b>VEHICLE INFORMATION</b>")
    L.append(f"🔢 Number: <code>{_h(reg)}</code>")
    L.append("━━━━━━━━━━━━━━━━━━━━")
    L.append(f"├ 👤 Owner: {_h(owner)}")
    if owner_father:
        L.append(f"├ 👨 Father: {_h(owner_father)}")
    if model or maker:
        _mm = f"{maker} {model}".strip()
        L.append(f"├ 🚘 Model: {_h(_mm)}")
    if variant:
        L.append(f"├ 🏷️ Variant: {_h(variant)}")
    if vclass:
        L.append(f"├ 🏍️ Class: {_h(vclass)}")
    if fuel:
        L.append(f"├ ⛽ Fuel: {_h(fuel)}")
    if city:
        L.append(f"├ 🏙️ City: {_h(city)}")
    L.append(f"📞 Phone: {_h(phone)}")
    if rto:
        L.append(f"📍 RTO: {_h(rto)}")
    if addr:
        L.append(f"🏠 Address:")
        L.append(f"{_h(addr[:160])}")
    L.append("━━━━━━━━━━━━━━━━━━━━")
    L.append("")
    L.append("🏍️ <b>Technical & RC Specifications</b>")
    L.append(f"├ 🆔 RC Status : {'✅ ' + _h(rc_status) if 'ACTIVE' in rc_status.upper() else _h(rc_status)}")
    if color:
        L.append(f"├ 🎨 Color : {_h(color)}")
    if chassis:
        L.append(f"├ 🔧 Chassis : <code>{_h(chassis)}</code>")
    if engine:
        L.append(f"├ ⚙️ Engine : <code>{_h(engine)}</code>")
    if cubic:
        L.append(f"├ 🔩 CC : {_h(cubic)}")
    if seat:
        L.append(f"├ 💺 Seats : {_h(seat)}")
    if norms:
        L.append(f"├ 📏 Norms : {_h(norms)}")
    if manu_month:
        L.append(f"├ 📅 Mfg : {_h(manu_month)}")
    if reg_date:
        L.append(f"├ 📅 Reg Date : {_h(reg_date)}")
    if ins_upto or ins_comp or ins_policy:
        _ins = " ".join([x for x in [ins_comp, ins_policy, ins_upto] if x])[:180]
        L.append(f"├ 🛡️ Insurance : {_h(_ins)}")
    if puc_upto or puc_no:
        _puc = " ".join([x for x in [puc_no, puc_upto] if x])[:120]
        L.append(f"├ 🌫️ PUC : {_h(_puc)}")
    if financer:
        L.append(f"└ 🏦 Finance : {_h(financer)}")
    else:
        L.append(f"└ 🏦 Finance : NA")
    if tax or age or fitness:
        L.append("")
        if tax:
            L.append(f"💰 Tax Upto: {_h(tax)}")
        if fitness:
            L.append(f"📋 Fitness Upto: {_h(fitness)}")
        if age:
            L.append(f"⏳ Age: {_h(age)}")
    L.append("")
    L.append("━━━━━━━━━━━━━━━━━━━━")
    L.append("")
    L.append("🚨 <b>Challan Summary (Engine 1)</b>")
    if summary:
        total = summary.get("total_challans") or summary.get("challan_summary",{}).get("total_challans") or ""
        amount = summary.get("total_amount") or summary.get("challan_summary",{}).get("total_amount") or ""
        if total or amount:
            if total:
                L.append(f"📊 Total Challans: {_h(str(total))}")
            if amount:
                L.append(f"💰 Total Amount: ₹{_h(str(amount))}")
        else:
            L.append("⚠️ Challan details temporarily live track status failed.")
    else:
        L.append("⚠️ Challan details temporarily live track status failed.")
    L.append("")
    L.append("━━━━━━━━━━━━━━━━━━━━")
    if challans:
        L.append("🚨 <b>CHALLAN INFO V2 (Backup Engine)</b>")
        L.append("")
        for ch in challans[:5]:
            cn = ch.get("challan_number") or ch.get("challan_no") or ""
            accused = ch.get("accused_name") or ""
            amt = ch.get("amount") or ch.get("challan_amount") or ""
            date = ch.get("challan_date") or ch.get("date") or ""
            status = ch.get("challan_status") or ch.get("status") or ""
            offence = ch.get("offense_details") or ch.get("offence") or ""
            if cn:
                L.append(f"🔹 Challan #: <code>{_h(cn)}</code>")
            if accused:
                L.append(f"   👤 Accused: {_h(accused)}")
            if amt:
                try:
                    amt_i = int(str(amt).replace(",",""))
                    amt_fmt = f"{amt_i:,}"
                except:
                    amt_fmt = str(amt)
                L.append(f"   💰 Amount: ₹{_h(amt_fmt)}")
            if date:
                L.append(f"   📅 Date: {_h(str(date))}")
            if status:
                L.append(f"   ❌ Status: {_h(str(status).upper())}")
            if offence:
                L.append(f"   🛑 Offence: {_h(str(offence).upper())}")
            L.append("")
        L.append("━━━━━━━━━━━━━━━━━━━━")
    else:
        L.append("🚨 <b>CHALLAN INFO V2 (Backup Engine)</b>")
        L.append("")
        L.append("✅ No pending challan found.")
        L.append("")
        L.append("━━━━━━━━━━━━━━━━━━━━")
    ms = int(res.get("ms") or res.get("response_time") or 0)
    L.append(f"⚡ Response: {ms}ms" + (" · cached" if res.get("cached") else ""))
    L.append(BRAND_LINK)
    return "\n".join(L)


def vehicletomobile_card(res: dict) -> str:
    """📲 Vehicle → Mobile card (vehicle_to_number) v127.2 — shows RC details even when mobile not in DB."""
    res = res if isinstance(res, dict) else {}
    data = res.get("data") or res
    reg = str(data.get("registration_number") or data.get("reg_no") or res.get("term") or "").upper()
    mob = str(data.get("mobile_number") or data.get("mobile") or data.get("phone") or "").strip()
    owner = str(data.get("owner_name") or data.get("owner") or "").strip()
    model = str(data.get("model") or data.get("vehicle") or "").strip()
    L = [f"📲 <b>VEHICLE TO NUMBER — {hesc(reg)}</b>", PCARD_MID, ""]
    if mob:
        L.append(f"📱 <b>Mobile:</b> <code>{hesc(mob)}</code>")
    else:
        L.append(f"❌ <b>Mobile DB me nahi hai</b> (sarkari record me mobile nahi)")
        if owner:
            L.append(f"👤 <b>Owner:</b> {hesc(owner)}")
        if model:
            L.append(f"🚘 <b>Model:</b> {hesc(model)}")
        if data.get("rto"):
            L.append(f"🏢 <b>RTO:</b> {hesc(str(data.get('rto')))}")
    L.append("")
    L.append(f"🔢 <b>RC:</b> <code>{hesc(reg)}</code>")
    if owner and mob:
        L.append(f"👤 <b>Owner:</b> {hesc(owner)}")
    L.append("")
    L.append(f"⚡ <b>Response:</b> {int(res.get('ms') or 0)}ms")
    L.append(BRAND_LINK)
    return "\n".join(L)


def aadhaar2num_card(res: dict) -> str:
    """🪪 Aadhaar → Mobile list card."""
    res = res if isinstance(res, dict) else {}
    data = res.get("data") or {}
    term = str(res.get("term") or data.get("aadhaar") or data.get("aadharNumber") or "").strip()
    records = data.get("data") or data.get("records") or []
    if isinstance(data, list):
        records = data
    count = data.get("count") or len(records) if isinstance(records, list) else 0
    L = [f"🪪 <b>AADHAAR TO NUMBER — {hesc(term)}</b>", PCARD_MID, ""]
    L.append(f"📊 <b>Total Records:</b> {count}")
    L.append("")
    for i, rec in enumerate(records[:10], 1):
        if not isinstance(rec, dict):
            continue
        name = rec.get("name") or rec.get("fullName") or "—"
        father = rec.get("fathersName") or rec.get("father") or ""
        phone = rec.get("phoneNumber") or rec.get("mobile") or rec.get("phone") or ""
        other = rec.get("otherNumber") or rec.get("alt") or ""
        addr = rec.get("address") or rec.get("addr") or ""
        aad = rec.get("aadharNumber") or rec.get("aadhaar") or term
        L.append(f"👤 <b>{i}. {hesc(str(name))}</b>")
        if father:
            L.append(f"   👨 Father: {hesc(str(father))}")
        if phone:
            L.append(f"   📱 Phone: <code>{hesc(str(phone))}</code>")
        if other:
            L.append(f"   📱 Alt: <code>{hesc(str(other))}</code>")
        if aad:
            L.append(f"   🆔 Aadhaar: <code>{hesc(str(aad))}</code>")
        if addr:
            L.append(f"   🏠 {hesc(str(addr)[:160])}")
        L.append("")
    if count > len(records):
        L.append(f"<i>…aur {count - len(records)} aur</i>")
        L.append("")
    L.append(f"⚡ <b>Response:</b> {int(res.get('ms') or 0)}ms")
    L.append(BRAND_LINK)
    return "\n".join(L)


def userapi_card(res: dict, kind: str) -> str:
    """🚗 RC + CHALLAN + new tools card."""
    res = res if isinstance(res, dict) else {}
    # v127: RC uses vehicle_rc_card
    if kind == "rc":
        try:
            return vehicle_rc_card(res)
        except Exception:
            pass
    if kind == "vehicletomobile":
        try:
            return vehicletomobile_card(res)
        except Exception:
            pass
    if kind == "aadhaar2num":
        try:
            return aadhaar2num_card(res)
        except Exception:
            pass
    cfg = uapi.TOOLS.get(kind, {"icon": "🔎", "label": "INFO"})
    L = [f"{cfg['icon']} <b>{cfg['label']} — {hesc(str(res.get('term') or ''))}</b>",
         PCARD_MID, ""]
    for lbl, val in (res.get("fields") or []):
        L.append(f"{lbl} <b>:</b> {hesc(str(val))}")
    extra = res.get("extra") or {}
    if extra:
        L.append("")
        L.append("📋 <b>Baaki details:</b>")
        for k, v in extra.items():
            L.append(f"   • <b>{hesc(str(k))}:</b> {hesc(str(v))}")
    _rawt = str(res.get("raw_text") or "").strip()
    if _rawt:
        L.append("")
        L.append(f"<pre>{hesc(_rawt[:1500])}</pre>")
    L.append("")
    L.append(f"⚡ <b>Response:</b> {int(res.get('ms') or 0)}ms"
             + ("  ·  <i>cached</i>" if res.get("cached") else ""))
    L.append(BRAND_LINK)
    return "\n".join([x for x in L if x is not None])


def result_card(st: dict, exam_label: str, year) -> str:
    """📋 RESULT CHECK — BSEB marksheet card (PDF ki jagah saaf text)."""
    st = st if isinstance(st, dict) else {}
    L = [f"📋 <b>{hesc(str(exam_label))} — {hesc(str(year))}</b>",
         PCARD_MID, ""]
    for lbl, key in (("👤 <b>Naam:</b>", "name"),
                     ("👨 <b>Pita:</b>", "father"),
                     ("👩 <b>Mata:</b>", "mother"),
                     ("🔢 <b>Roll Code:</b>", "roll_code"),
                     ("🎫 <b>Roll No:</b>", "roll_no"),
                     ("🪪 <b>Reg. No:</b>", "reg_no"),
                     ("🏫 <b>School:</b>", "school"),
                     ("📅 <b>DOB:</b>", "dob"),
                     ("⚧ <b>Gender:</b>", "gender"),
                     ("📚 <b>Faculty:</b>", "faculty")):
        v = st.get(key)
        if v:
            L.append(f"{lbl} {hesc(str(v))}")

    subs = st.get("subjects") or []
    if subs:
        L.append("")
        L.append("📝 <b>SUBJECT-WISE MARKS</b>")
        L.append(PCARD_MID)
        for s in subs[:15]:
            try:
                L.append(bseb._sub_line(s))
            except Exception:                                # noqa: BLE001
                nm = hesc(str(s.get("name") or s.get("subject") or "—"))
                L.append(f"   • {nm}: {hesc(str(s.get('total') or ''))}")

    def _n(v):
        """492.0 → 492 (marks me .0 bura lagta hai)."""
        try:
            f = float(v)
            return str(int(f)) if f == int(f) else str(f)
        except Exception:                                        # noqa: BLE001
            return str(v)

    L.append("")
    tot = st.get("total")
    if tot not in (None, ""):
        full = st.get("full_marks") or st.get("out_of")
        L.append(f"🏆 <b>Total:</b>     {hesc(_n(tot))}"
                 + (f" / {hesc(_n(full))}" if full else ""))
    for lbl, key in (("📊 <b>Percent:</b>", "percent"),
                     ("🥇 <b>Division:</b>", "division"),
                     ("✅ <b>Result:</b>", "result_status")):
        v = st.get(key)
        if v:
            L.append(f"{lbl}   {hesc(str(v))}")
    if st.get("is_topper"):
        L.append("🌟 <b>TOPPER!</b> 🎉")

    L.append("")
    try:
        L.append(bseb.MEDIA_NOTE)
    except Exception:                                        # noqa: BLE001
        pass
    L.append(BRAND_LINK)
    return "\n".join([x for x in L if x is not None])


def result_pick_text() -> str:
    """📋 RESULT CHECK ka step 1 — kaunsa exam?"""
    return ("📋 <b>RESULT CHECK — BIHAR BOARD</b>\n"
            f"{PCARD_MID}\n\n"
            "Pehle batao <b>kaunsa exam</b> hai 👇\n\n"
            f"<i>Saal: {bseb.CURRENT_YEAR}</i>")


def result_pick_kb():
    """Exam chunne ke inline buttons (bseb.EXAMS se khud bante hain)."""
    rows = []
    for key, ex in bseb.EXAMS.items():
        rows.append([InlineKeyboardButton(str(ex.get("btn") or ex.get("short") or key),
                                          callback_data=f"rs:{key}")])
    return InlineKeyboardMarkup(rows)


def result_ask_roll_text(exam_key: str) -> str:
    """Step 2 — roll code + roll number maango."""
    ex = bseb.EXAMS.get(exam_key, {})
    return (f"📋 <b>{hesc(str(ex.get('label') or 'BSEB'))} — {bseb.CURRENT_YEAR}</b>\n"
            f"{PCARD_MID}\n\n"
            "Ab bhejo: <b>Roll Code + Roll Number</b>\n\n"
            "📌 <b>Jaise:</b> <code>22050 2600046</code>\n"
            "<i>(pehle roll code, space, phir roll number)</i>")


_TYPING_STOP: dict = {}
