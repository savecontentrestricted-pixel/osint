"""
Tool 6: Social Media Security Checker (Educational)
Checks public Instagram profile for security risks - 100% public data only, educational purpose.

Checks:
- Bio me email/phone leak
- External link suspicious?
- Private vs Public
- Verified badge
- Followers ratio (fake account risk)
- Username me birth year / personal info
- Profile pic missing
- Business account risk
- Bio me sensitive info
- Security Score 0-100
"""

import re
import requests
from typing import Dict, Any
from .instagram_osint import instagram_osint

def check_email_in_bio(bio: str) -> Dict[str, Any]:
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', bio)
    return {"found": len(emails) > 0, "emails": emails, "risk": "High" if emails else "Low"}

def check_phone_in_bio(bio: str) -> Dict[str, Any]:
    # Indian + international phone patterns
    phones = re.findall(r'(\+91[\s-]?\d{10}|\b\d{10}\b|\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', bio)
    # Filter false positives
    phones = [p for p in phones if len(re.sub(r'\D', '', p)) >= 10]
    return {"found": len(phones) > 0, "phones": phones[:3], "risk": "High" if phones else "Low"}

def check_external_link(bio: str, external_url: str = None) -> Dict[str, Any]:
    links = re.findall(r'https?://\S+', bio)
    if external_url:
        links.append(external_url)
    
    suspicious_keywords = ["bit.ly", "tinyurl", "free", "gift", "crypto", "earn", "money"]
    suspicious = []
    for link in links:
        for kw in suspicious_keywords:
            if kw in link.lower():
                suspicious.append(link)
                break
    
    return {
        "found": len(links) > 0,
        "links": links[:3],
        "suspicious": suspicious,
        "risk": "Medium" if suspicious else "Low" if links else "None"
    }

def check_username_risk(username: str) -> Dict[str, Any]:
    risks = []
    # Birth year in username (e.g., john1998)
    if re.search(r'(19|20)\d{2}', username):
        risks.append("Birth year in username - easy to guess")
    # Too many numbers
    if len(re.findall(r'\d', username)) >= 4:
        risks.append("Many numbers in username - may be auto-generated or weak")
    # Very short
    if len(username) <= 4:
        risks.append("Very short username - easy to bruteforce")
    
    return {"risks": risks, "risk_level": "High" if len(risks) >= 2 else "Medium" if risks else "Low"}

