"""
Website Extractor - Emails, Phones, Links, Meta Tags
100% working, no API key needed
"""

import re
import requests
from .fast_cache import with_cache
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import socket

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def extract_emails(text: str) -> List[str]:
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    # Filter and dedup
    emails = list(set([e.lower() for e in emails if not e.lower().endswith(('.png','.jpg','.jpeg','.gif','.webp'))]))
    return emails[:50]

def extract_phones(text: str) -> List[str]:
    # Indian + international
    phones = re.findall(r'(\+91[\s-]?\d{10}|\b\d{10}\b|\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', text)
    phones = [re.sub(r'\s+', ' ', p).strip() for p in phones]
    # Deduplicate and filter valid
    unique = []
    seen = set()
    for p in phones:
        digits = re.sub(r'\D', '', p)
        if len(digits) >= 10 and digits not in seen:
            seen.add(digits)
            unique.append(p)
    return unique[:50]

def extract_links(html: str, base_url: str) -> Dict[str, List[str]]:
    soup = BeautifulSoup(html, 'html.parser')
    internal = []
    external = []
    base_domain = urlparse(base_url).netloc

    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        if parsed.netloc == base_domain or not parsed.netloc:
            internal.append(full_url)
        else:
            external.append(full_url)

    return {
        "internal": list(set(internal))[:100],
        "external": list(set(external))[:100],
        "total": len(internal) + len(external)
    }

def extract_meta(html: str, url: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, 'html.parser')
    
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    
    desc = ""
    desc_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
    if desc_tag and desc_tag.get('content'):
        desc = desc_tag['content'].strip()

    keywords = ""
    kw_tag = soup.find('meta', attrs={'name': 'keywords'})
    if kw_tag and kw_tag.get('content'):
        keywords = kw_tag['content'].strip()

    og_image = ""
    og_tag = soup.find('meta', attrs={'property': 'og:image'})
    if og_tag and og_tag.get('content'):
        og_image = og_tag['content'].strip()

    favicon = ""
    icon_tag = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
    if icon_tag and icon_tag.get('href'):
        favicon = urljoin(url, icon_tag['href'])

    # Headings
    h1 = [h.get_text().strip() for h in soup.find_all('h1')][:5]
    h2 = [h.get_text().strip() for h in soup.find_all('h2')][:10]

    return {
        "title": title[:200],
        "description": desc[:500],
        "keywords": keywords[:500],
        "og_image": og_image,
        "favicon": favicon,
        "h1": h1,
        "h2": h2,
    }

@with_cache("web", 1800, 21600)
def website_extractor(url: str) -> Dict[str, Any]:
    if not url.startswith('http'):
        url = 'https://' + url

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code} - Site not accessible"}

        html = r.text
        # v2.8 ultra-fast: 3MB+ pages ka parse cap (bade pages pe BS4 slow hota hai)
        if len(html) > 3_000_000:
            html = html[:3_000_000]
        text = BeautifulSoup(html, 'html.parser').get_text()

        emails = extract_emails(html + " " + text)
        phones = extract_phones(html + " " + text)
        links = extract_links(html, url)
        meta = extract_meta(html, url)

        return {
            "ok": True,
            "url": url,
            "status_code": r.status_code,
            "emails": emails,
            "phones": phones,
            "links": links,
            "meta": meta,
            "text_length": len(text),
            "html_length": len(html),
        }
    except Exception as e:
        return {"ok": False, "error": f"Extractor error: {str(e)[:200]}"}
