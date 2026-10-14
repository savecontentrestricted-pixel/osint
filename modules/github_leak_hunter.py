"""
GitHub Leak Hunter - Pro OSINT Tool
Searches GitHub public repos for leaked secrets, keywords

Example: example.com -> finds repos where example.com leaked with API keys
"""

import requests
from .fast_cache import with_cache
import re
import time

def github_search_code(query, max_results=10):
    """
    Search GitHub code using public search API
    Note: Without auth, rate limited to 10 req/min
    With token, 30 req/min
    """
    result = {
        "ok": False,
        "query": query,
        "results": [],
        "total": 0,
        "error": None
    }
    
    try:
        # Use GitHub search API - public, no auth needed for basic
        # https://api.github.com/search/code?q=QUERY
        # Note: Code search requires auth in new GitHub API, so we use alternative: search repos + content via public
        # We'll use https://api.github.com/search/repositories and then check, plus use GitHub web search fallback
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Try code search (may need auth, but try without)
        # If fails, fallback to repo search with query in description/readme
        url = f"https://api.github.com/search/code?q={query}+in:file&per_page={max_results}"
        
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                items = data.get("items", [])
                results = []
                for item in items[:max_results]:
                    repo = item.get("repository", {})
                    results.append({
                        "name": item.get("name",""),
                        "path": item.get("path",""),
                        "repo": repo.get("full_name",""),
                        "repo_url": repo.get("html_url",""),
                        "file_url": item.get("html_url",""),
                        "score": item.get("score",0)
                    })
                result["results"] = results
                result["total"] = data.get("total_count",0)
                result["ok"] = True
                return result
            elif r.status_code == 403 or r.status_code == 422:
                # Code search needs auth or query too broad, fallback to repo search
                raise Exception("Code search needs auth, using fallback")
            else:
                result["error"] = f"GitHub API {r.status_code}: {r.text[:200]}"
        except Exception as e:
            # Fallback: Search repositories containing query
            fallback_url = f"https://api.github.com/search/repositories?q={query}&per_page={max_results}&sort=stars"
            try:
                r2 = requests.get(fallback_url, headers=headers, timeout=15)
                if r2.status_code == 200:
                    data2 = r2.json()
                    items2 = data2.get("items", [])
                    results = []
                    for repo in items2[:max_results]:
                        results.append({
                            "name": repo.get("name",""),
                            "path": "",
                            "repo": repo.get("full_name",""),
                            "repo_url": repo.get("html_url",""),
                            "file_url": repo.get("html_url",""),
                            "description": repo.get("description","")[:150],
                            "stars": repo.get("stargazers_count",0),
                            "score": repo.get("score",0)
                        })
                    result["results"] = results
                    result["total"] = data2.get("total_count",0)
                    result["ok"] = True
                    result["fallback"] = True
                    return result
                else:
                    result["error"] = f"Fallback also failed {r2.status_code}"
            except Exception as e2:
                result["error"] = str(e2)[:300]
        
        return result
        
    except Exception as e:
        result["error"] = str(e)[:300]
        return result

@with_cache("ghl", 1800, 21600)
def github_leak_hunter(query):
    """Main function"""
    # Clean query
    query = query.strip()
    if not query:
        return {"ok": False, "error": "Empty query"}
    
    # Search
    res = github_search_code(query, max_results=10)
    return res

def format_github_report(result):
    """Format as beautiful text"""
    if not result.get("ok"):
        return f"❌ Error: {result.get('error','Unknown')}\n\nTip: Try more specific query like 'example.com api_key' or use GitHub token for higher limits."
    
    query = result.get("query")
    results = result.get("results", [])
    total = result.get("total",0)
    is_fallback = result.get("fallback", False)
    
    txt = f"""
╔══════════════════════════════════════╗
║  🐙 <b>GITHUB LEAK HUNTER - PRO</b>     ║
╚══════════════════════════════════════╝

🔍 <b>Query:</b> <code>{query}</code>

📊 <b>Total Found:</b> {total} repos

"""
    if is_fallback:
        txt += "ℹ️ <i>Showing repo search (code search needs auth)</i>\n\n"
    
    txt += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if not results:
        txt += "✅ No public leaks found for this query (good!)\n\n"
    else:
        txt += f"📁 <b>Results ({len(results)}):</b>\n\n"
        for i, r in enumerate(results[:10], 1):
            txt += f"<b>{i}. {r.get('repo','')}</b>\n"
            if r.get('name'):
                txt += f"   📄 File: <code>{r.get('name')}</code>\n"
            if r.get('path'):
                txt += f"   📂 Path: <code>{r.get('path')}</code>\n"
            if r.get('description'):
                txt += f"   📝 {r.get('description')[:100]}\n"
            if r.get('stars') is not None:
                txt += f"   ⭐ Stars: {r.get('stars')}\n"
            txt += f"   🔗 <a href=\"{r.get('file_url','')}\">View</a>\n\n"
    
    txt += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    txt += f"⚠️ <b>Note:</b> Only public repos. Use for your own domain to check leaks.\n"
    txt += f"🔒 If you find your own secrets leaked, revoke them immediately!\n\n"
    txt += f"🔥 Powered by @Supermannn_x\n"
    
    return txt

if __name__ == "__main__":
    res = github_leak_hunter("example.com")
    print(format_github_report(res))
