"""
Ultra-Fast Cache + Session for OSINT Hunter Hub
- Connection pooling
- In-memory TTL cache
- Performance metrics
"""
import time
import threading
import requests
from typing import Any, Dict, Optional

# Global session with connection pooling - reuse for speed
_session = None
_session_lock = threading.Lock()

def get_session() -> requests.Session:
    global _session
    if _session is None:
        with _session_lock:
            if _session is None:
                s = requests.Session()
                # Connection pooling: 20 connections, keep-alive
                adapter = requests.adapters.HTTPAdapter(
                    pool_connections=20,
                    pool_maxsize=20,
                    max_retries=2,
                    pool_block=False
                )
                s.mount('http://', adapter)
                s.mount('https://', adapter)
                s.headers.update({
                    'User-Agent': 'OSINT-Hunter-Hub/2.0 Fast',
                    'Accept': 'application/json',
                    'Connection': 'keep-alive'
                })
                _session = s
    return _session

# In-memory TTL cache
_cache: Dict[str, tuple] = {}  # key -> (value, expiry)
_cache_lock = threading.Lock()
_cache_hits = 0
_cache_miss = 0

def cache_get(key: str) -> Optional[Any]:
    global _cache_hits, _cache_miss
    with _cache_lock:
        if key in _cache:
            val, exp = _cache[key]
            if time.time() < exp:
                _cache_hits += 1
                return val
            else:
                del _cache[key]
        _cache_miss += 1
        return None

def cache_set(key: str, value: Any, ttl: int = 300):
    with _cache_lock:
        _cache[key] = (value, time.time() + ttl)
        # Cleanup old entries if too many
        if len(_cache) > 1000:
            now = time.time()
            expired = [k for k, (_, exp) in _cache.items() if exp < now]
            for k in expired[:100]:
                del _cache[k]

def cache_stats() -> Dict:
    with _cache_lock:
        total = _cache_hits + _cache_miss
        hit_rate = (_cache_hits / total * 100) if total > 0 else 0
        out = {
            "hits": _cache_hits,
            "miss": _cache_miss,
            "hit_rate": f"{hit_rate:.1f}%",
            "size": len(_cache)
        }
        try:
            from modules.database import cache_stats as _dcs
            out["persistent"] = _dcs()
        except Exception:
            out["persistent"] = {"total": 0, "live": 0, "hits": 0}
        return out

# Force join cache - 60 sec TTL per user (fast but secure)
_force_join_cache: Dict[int, tuple] = {}  # user_id -> (is_joined, expiry)
_force_join_lock = threading.Lock()

def force_join_cache_get(uid: int) -> Optional[bool]:
    with _force_join_lock:
        if uid in _force_join_cache:
            val, exp = _force_join_cache[uid]
            if time.time() < exp:
                return val
            else:
                del _force_join_cache[uid]
        return None

def force_join_cache_set(uid: int, is_joined: bool, ttl: int = 60):
    with _force_join_lock:
        _force_join_cache[uid] = (is_joined, time.time() + ttl)

def force_join_cache_clear(uid: int = None):
    with _force_join_lock:
        if uid is None:
            _force_join_cache.clear()
        else:
            _force_join_cache.pop(uid, None)

# API response cache - 5 min for same queries
def api_cache_key(tool: str, term: str) -> str:
    return f"{tool}:{term.lower().strip()}"

# v2.0 — persistent (DB) cache layer so restart/deploy ke baad bhi instant
_db_writes = 0

def _db_cache_get(dbkey: str):
    try:
        from modules.database import cache_get as _g
        return _g(dbkey)
    except Exception:
        return None

def api_cache_get(tool: str, term: str) -> Optional[Dict]:
    key = api_cache_key(tool, term)
    mem = cache_get(key)
    if mem is not None:
        return mem
    # DB (persistent) hit — 0 ms, koi network call nahi
    pc = _db_cache_get(f"osint:{key}")
    if isinstance(pc, dict) and pc:
        try:
            cache_set(key, pc, 300)
        except Exception:
            pass
        try:
            from modules.database import cache_hit_bump as _b
            _b(f"osint:{key}")
        except Exception:
            pass
        return pc
    return None

def api_cache_set(tool: str, term: str, data: Dict, ttl: int = 300):
    global _db_writes
    key = api_cache_key(tool, term)
    cache_set(key, data, ttl)
    try:
        from modules.database import cache_put as _p, cache_prune as _pr
        if isinstance(data, dict) and data.get("ok"):
            _p(f"osint:{key}", data, 2592000)          # success = 30 din
        elif isinstance(data, dict) and data.get("not_found"):
            _p(f"osint:{key}", data, 21600)            # no-record = 6 ghante
        _db_writes += 1
        if _db_writes % 50 == 0:
            _pr()
    except Exception:
        pass