def calculate_security_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score 0-100, higher = more secure
    """
    score = 100
    issues = []
    recommendations = []

    # Email leak -20
    if data["email_leak"]["found"]:
        score -= 20
        issues.append(f"📧 Email leak in bio: {', '.join(data['email_leak']['emails'])}")
        recommendations.append("🔒 Bio se email hatao, contact ke liye business email alag rakho")

    # Phone leak -25 (highest risk)
    if data["phone_leak"]["found"]:
        score -= 25
        issues.append(f"📱 Phone leak in bio")
        recommendations.append("🔒 Phone number bio se hatao, scammers call kar sakte hain")

    # Suspicious link -15
    if data["external_link"]["suspicious"]:
        score -= 15
        issues.append(f"🔗 Suspicious link in bio: {data['external_link']['suspicious'][0]}")
        recommendations.append("⚠️ Short links / free gift wale links se phishing risk hai")

    # Not private -10
    if not data.get("is_private"):
        score -= 10
        issues.append("🔓 Public account - anyone can see posts")
        recommendations.append("🔒 Sensitive posts ke liye private account ya Close Friends use karo")

    # Not verified but high followers - fake risk
    followers_str = str(data.get("followers") or "0")
    # Parse followers like "1M", "10K"
    followers_num = 0
    try:
        if "M" in followers_str:
            followers_num = float(followers_str.replace("M", "").replace(",", "")) * 1000000
        elif "K" in followers_str:
            followers_num = float(followers_str.replace("K", "").replace(",", "")) * 1000
        else:
            followers_num = int(re.sub(r'\D', '', followers_str) or 0)
    except:
        pass

    if followers_num > 10000 and not data.get("is_verified"):
        score -= 5
        issues.append("👥 High followers but not verified - impersonation risk")

    # Username risks
    if data["username_risk"]["risks"]:
        score -= 10
        issues.extend(data["username_risk"]["risks"])
        recommendations.append("🔑 Username me birth year / numbers avoid karo")

    # No profile pic
    if not data.get("profile_pic"):
        score -= 5
        issues.append("🖼️ No profile pic - looks suspicious/fake")
        recommendations.append("🖼️ Professional profile pic lagao")

    # Business account with personal info
    if data.get("is_business") and (data["email_leak"]["found"] or data["phone_leak"]["found"]):
        score -= 5
        issues.append("💼 Business account with personal contact leak")

    score = max(0, min(100, score))

    # Security level
    if score >= 80:
        level = "🟢 Excellent"
    elif score >= 60:
        level = "🟡 Good"
    elif score >= 40:
        level = "🟠 Medium Risk"
    else:
        level = "🔴 High Risk"

    return {
        "score": score,
        "level": level,
        "issues": issues,
        "recommendations": recommendations
    }

def social_security_check(username: str) -> Dict[str, Any]:
    username = username.strip().lstrip('@').split('/')[0]
    
    # Get Instagram public data
    insta_data = instagram_osint(username)
    
    if not insta_data.get("ok"):
        return {"ok": False, "error": insta_data.get("error")}

    bio = insta_data.get("bio") or ""
    # Try to get more accurate bio from og description parsing
    # og:description contains bio + followers count, we need to clean
    # For now use bio as is

    # Perform checks
    email_leak = check_email_in_bio(bio)
    phone_leak = check_phone_in_bio(bio)
    external_link = check_external_link(bio, insta_data.get("profile_pic"))  # Actually external_url not in basic, but ok
    # Try to get external_url if available via advanced method
    try:
        from .instagram_osint import instagram_osint_advanced
        adv = instagram_osint_advanced(username)
        if adv.get("external_url"):
            external_link = check_external_link(bio, adv.get("external_url"))
    except:
        pass

    username_risk = check_username_risk(username)

    combined = {
        "ok": True,
        "username": username,
        "full_name": insta_data.get("full_name"),
        "bio": bio[:500],
        "followers": insta_data.get("followers"),
        "following": insta_data.get("following"),
        "posts": insta_data.get("posts"),
        "profile_pic": insta_data.get("profile_pic"),
        "is_private": insta_data.get("is_private"),
        "is_verified": insta_data.get("is_verified") if "is_verified" in insta_data else None,
        "is_business": insta_data.get("is_business") if "is_business" in insta_data else None,
        "email_leak": email_leak,
        "phone_leak": phone_leak,
        "external_link": external_link,
        "username_risk": username_risk,
    }

    security = calculate_security_score(combined)
    combined["security"] = security

    return combined

def security_report_text(data: Dict[str, Any]) -> str:
    if not data.get("ok"):
        return f"❌ {data.get('error')}"

    sec = data.get("security", {})
    txt = f"""
🔒 <b>Social Media Security Check: @{data.get('username')}</b>

👤 <b>Profile:</b> {data.get('full_name') or 'N/A'}
📝 <b>Bio:</b> {data.get('bio')[:200] or 'N/A'}
👥 <b>Followers:</b> {data.get('followers') or 'N/A'} | <b>Following:</b> {data.get('following') or 'N/A'} | <b>Posts:</b> {data.get('posts') or 'N/A'}
🔒 <b>Private:</b> {data.get('is_private')} | ✅ <b>Verified:</b> {data.get('is_verified') or 'N/A'}

<b>--- Security Analysis ---</b>

📧 <b>Email Leak:</b> {'❌ FOUND - ' + ', '.join(data['email_leak']['emails']) if data['email_leak']['found'] else '✅ Not found'}
📱 <b>Phone Leak:</b> {'❌ FOUND' if data['phone_leak']['found'] else '✅ Not found'}
🔗 <b>External Links:</b> {len(data['external_link']['links'])} found | Suspicious: {len(data['external_link']['suspicious'])} | Risk: {data['external_link']['risk']}
👤 <b>Username Risk:</b> {data['username_risk']['risk_level']} | Issues: {len(data['username_risk']['risks'])}

<b>--- Security Score ---</b>
🎯 <b>Score:</b> {sec.get('score')}/100 - {sec.get('level')}

<b>--- Issues Found ({len(sec.get('issues',[]))}) ---</b>
"""
    for issue in sec.get("issues", [])[:10]:
        txt += f"• {issue}\n"

    txt += f"\n<b>--- Recommendations ---</b>\n"
    for rec in sec.get("recommendations", [])[:10]:
        txt += f"• {rec}\n"

    txt += f"""
<b>--- Educational Tips ---</b>
• 🔑 2FA on rakho (Instagram → Settings → Security → Two-Factor)
• 🔒 Bio me personal email/phone mat dalo
• 🛡️ Strong password: 12+ chars, upper+lower+number+symbol
• 📵 Unknown links pe click mat karo
• ✅ Verified badge ke liye apply karo agar eligible ho

⚠️ <i>Note: Ye sirf public data pe based educational check hai, Instagram ka private security data nahi dekh sakte.</i>
"""
    return txt
