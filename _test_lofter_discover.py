import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

# Fetch the discover page bundle.js
r = requests.get("https://lofter.lf127.net/nos-upload-cli/1695691864965/bundle.js", headers=headers, timeout=15)
print(f"Discover bundle: {r.status_code} len={len(r.text)}")

if r.status_code == 200:
    # Search for API endpoints
    api_paths = re.findall(r'["\'](/[a-zA-Z0-9/_.-]{3,80})["\']', r.text)
    interesting = [p for p in api_paths if any(k in p.lower() for k in ['search', 'post', 'tag', 'gate', 'api', 'explore', 'discover', 'front'])]
    print(f"Interesting paths: {list(set(interesting))[:50]}")
    
    # Base URL patterns
    base_patterns = re.findall(r'(?:baseURL|BASE_URL|apiUrl|API_URL|apiHost|host)["\']?\s*[:=]\s*["\']([^"\']+)["\']', r.text, re.IGNORECASE)
    print(f"Base URL patterns: {list(set(base_patterns))[:10]}")
    
    # Full lofter URLs
    lofter_urls = re.findall(r'["\'](https?://[a-z0-9._:/-]*lofter[a-z0-9._:/-]*)["\']', r.text, re.IGNORECASE)
    print(f"Lofter URLs: {list(set(lofter_urls))[:20]}")

# Also fetch the full discover page and find all script sources
r2 = requests.get("https://www.lofter.com/front/discover", headers=headers, timeout=15)
js_urls = re.findall(r'(?:src|href)="(https?://[^"]+\.js[^"]*)"', r2.text)
print(f"\nDiscover page JS: {js_urls}")

# Find all webpack chunks
chunk_urls = re.findall(r'["\']([^"\']*(?:chunk|webpack)[^"\']*\.js)["\']', r2.text)
print(f"Chunk files: {chunk_urls[:10]}")

