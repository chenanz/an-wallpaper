import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

# Visit a tag page and find all JS bundle URLs
r = requests.get("https://www.lofter.com/tag/原神同人?type=new", headers=headers, timeout=15)

# Get all JS sources
js_urls = re.findall(r'(?:src|href)="(https?://[^"]+\.js[^"]*)"', r.text)
print(f"JS URLs: {js_urls}")

# Also look for CSS to find versioned CDN prefixes
cdn_prefixes = set(re.findall(r'(https?://[a-z0-9._-]+\.lf127\.net|https?://[a-z0-9._-]+lofter[a-z0-9._-]*\.net)', r.text))
print(f"CDN prefixes: {cdn_prefixes}")

# The SPA probably loads more JS asynchronously
# Let's check if there's a webpack manifest or chunk manifest
manifest_patterns = re.findall(r'["\']((?:https?://[^"\']+)?/(?:webpack|static|assets|chunks)/[^"\']+\.js)["\']', r.text)
print(f"Manifest patterns: {manifest_patterns[:10]}")

# Let's try to find the app entry point
# Look for the main app JS that would contain API calls
# SPA frameworks often put API URLs in the JS bundles
dll_url = "https://lofter.lf127.net/webpack/lofter-dll/dll_c18ec65e7d3d3c60a4a8.js"
r2 = requests.get(dll_url, headers=headers, timeout=15)
print(f"\nDLL bundle: {r2.status_code} len={len(r2.text)}")

# Search for API endpoints in the DLL
api_paths = re.findall(r'["\'](/[a-zA-Z0-9/_.-]{3,60})["\']', r2.text)
interesting = [p for p in api_paths if any(k in p.lower() for k in ['api', 'search', 'post', 'tag', 'gate', 'front', 'blog', 'lofter'])]
print(f"Interesting paths in DLL: {list(set(interesting))[:30]}")

# Search for full lofter URLs
full_urls = re.findall(r'["\'](https?://[a-z0-9._/-]+lofter[a-z0-9._/-]*)["\']', r2.text, re.IGNORECASE)
print(f"Lofter URLs in DLL: {list(set(full_urls))[:20]}")

