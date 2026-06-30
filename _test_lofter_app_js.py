import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

# Fetch the main app JS bundle (this is where API routes would be)
app_js_url = "https://lofter.lf127.net/webpack/lofter-client-account/src/applications/login/pc.76448d5f325ccb3254db.js"
r = requests.get(app_js_url, headers=headers, timeout=15)
print(f"App JS: {r.status_code} len={len(r.text)}")

# Search for API endpoints
# Look for search/post related paths
search_patterns = re.findall(r'["\'](/[a-zA-Z0-9/_.-]{3,80})["\']', r.text)
interesting = [p for p in search_patterns if any(k in p.lower() for k in ['search', 'post', 'tag', 'gate', 'front', 'blog', 'api', 'explore'])]
print(f"Interesting paths: {list(set(interesting))[:50]}")

# Look for base URLs or API host configs
host_patterns = re.findall(r'["\'](https?://[a-z0-9._:-]+lofter[a-z0-9._:/-]*)["\']', r.text, re.IGNORECASE)
print(f"Host URLs: {list(set(host_patterns))[:20]}")

# Look for axios/fetch baseURL patterns
base_patterns = re.findall(r'(?:baseURL|BASE_URL|apiUrl|API_URL|apiHost|host)["\']?\s*[:=]\s*["\']([^"\']+)["\']', r.text, re.IGNORECASE)
print(f"Base URL patterns: {list(set(base_patterns))[:10]}")

# Look for gateway/API patterns specific to 网易/LF127
gw_patterns = re.findall(r'["\']((?:/front/|/gateway/|/newapi/)[a-zA-Z0-9/_.-]+)["\']', r.text)
print(f"Gateway paths: {list(set(gw_patterns))[:20]}")

# Also look for "searchPost" or "tagPosts" directly as function names
func_patterns = re.findall(r'["\']([a-zA-Z]*(?:search|tag|post)[a-zA-Z]*\.[a-zA-Z]+)["\']', r.text, re.IGNORECASE)
print(f"API function patterns: {list(set(func_patterns))[:30]}")

# Try finding webpack chunk files
chunk_patterns = re.findall(r'["\']([a-f0-9]+)["\']', r.text)
print(f"\nTotal hash patterns: {len(chunk_patterns)}")

# Look for webpack chunk loading patterns
chunk_urls = re.findall(r'["\']([^"\']*(?:chunk|src|app)[^"\']*\.js)["\']', r.text)
print(f"Chunk JS files: {list(set(chunk_urls))[:20]}")

# Search for the specific string "search" more broadly
search_strs = []
for m in re.finditer(r'["\']([^"\']{4,60}search[^"\']{0,60})["\']', r.text, re.IGNORECASE):
    search_strs.append(m.group(1))
print(f"\nStrings containing 'search': {list(set(search_strs))[:30]}")

