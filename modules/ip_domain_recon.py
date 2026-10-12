"""
Tool 4: IP & Domain Recon - OSINT
Features:
- IP lookup (location, ISP, VPN/proxy detection, blacklist)
- Domain WHOIS
- DNS records (A, MX, NS, TXT, CNAME)
- SSL certificate info
- Hosting detection
"""

import socket
import ssl
import json
import requests
from datetime import datetime
from typing import Dict, Any, List
import re

# Free APIs - no key needed
IP_API_URL = "http://ip-api.com/json/{ip}?fields=status,message,continent,country,regionName,city,zip,lat,lon,timezone,isp,org,as,proxy,hosting,query,reverse"

def ip_lookup(ip: str) -> Dict[str, Any]:
    """IP geolocation + ISP + VPN detection using ip-api.com (free, no key)"""
    ip = ip.strip()
    # Validate IP
    try:
        socket.inet_aton(ip)
    except:
        # Try resolve if domain given
        try:
            ip = socket.gethostbyname(ip)
        except:
            return {"ok": False, "error": f"Invalid IP/Domain: {ip}"}

    try:
        r = requests.get(IP_API_URL.format(ip=ip), timeout=10)
        data = r.json()
        if data.get("status") != "success":
            return {"ok": False, "error": data.get("message", "IP lookup failed")}

        # Additional checks
        is_vpn = data.get("proxy", False) or data.get("hosting", False)
        
        result = {
            "ok": True,
            "ip": data.get("query"),
            "reverse_dns": data.get("reverse"),
            "continent": data.get("continent"),
            "country": data.get("country"),
            "region": data.get("regionName"),
            "city": data.get("city"),
            "zip": data.get("zip"),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "timezone": data.get("timezone"),
            "isp": data.get("isp"),
            "org": data.get("org"),
            "as": data.get("as"),
            "is_proxy": data.get("proxy"),
            "is_hosting": data.get("hosting"),
            "is_vpn_proxy": is_vpn,
            "google_maps": f"https://www.google.com/maps?q={data.get('lat')},{data.get('lon')}" if data.get('lat') else None,
        }
        return result
    except Exception as e:
        return {"ok": False, "error": f"IP lookup error: {str(e)}"}

def dns_lookup(domain: str) -> Dict[str, Any]:
    """DNS records lookup using socket + dnspython fallback"""
    domain = domain.strip().lower()
    domain = re.sub(r'^https?://', '', domain)
    domain = domain.split('/')[0]
    
    result = {"ok": True, "domain": domain, "records": {}}
    
    # A record
    try:
        a_records = socket.gethostbyname_ex(domain)[2]
        result["records"]["A"] = a_records
        result["ip"] = a_records[0] if a_records else None
    except Exception as e:
        result["records"]["A"] = f"Error: {str(e)}"

    # Try dnspython if available
    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        
        for rtype in ["MX", "NS", "TXT", "CNAME", "AAAA"]:
            try:
                answers = resolver.resolve(domain, rtype)
                result["records"][rtype] = [str(r) for r in answers]
            except Exception:
                result["records"][rtype] = []
    except ImportError:
        # dnspython not installed, use basic
        result["records"]["MX"] = "Install dnspython for MX lookup"
    except Exception as e:
        pass

    return result

def whois_lookup(domain: str) -> Dict[str, Any]:
    """WHOIS lookup - tries python-whois, fallback to API"""
    domain = domain.strip().lower()
    domain = re.sub(r'^https?://', '', domain)
    domain = domain.split('/')[0]

    # Try python-whois
    try:
        import whois
        w = whois.whois(domain)
        result = {
            "ok": True,
            "domain": domain,
            "registrar": w.registrar,
            "whois_server": w.whois_server,
            "creation_date": str(w.creation_date) if w.creation_date else None,
            "expiration_date": str(w.expiration_date) if w.expiration_date else None,
            "updated_date": str(w.updated_date) if w.updated_date else None,
            "name_servers": w.name_servers,
            "status": w.status,
            "emails": w.emails,
            "org": w.org,
            "country": w.country,
        }
        return result
    except ImportError:
        pass
    except Exception as e:
        # Fallback to free API
        pass

    # Fallback to free whois API (who.is)
    try:
        # Use hackertarget API (free, 100/day)
        r = requests.get(f"https://api.hackertarget.com/whois/?q={domain}", timeout=10)
        if r.status_code == 200 and "error" not in r.text.lower()[:100]:
            return {"ok": True, "domain": domain, "raw_whois": r.text[:3000], "source": "hackertarget"}
        else:
            return {"ok": False, "error": f"WHOIS failed: {r.text[:200]}"}
    except Exception as e:
        return {"ok": False, "error": f"WHOIS error: {str(e)}"}

def ssl_check(domain: str) -> Dict[str, Any]:
    """SSL certificate info"""
    domain = domain.strip().lower()
    domain = re.sub(r'^https?://', '', domain)
    domain = domain.split('/')[0]
    domain = domain.split(':')[0]

    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                # Parse dates
                not_before = cert.get('notBefore')
                not_after = cert.get('notAfter')
                
                issuer = dict(x[0] for x in cert.get('issuer', ()))
                subject = dict(x[0] for x in cert.get('subject', ()))

                result = {
                    "ok": True,
                    "domain": domain,
                    "issuer": issuer.get('organizationName', str(issuer)),
                    "subject": subject.get('commonName', str(subject)),
                    "not_before": not_before,
                    "not_after": not_after,
                    "serial_number": cert.get('serialNumber'),
                    "version": cert.get('version'),
                    "is_expired": False,  # Could parse date
                    "san": [x[1] for x in cert.get('subjectAltName', [])] if cert.get('subjectAltName') else [],
                }
                return result
    except Exception as e:
        return {"ok": False, "error": f"SSL check error: {str(e)} - maybe no SSL or port 443 closed"}

def full_recon(target: str) -> Dict[str, Any]:
    """Full recon - auto detect IP or domain"""
    target = target.strip()
    # Check if IP
    is_ip = False
    try:
        socket.inet_aton(target)
        is_ip = True
    except:
        pass

    if is_ip:
        ip_info = ip_lookup(target)
        return {"type": "ip", "target": target, "ip_info": ip_info}
    else:
        # Domain
        domain = re.sub(r'^https?://', '', target).split('/')[0]
        dns_info = dns_lookup(domain)
        whois_info = whois_lookup(domain)
        ssl_info = ssl_check(domain)
        ip_info = None
        if dns_info.get("ip"):
            ip_info = ip_lookup(dns_info["ip"])

        return {
            "type": "domain",
            "target": domain,
            "dns": dns_info,
            "whois": whois_info,
            "ssl": ssl_info,
            "ip_info": ip_info,
        }
