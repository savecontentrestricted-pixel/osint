"""
Tool 3: Email OSINT (Public Data Only)
- Email validation
- Disposable check
- Gravatar check
- Breach check via HaveIBeenPwned API (free, no key for limited)
- Social lookup hints
"""

import re
import requests
import hashlib
from typing import Dict, Any

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

DISPOSABLE_DOMAINS = {
    "tempmail.com", "10minutemail.com", "guerrillamail.com", "mailinator.com",
    "yopmail.com", "throwaway.email", "temp-mail.org", "fakeinbox.com"
}

def validate_email(email: str) -> Dict[str, Any]:
    email = email.strip().lower()
    is_valid = bool(EMAIL_REGEX.match(email))
    domain = email.split('@')[1] if '@' in email else None
    is_disposable = domain in DISPOSABLE_DOMAINS if domain else False
    
    return {
        "email": email,
        "is_valid_format": is_valid,
        "domain": domain,
        "is_disposable": is_disposable,
        "is_free_provider": domain in {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "protonmail.com", "icloud.com"} if domain else False
    }

def gravatar_check(email: str) -> Dict[str, Any]:
    """Check if Gravatar exists"""
    email = email.strip().lower()
    email_hash = hashlib.md5(email.encode()).hexdigest()
    gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"
    try:
        r = requests.get(gravatar_url, timeout=10)
        exists = r.status_code == 200
        return {
            "has_gravatar": exists,
            "gravatar_url": f"https://www.gravatar.com/avatar/{email_hash}?d=identicon" if exists else None,
            "hash": email_hash
        }
    except Exception as e:
        return {"has_gravatar": False, "error": str(e), "hash": email_hash}

def breach_check(email: str) -> Dict[str, Any]:
    """
    Check HaveIBeenPwned - free API without key is rate limited, but we try
    Uses: https://haveibeenpwned.com/api/v3/breachedaccount/{email}
    Note: Official API needs key, so we use alternative free check via proxy or just note
    """
    # For demo, use HIBP free endpoint with User-Agent, may need key
    # We'll try with no key and handle 401
    try:
        headers = {"User-Agent": "OSINT-Tool", "hibp-api-key": ""}  # No key, will likely 401
        # Actually free check not allowed without key now, so we use alternative: https://api.xposedornot.com/v1/check-email/{email}
        r = requests.get(f"https://api.xposedornot.com/v1/check-email/{email}", timeout=15)
        if r.status_code == 200:
            data = r.json()
            breaches = data.get("breaches", [])
            return {
                "ok": True,
                "breached": len(breaches) > 0,
                "breach_count": len(breaches),
                "breaches": breaches[:10],  # first 10
                "source": "xposedornot.com"
            }
        else:
            return {"ok": False, "error": f"API {r.status_code}", "breached": None}
    except Exception as e:
        return {"ok": False, "error": str(e), "breached": None}

def email_osint(email: str) -> Dict[str, Any]:
    email = email.strip().lower()
    validation = validate_email(email)
    
    if not validation["is_valid_format"]:
        return {"ok": False, "error": "Invalid email format", "validation": validation}

    gravatar = gravatar_check(email)
    breach = breach_check(email)

    # Additional: check domain MX
    mx_records = []
    try:
        import dns.resolver
        domain = validation["domain"]
        answers = dns.resolver.resolve(domain, 'MX')
        mx_records = [str(r.exchange) for r in answers]
    except:
        pass

    result = {
        "ok": True,
        "email": email,
        "validation": validation,
        "gravatar": gravatar,
        "breach": breach,
        "mx_records": mx_records,
        "suggestions": []
    }

    if breach.get("breached"):
        result["suggestions"].append(f"⚠️ Email {breach.get('breach_count')} breaches me mila hai - password change karo!")
    if validation["is_disposable"]:
        result["suggestions"].append("⚠️ Disposable email hai - temporary")
    if gravatar.get("has_gravatar"):
        result["suggestions"].append("ℹ️ Gravatar profile exists - photo mil sakta hai")

    return result
