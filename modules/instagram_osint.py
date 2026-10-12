"""
Tool 2: Instagram OSINT (Public Data Only)
Uses public web scraping (no login) - extracts public profile info
Note: Instagram blocks heavily, uses best effort with fallback
"""

import requests
import re
import json
from typing import Dict, Any

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def instagram_osint(username: str) -> Dict[str, Any]:
    username = username.strip().lstrip('@').split('/')[0]
    if not username:
        return {"ok": False, "error": "Username empty"}

    # Try public page scraping
    try:
        url = f"https://www.instagram.com/{username}/"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 404:
            return {"ok": False, "error": f"User @{username} not found (404)"}
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code} - Instagram blocked or private"}

        html = r.text

        # Try to extract JSON from window._sharedData or similar
        # New Instagram uses JSON in script tags
        data = {}
        
        # Extract og: tags
        og_title = re.search(r'<meta property="og:title" content="([^"]+)"', html)
        og_desc = re.search(r'<meta property="og:description" content="([^"]+)"', html)
        og_image = re.search(r'<meta property="og:image" content="([^"]+)"', html)

        # Followers etc from description: "X Followers, Y Following, Z Posts"
        followers = following = posts = None
        bio = ""
        if og_desc:
            desc = og_desc.group(1)
            bio = desc
            # Example: "123 Followers, 45 Following, 67 Posts - See Instagram photos and videos from ..."
            m = re.search(r'([\d,\.KMB]+)\s+Followers', desc, re.I)
            if m:
                followers = m.group(1)
            m = re.search(r'([\d,\.KMB]+)\s+Following', desc, re.I)
            if m:
                following = m.group(1)
            m = re.search(r'([\d,\.KMB]+)\s+Posts', desc, re.I)
            if m:
                posts = m.group(1)

        # Try to find additional data in application/ld+json
        ld_json = re.search(r'<script type="application/ld\+json">([^<]+)</script>', html)
        ld_data = {}
        if ld_json:
            try:
                ld_data = json.loads(ld_json.group(1))
            except:
                pass

        result = {
            "ok": True,
            "username": username,
            "profile_url": url,
            "full_name": og_title.group(1) if og_title else None,
            "bio": bio,
            "followers": followers,
            "following": following,
            "posts": posts,
            "profile_pic": og_image.group(1) if og_image else None,
            "is_private": "private" in html.lower()[:2000] if followers is None else None,
            "raw_og": {
                "title": og_title.group(1) if og_title else None,
                "description": og_desc.group(1) if og_desc else None,
            }
        }
        return result

    except Exception as e:
        return {"ok": False, "error": f"Instagram OSINT error: {str(e)} - Instagram blocks scraping heavily, try later"}

def instagram_osint_advanced(username: str) -> Dict[str, Any]:
    """
    Placeholder for advanced version using Instaloader or API
    For now calls basic version
    """
    basic = instagram_osint(username)
    # Could add instaloader logic here if installed
    try:
        import instaloader
        L = instaloader.Instaloader()
        # Anonymous, no login - may still get blocked
        profile = instaloader.Profile.from_username(L.context, username)
        advanced_data = {
            "is_private": profile.is_private,
            "is_verified": profile.is_verified,
            "followers": profile.followers,
            "following": profile.followees,
            "posts_count": profile.mediacount,
            "bio": profile.biography,
            "external_url": profile.external_url,
            "is_business": profile.is_business_account,
            "business_category": profile.business_category_name,
        }
        # Merge
        basic.update(advanced_data)
        basic["method"] = "instaloader"
    except ImportError:
        basic["note"] = "Install instaloader for advanced data: pip install instaloader"
    except Exception as e:
        basic["advanced_error"] = str(e)

    return basic
